from dataclasses import dataclass

from .chunking import Chunk
from .retrieval import retrieve_top_k, tokenize


REFUSAL_MESSAGE = "I do not have enough grounded evidence in the provided corpus to answer that question."

_QUESTION_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "did",
        "do",
        "does",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }
)
_MIN_MEANINGFUL_MATCHES = 2
_MIN_MEANINGFUL_COVERAGE = 0.5


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[str]
    refused: bool


def _meaningful_terms(text: str) -> set[str]:
    return set(tokenize(text)) - _QUESTION_STOPWORDS


def _has_sufficient_evidence(question_terms: set[str], chunk: Chunk) -> bool:
    if not question_terms:
        return False

    matched_terms = question_terms & set(tokenize(chunk.text))
    coverage = len(matched_terms) / len(question_terms)
    return (
        len(matched_terms) >= _MIN_MEANINGFUL_MATCHES
        and coverage >= _MIN_MEANINGFUL_COVERAGE
    )


def _source_index(chunks: list[Chunk], target: Chunk) -> int | None:
    for index, chunk in enumerate(chunks):
        if chunk is target:
            return index
    return None


def _ends_sentence(text: str) -> bool:
    return text.rstrip().endswith((".", "?", "!"))


def _longest_word_overlap(left: str, right: str) -> int:
    left_words = left.split()
    right_words = right.split()
    for size in range(min(len(left_words), len(right_words)), 0, -1):
        if left_words[-size:] == right_words[:size]:
            return size
    return 0


def _complete_excerpt(
    seed: Chunk,
    chunks: list[Chunk],
) -> tuple[str, list[str], set[int]]:
    source_index = _source_index(chunks, seed)
    excerpt = seed.text
    source_ids = [seed.chunk_id]
    consumed_indices = {source_index} if source_index is not None else set()

    if source_index is None:
        return excerpt, source_ids, consumed_indices

    current_index = source_index
    while not _ends_sentence(excerpt):
        next_index = current_index + 1
        if next_index >= len(chunks):
            break

        current = chunks[current_index]
        candidate = chunks[next_index]
        if candidate.doc_id != current.doc_id:
            break

        overlap = _longest_word_overlap(current.text, candidate.text)
        candidate_words = candidate.text.split()
        if overlap == 0 or overlap == len(candidate_words):
            break

        excerpt += " " + " ".join(candidate_words[overlap:])
        if candidate.chunk_id not in source_ids:
            source_ids.append(candidate.chunk_id)
        consumed_indices.add(next_index)
        current_index = next_index

    return excerpt, source_ids, consumed_indices


def build_grounded_answer(question: str, chunks: list[Chunk], top_k: int = 2) -> RagAnswer:
    results = retrieve_top_k(question, chunks, k=top_k)
    question_terms = _meaningful_terms(question)
    supporting_points: list[str] = []
    citations: list[str] = []
    cited_ids: set[str] = set()
    consumed_indices: set[int] = set()

    for item in results:
        chunk = item.chunk
        source_index = _source_index(chunks, chunk)
        if (
            chunk.chunk_id in cited_ids
            or source_index in consumed_indices
            or not _has_sufficient_evidence(question_terms, chunk)
        ):
            continue

        excerpt, source_ids, used_indices = _complete_excerpt(chunk, chunks)
        consumed_indices.update(used_indices)
        new_source_ids = [source_id for source_id in source_ids if source_id not in cited_ids]
        cited_ids.update(new_source_ids)
        citations.extend(new_source_ids)
        inline_citations = " ".join(f"[{source_id}]" for source_id in new_source_ids)
        supporting_points.append(f"- {excerpt} {inline_citations}")

    if not supporting_points:
        return RagAnswer(answer=REFUSAL_MESSAGE, citations=[], refused=True)

    answer = "Grounded answer:\n" + "\n".join(supporting_points)
    return RagAnswer(answer=answer, citations=citations, refused=False)
