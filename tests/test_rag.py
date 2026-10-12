from dataclasses import fields
from inspect import signature
import sys

import pytest

from src.chunking import Chunk
from src.chunking import build_chunks
from src.cli import main
from src.corpus import load_default_corpus
from src.rag import REFUSAL_MESSAGE, RagAnswer, build_grounded_answer
from src.retrieval import retrieve_top_k


SUPPORTED_QUESTION = "What is retrieval augmented generation?"
UNSUPPORTED_QUESTION = "Who won the world cup in 1958?"


def make_chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id="doc", title="Title", text=text)


def run_cli(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], *args: str) -> str:
    monkeypatch.setattr(sys, "argv", ["src.cli", *args])
    main()
    return capsys.readouterr().out


def test_cli_supported_question_has_separate_sections_and_valid_citation(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output = run_cli(monkeypatch, capsys, "--question", SUPPORTED_QUESTION)

    assert output == (
        "Question:\n"
        f"{SUPPORTED_QUESTION}\n\n"
        "Answer:\n"
        "Grounded answer:\n"
        "- Retrieval augmented generation combines retrieval with text generation. "
        "The model should answer using retrieved evidence rather than [doc-1-chunk-0]\n\n"
        "Corpus profile: default\n\n"
        "Refused: False\n"
        "Citations: doc-1-chunk-0\n"
    )


def test_cli_unsupported_question_has_exact_safe_refusal(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output = run_cli(monkeypatch, capsys, "--question", UNSUPPORTED_QUESTION)

    assert output == (
        "Question:\n"
        f"{UNSUPPORTED_QUESTION}\n\n"
        "Answer:\n"
        f"{REFUSAL_MESSAGE}\n\n"
        "Corpus profile: default\n\n"
        "Refused: True\n"
        "Citations: None\n"
    )


def test_cli_existing_explicit_arguments_remain_compatible(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output = run_cli(
        monkeypatch,
        capsys,
        "--question",
        SUPPORTED_QUESTION,
        "--chunk-size",
        "140",
        "--overlap",
        "30",
        "--top-k",
        "2",
        "--corpus-profile",
        "default",
    )

    assert "Refused: False" in output
    assert "Citations: doc-1-chunk-0" in output


@pytest.mark.parametrize("question", [SUPPORTED_QUESTION, UNSUPPORTED_QUESTION])
def test_cli_output_is_deterministic_for_repeated_inputs(
    question: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    first = run_cli(monkeypatch, capsys, "--question", question)
    second = run_cli(monkeypatch, capsys, "--question", question)

    assert first == second


def test_build_grounded_answer_returns_citations_for_supported_query() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)
    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)
    supporting_chunk = next(chunk for chunk in chunks if chunk.chunk_id == "doc-1-chunk-0")

    assert result.refused is False
    assert result.answer == f"Grounded answer:\n- {supporting_chunk.text} [doc-1-chunk-0]"
    assert result.citations == ["doc-1-chunk-0"]


def test_citations_correspond_exactly_to_qualifying_retrieved_chunks() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)
    retrieved = retrieve_top_k(SUPPORTED_QUESTION, chunks, k=2)
    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)

    retrieved_ids = {item.chunk.chunk_id for item in retrieved}

    assert [item.chunk.chunk_id for item in retrieved] == [
        "doc-1-chunk-0",
        "doc-2-chunk-0",
    ]
    assert set(result.citations) <= retrieved_ids
    assert result.citations == ["doc-1-chunk-0"]
    assert all(f"[{chunk_id}]" in result.answer for chunk_id in result.citations)


def test_non_qualifying_retrieved_chunk_is_excluded_from_answer_and_citations() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)
    weak_chunk = next(chunk for chunk in chunks if chunk.chunk_id == "doc-2-chunk-0")

    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)

    assert weak_chunk.text not in result.answer
    assert weak_chunk.chunk_id not in result.citations


def test_duplicate_qualifying_chunk_ids_are_emitted_once() -> None:
    duplicate = make_chunk("duplicate", "alpha beta")

    result = build_grounded_answer("alpha beta", [duplicate, duplicate], top_k=2)

    assert result.answer == "Grounded answer:\n- alpha beta [duplicate]"
    assert result.citations == ["duplicate"]


def test_grounded_answer_is_deterministic_for_identical_inputs() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)

    first = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)
    second = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)

    assert first == second


def test_top_k_one_keeps_existing_call_shape_and_returns_one_valid_citation() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)

    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=1)

    assert result.refused is False
    assert result.citations == ["doc-1-chunk-0"]


