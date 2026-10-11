import pytest

from src.chunking import build_chunks, split_text_with_overlap
from src.corpus import Document


def reconstruct_source_words(chunks: list[str], source_words: list[str]) -> list[str]:
    """Remove each chunk's intentional word overlap against known source order."""
    reconstructed: list[str] = []
    source_index = 0

    for chunk in chunks:
        chunk_words = chunk.split()
        for overlap_size in range(min(len(chunk_words) - 1, source_index), -1, -1):
            new_words = chunk_words[overlap_size:]
            if (
                source_words[source_index - overlap_size : source_index] == chunk_words[:overlap_size]
                and source_words[source_index : source_index + len(new_words)] == new_words
            ):
                reconstructed.extend(new_words)
                source_index += len(new_words)
                break
        else:
            pytest.fail(f"Chunk cannot be aligned to the source sequence: {chunk!r}")

    return reconstructed


@pytest.mark.parametrize("text", ["", " \t\n "])
def test_split_text_with_overlap_returns_no_chunks_for_empty_input(text: str) -> None:
    assert split_text_with_overlap(text) == []


def test_split_text_with_overlap_normalizes_whitespace() -> None:
    assert split_text_with_overlap("  alpha\t beta\n gamma  ", chunk_size=30, overlap=5) == [
        "alpha beta gamma"
    ]


def test_split_text_with_overlap_returns_short_and_exact_size_text_unchanged() -> None:
    assert split_text_with_overlap("alpha beta", chunk_size=20, overlap=5) == ["alpha beta"]
    assert split_text_with_overlap("abcd efgh", chunk_size=9, overlap=2) == ["abcd efgh"]


def test_split_text_with_overlap_keeps_ordinary_words_intact_at_boundaries() -> None:
    chunks = split_text_with_overlap("alpha beta gamma delta", chunk_size=16, overlap=5)

    assert chunks == ["alpha beta gamma", "gamma delta"]
    assert all(word in {"alpha", "beta", "gamma", "delta"} for chunk in chunks for word in chunk.split())
    assert all(len(chunk) <= 16 for chunk in chunks)


def test_split_text_with_overlap_reuses_complete_trailing_words_for_overlap() -> None:
    chunks = split_text_with_overlap("one two three four five", chunk_size=15, overlap=5)

    assert chunks == ["one two three", "three four five"]
    assert chunks[0].split()[-1] == chunks[1].split()[0] == "three"
    assert len("three") == 5


def test_split_text_with_overlap_uses_zero_overlap() -> None:
    assert split_text_with_overlap("alpha beta gamma", chunk_size=10, overlap=0) == [
        "alpha beta",
        "gamma",
    ]


def test_split_text_with_overlap_selects_smaller_overlap_that_fits_new_content() -> None:
    chunks = split_text_with_overlap("aa bbb cccc dddddd", chunk_size=14, overlap=10)

    assert chunks == ["aa bbb cccc", "cccc dddddd"]
    assert len("bbb cccc") <= 10
    assert len("bbb cccc dddddd") > 14
    assert len("cccc dddddd") <= 14


def test_split_text_with_overlap_splits_long_words_with_character_overlap() -> None:
    word = "supercalifragilisticexpialidocious"
    chunks = split_text_with_overlap(word, chunk_size=10, overlap=3)

    assert chunks == ["supercalif", "lifragilis", "listicexpi", "xpialidoci", "ocious"]
    assert all(len(chunk) <= 10 for chunk in chunks)
    assert chunks[0] + "".join(chunk[3:] for chunk in chunks[1:]) == word


def test_split_text_with_overlap_handles_single_character_chunk_sizes() -> None:
    assert split_text_with_overlap("a b c d", chunk_size=1, overlap=0) == ["a", "b", "c", "d"]


def test_split_text_with_overlap_preserves_source_words_in_order() -> None:
    text = "alpha beta gamma delta epsilon zeta eta theta"
    chunks = split_text_with_overlap(text, chunk_size=18, overlap=5)

    assert reconstruct_source_words(chunks, text.split()) == text.split()


def test_split_text_with_overlap_handles_repeated_words_deterministically() -> None:
    text = "red blue red blue red blue"
    chunks = split_text_with_overlap(text, chunk_size=12, overlap=5)

    assert chunks == [
        "red blue red",
        "red blue red",
        "red blue",
    ]
    assert reconstruct_source_words(chunks, text.split()) == text.split()


def test_split_text_with_overlap_makes_forward_progress_for_small_windows() -> None:
    chunks = split_text_with_overlap("x" * 50, chunk_size=2, overlap=1)

    assert len(chunks) == 49
    assert all(len(chunk) <= 2 for chunk in chunks)
    assert chunks[-1] == "xx"


def test_split_text_with_overlap_does_not_append_a_duplicate_terminal_chunk() -> None:
    chunks = split_text_with_overlap("alpha beta gamma delta epsilon", chunk_size=16, overlap=5)

    assert chunks == ["alpha beta gamma", "gamma delta", "delta epsilon"]
    assert chunks.count(chunks[-1]) == 1


@pytest.mark.parametrize("chunk_size", [0, -1])
def test_split_text_with_overlap_rejects_non_positive_chunk_size(chunk_size: int) -> None:
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        split_text_with_overlap("abc", chunk_size=chunk_size)


@pytest.mark.parametrize("overlap", [-1, 10, 11])
def test_split_text_with_overlap_rejects_invalid_overlap_values(overlap: int) -> None:
    with pytest.raises(ValueError):
        split_text_with_overlap("abc", chunk_size=10, overlap=overlap)


def test_build_chunks_preserves_document_metadata_and_order() -> None:
    documents = [
        Document(doc_id="doc-a", title="First", text="alpha beta gamma delta"),
        Document(doc_id="doc-b", title="Second", text="epsilon zeta eta theta"),
    ]

    chunks = build_chunks(documents, chunk_size=12, overlap=3)

    assert [(chunk.doc_id, chunk.title) for chunk in chunks] == [
        ("doc-a", "First"),
        ("doc-a", "First"),
        ("doc-b", "Second"),
        ("doc-b", "Second"),
    ]
    assert [chunk.chunk_id for chunk in chunks] == [
        "doc-a-chunk-0",
        "doc-a-chunk-1",
        "doc-b-chunk-0",
        "doc-b-chunk-1",
    ]


def test_build_chunks_generates_stable_unique_chunk_ids() -> None:
    documents = [Document(doc_id="doc-a", title="First", text="alpha beta gamma delta")]

    first = build_chunks(documents, chunk_size=12, overlap=3)
    second = build_chunks(documents, chunk_size=12, overlap=3)

    assert first == second
    assert len({chunk.chunk_id for chunk in first}) == len(first)
