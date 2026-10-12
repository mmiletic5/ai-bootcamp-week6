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


def build_grounded_answer(question: str, chunks: list[Chunk], top_k: int = 2) -> RagAnswer:
    results = retrieve_top_k(question, chunks, k=top_k)
    question_terms = _meaningful_terms(question)
    supporting_points: list[str] = []
    citations: list[str] = []
    cited_ids: set[str] = set()

    for item in results:
        chunk = item.chunk
        if chunk.chunk_id in cited_ids or not _has_sufficient_evidence(question_terms, chunk):
            continue
        cited_ids.add(chunk.chunk_id)
        citations.append(chunk.chunk_id)
        supporting_points.append(f"- {chunk.text} [{chunk.chunk_id}]")

    if not supporting_points:
        return RagAnswer(answer=REFUSAL_MESSAGE, citations=[], refused=True)

    answer = "Grounded answer:\n" + "\n".join(supporting_points)
    return RagAnswer(answer=answer, citations=citations, refused=False)