def test_public_rag_interfaces_remain_compatible() -> None:
    assert [field.name for field in fields(RagAnswer)] == ["answer", "citations", "refused"]
    assert list(signature(build_grounded_answer).parameters) == ["question", "chunks", "top_k"]
    assert signature(build_grounded_answer).parameters["top_k"].default == 2


def test_build_grounded_answer_refuses_unsupported_query() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=120, overlap=20)
    result = build_grounded_answer("Who was emperor of Mars?", chunks, top_k=2)
    assert result.refused is True
    assert result.citations == []


@pytest.mark.parametrize("question", ["", " \t\r\n "])
def test_empty_or_whitespace_only_question_returns_exact_refusal(question: str) -> None:
    result = build_grounded_answer(question, [make_chunk("evidence", "alpha beta")])

    assert result == RagAnswer(REFUSAL_MESSAGE, [], True)


def test_empty_chunk_collection_returns_exact_refusal() -> None:
    result = build_grounded_answer("alpha beta", [])

    assert result == RagAnswer(REFUSAL_MESSAGE, [], True)


def test_no_retrieved_results_returns_exact_refusal() -> None:
    chunks = [make_chunk("unrelated", "gamma delta")]

    assert retrieve_top_k("alpha beta", chunks, k=2) == []
    assert build_grounded_answer("alpha beta", chunks) == RagAnswer(
        REFUSAL_MESSAGE, [], True
    )


def test_question_containing_only_stopwords_is_refused_despite_positive_score() -> None:
    chunks = [make_chunk("stopwords", "the system is in the corpus")]

    assert retrieve_top_k("what is in the system", chunks, k=2)[0].score > 0
    assert build_grounded_answer("what is in the system", chunks) == RagAnswer(
        REFUSAL_MESSAGE, [], True
    )


def test_irrelevant_common_word_overlap_does_not_qualify_as_evidence() -> None:
    question = "Who won the world cup in 1958?"
    chunks = [make_chunk("common-words", "Who is in the local archive?")]

    assert retrieve_top_k(question, chunks, k=2)[0].score > 0
    assert build_grounded_answer(question, chunks) == RagAnswer(
        REFUSAL_MESSAGE, [], True
    )


def test_only_one_distinct_meaningful_match_is_refused() -> None:
    chunks = [make_chunk("one-match", "alpha alpha unrelated")]

    assert build_grounded_answer("alpha beta", chunks) == RagAnswer(
        REFUSAL_MESSAGE, [], True
    )


def test_two_meaningful_matches_below_half_query_coverage_are_refused() -> None:
    chunks = [make_chunk("below-boundary", "alpha beta unrelated")]

    assert build_grounded_answer("alpha beta gamma delta epsilon", chunks) == RagAnswer(
        REFUSAL_MESSAGE, [], True
    )


def test_two_meaningful_matches_at_half_query_coverage_are_supported() -> None:
    chunk = make_chunk("at-boundary", "alpha beta supporting text")

    result = build_grounded_answer("alpha beta gamma delta", [chunk])

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta supporting text [at-boundary]",
        ["at-boundary"],
        False,
    )


def test_duplicate_query_terms_count_once_for_matches_and_coverage() -> None:
    chunk = make_chunk("distinct-terms", "alpha beta supporting text")

    result = build_grounded_answer("alpha alpha beta beta gamma delta", [chunk])

    assert result.refused is False
    assert result.citations == ["distinct-terms"]


def test_refusal_contains_no_retrieved_excerpt_or_citation() -> None:
    marker = "UNSUPPORTED_EXCERPT_MARKER"
    chunks = [make_chunk("weak-evidence", f"alpha {marker}")]

    result = build_grounded_answer("alpha beta", chunks)

    assert result.answer == REFUSAL_MESSAGE
    assert marker not in result.answer
    assert "weak-evidence" not in result.answer
    assert result.citations == []
    assert result.refused is True


@pytest.mark.parametrize(
    ("top_k", "error_type", "message"),
    [
        (True, TypeError, "k must be a positive integer"),
        (1.5, TypeError, "k must be a positive integer"),
        (0, ValueError, "k must be > 0"),
        (-1, ValueError, "k must be > 0"),
    ],
)
def test_invalid_top_k_preserves_retrieval_validation_errors(
    top_k: object, error_type: type[Exception], message: str
) -> None:
    with pytest.raises(error_type, match=message):
        build_grounded_answer("", [], top_k=top_k)  # type: ignore[arg-type]


def test_supported_question_remains_grounded_after_refusal_checks() -> None:
    chunk = make_chunk("supported", "retrieval augmented generation uses corpus evidence")

    result = build_grounded_answer(SUPPORTED_QUESTION, [chunk])

    assert result == RagAnswer(
        "Grounded answer:\n- retrieval augmented generation uses corpus evidence [supported]",
        ["supported"],
        False,
    )
