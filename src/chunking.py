from dataclasses import dataclass

from .corpus import Document


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str


def split_text_with_overlap(text: str, chunk_size: int = 140, overlap: int = 30) -> list[str]:
    """Split normalized text into word-aware, character-bounded chunks.

    The ``overlap`` is a character target: the next chunk reuses the largest
    suffix of complete trailing words whose joined length fits that target and
    can coexist with the next new word. Exact overlap is not always possible
    without splitting a word, so the effective overlap can be smaller
    (including zero). This guarantees forward progress and avoids duplicate
    overlap-only chunks. Words longer than ``chunk_size`` are the deliberate
    exception and are split into character windows using the requested overlap.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    words = cleaned.split(" ")
    chunks: list[str] = []
    start = 0

    while start < len(words):
        if len(words[start]) > chunk_size:
            word = words[start]
            step = chunk_size - overlap
            word_start = 0
            while word_start < len(word):
                word_end = min(word_start + chunk_size, len(word))
                chunks.append(word[word_start:word_end])
                if word_end == len(word):
                    break
                word_start += step
            start += 1
            continue

        end = start
        chunk_length = 0
        while end < len(words) and len(words[end]) <= chunk_size:
            separator_length = 1 if end > start else 0
            candidate_length = chunk_length + separator_length + len(words[end])
            if candidate_length > chunk_size:
                break
            chunk_length = candidate_length
            end += 1

        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break

        if len(words[end]) > chunk_size:
            start = end
            continue

        overlap_start = end
        overlap_length = 0
        for index in range(end - 1, start - 1, -1):
            candidate_length = len(words[index])
            if overlap_length:
                candidate_length += 1 + overlap_length
            if candidate_length > overlap:
                break
            overlap_length = candidate_length
            if index > start and overlap_length + 1 + len(words[end]) <= chunk_size:
                overlap_start = index

        start = overlap_start

    return chunks


def build_chunks(documents: list[Document], chunk_size: int = 140, overlap: int = 30) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in documents:
        parts = split_text_with_overlap(doc.text, chunk_size=chunk_size, overlap=overlap)
        for i, part in enumerate(parts):
            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}-chunk-{i}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    text=part,
                )
            )
    return chunks
