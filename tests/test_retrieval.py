import pytest

from src.chunking import Chunk
from src.retrieval import lexical_score, retrieve_top_k, tokenize


def make_chunk(chunk_id: str, text: str, doc_id: str = "doc", title: str = "Title") -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id=doc_id, title=title, text=text)


@pytest.fixture
def ranked_chunks() -> list[Chunk]:
    return [
        make_chunk("chunk-c", "rag retrieval citation evidence extra"),
        make_chunk("chunk-a", "rag citation"),
        make_chunk("chunk-b", "rag citation filler"),
        make_chunk("chunk-z", "weather forecast rain"),
    ]


def test_tokenize_matches_case_insensitively() -> None:
    assert tokenize("RAG, Citation-42!") == ["rag", "citation", "42"]


def test_lexical_score_uses_matching_chunk_token_occurrences() -> None:
    assert lexical_score("rag citation", "rag citation filler filler") == pytest.approx(0.5)


def test_lexical_score_counts_repeated_matching_chunk_words() -> None:
    assert lexical_score("rag rag", "rag filler rag") == pytest.approx(2 / 3)


def test_retrieve_top_k_returns_descending_scores_and_preserves_metadata(
    ranked_chunks: list[Chunk],
) -> None:
    results = retrieve_top_k("rag citation", ranked_chunks, k=3)

    assert [result.chunk.chunk_id for result in results] == ["chunk-a", "chunk-b", "chunk-c"]
    assert [result.score for result in results] == [1.0, pytest.approx(2 / 3), pytest.approx(2 / 5)]
    assert results[0].chunk.doc_id == "doc"
    assert results[0].chunk.title == "Title"
    assert results[0].chunk.text == "rag citation"


def test_retrieve_top_k_returns_exactly_top_two_of_three_eligible_chunks(
    ranked_chunks: list[Chunk],
) -> None:
    results = retrieve_top_k("rag citation", ranked_chunks, k=2)

    assert [result.chunk.chunk_id for result in results] == ["chunk-a", "chunk-b"]
    assert len(results) == 2


def test_retrieve_top_k_returns_exactly_top_three_of_three_eligible_chunks(
    ranked_chunks: list[Chunk],
) -> None:
    results = retrieve_top_k("rag citation", ranked_chunks, k=3)

    assert [result.chunk.chunk_id for result in results] == ["chunk-a", "chunk-b", "chunk-c"]
    assert len(results) == 3


def test_retrieve_top_k_returns_fewer_results_than_k_when_fewer_qualify() -> None:
    chunks = [make_chunk("match", "rag evidence"), make_chunk("miss", "weather forecast")]

    results = retrieve_top_k("rag", chunks, k=3)

    assert [result.chunk.chunk_id for result in results] == ["match"]


def test_retrieve_top_k_allows_k_larger_than_eligible_corpus() -> None:
    chunks = [make_chunk("a", "rag"), make_chunk("b", "rag evidence")]

    results = retrieve_top_k("rag", chunks, k=10)

    assert [result.chunk.chunk_id for result in results] == ["a", "b"]


def test_retrieve_top_k_returns_empty_for_unrelated_or_empty_query() -> None:
    chunks = [make_chunk("a", "vector database retrieval")]

    assert retrieve_top_k("basketball playoffs", chunks, k=2) == []
    assert retrieve_top_k("", chunks, k=2) == []


def test_retrieve_top_k_returns_empty_for_an_empty_chunk_collection() -> None:
    assert retrieve_top_k("rag", [], k=2) == []


@pytest.mark.parametrize("k", [0, -1])
def test_retrieve_top_k_rejects_non_positive_k(k: int) -> None:
    with pytest.raises(ValueError, match="k must be > 0"):
        retrieve_top_k("rag", [], k=k)


@pytest.mark.parametrize("k", [True, False, 1.0, "1", None])
def test_retrieve_top_k_rejects_invalid_k_types(k: object) -> None:
    with pytest.raises(TypeError, match="k must be a positive integer"):
        retrieve_top_k("rag", [], k=k)  # type: ignore[arg-type]


@pytest.mark.parametrize("min_score", [-0.01, float("nan"), float("inf"), float("-inf")])
def test_retrieve_top_k_rejects_negative_or_non_finite_min_score(min_score: float) -> None:
    with pytest.raises(ValueError):
        retrieve_top_k("rag", [], min_score=min_score)


@pytest.mark.parametrize("min_score", [True, False, "0.1", None])
def test_retrieve_top_k_rejects_invalid_min_score_types(min_score: object) -> None:
    with pytest.raises(TypeError, match="min_score must be a finite non-negative number"):
        retrieve_top_k("rag", [], min_score=min_score)  # type: ignore[arg-type]


def test_retrieve_top_k_zero_min_score_still_excludes_zero_score_chunks() -> None:
    chunks = [make_chunk("match", "rag evidence"), make_chunk("miss", "weather forecast")]

    results = retrieve_top_k("rag", chunks, min_score=0)

    assert [result.chunk.chunk_id for result in results] == ["match"]


def test_retrieve_top_k_uses_an_inclusive_min_score_threshold() -> None:
    chunks = [make_chunk("boundary", "rag filler")]

    assert retrieve_top_k("rag", chunks, min_score=0.5)[0].chunk.chunk_id == "boundary"
    assert retrieve_top_k("rag", chunks, min_score=0.500001) == []


def test_retrieve_top_k_breaks_ties_by_chunk_id_regardless_of_input_order() -> None:
    chunks = [
        make_chunk("z-id", "rag evidence"),
        make_chunk("a-id", "rag evidence"),
        make_chunk("m-id", "rag evidence"),
    ]

    first = retrieve_top_k("rag", chunks, k=3)
    second = retrieve_top_k("rag", list(reversed(chunks)), k=3)

    assert [result.chunk.chunk_id for result in first] == ["a-id", "m-id", "z-id"]
    assert [result.chunk.chunk_id for result in second] == ["a-id", "m-id", "z-id"]


def test_retrieve_top_k_does_not_mutate_input_chunks() -> None:
    chunks = [
        make_chunk("b", "rag evidence", doc_id="doc-b", title="B"),
        make_chunk("a", "rag citation", doc_id="doc-a", title="A"),
    ]
    original = list(chunks)

    retrieve_top_k("rag", chunks, k=2)

    assert chunks == original
    assert [chunk.chunk_id for chunk in chunks] == ["b", "a"]


def test_retrieve_top_k_case_insensitive_matching() -> None:
    results = retrieve_top_k("RAG", [make_chunk("a", "rag Evidence")])

    assert results[0].score == pytest.approx(0.5)
