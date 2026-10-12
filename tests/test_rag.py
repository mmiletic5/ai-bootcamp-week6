from dataclasses import fields
from inspect import signature
import sys

import pytest

from src.chunking import Chunk
from src.chunking import build_chunks
from src.cli import main
from src.corpus import load_default_corpus
from src.corpus import load_training_rag_corpus
from src.rag import REFUSAL_MESSAGE, RagAnswer, build_grounded_answer
from src.retrieval import retrieve_top_k


SUPPORTED_QUESTION = "What is retrieval augmented generation?"
UNSUPPORTED_QUESTION = "Who won the world cup in 1958?"
DEFAULT_COMPLETE_TEXT = (
    "Retrieval augmented generation combines retrieval with text generation. "
    "The model should answer using retrieved evidence rather than unsupported assumptions."
)


def make_chunk(chunk_id: str, text: str, doc_id: str = "doc") -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id=doc_id, title="Title", text=text)


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
        f"- {DEFAULT_COMPLETE_TEXT} [doc-1-chunk-0] [doc-1-chunk-1]\n\n"
        "Corpus profile: default\n\n"
        "Refused: False\n"
        "Citations: doc-1-chunk-0, doc-1-chunk-1\n"
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
    assert "Answer:\nGrounded answer:\n- " in output
    assert "Citations: doc-1-chunk-0, doc-1-chunk-1" in output


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

    assert result.refused is False
    assert result.answer == (
        f"Grounded answer:\n- {DEFAULT_COMPLETE_TEXT} "
        "[doc-1-chunk-0] [doc-1-chunk-1]"
    )
    assert result.citations == ["doc-1-chunk-0", "doc-1-chunk-1"]


def test_citations_distinguish_qualifying_seed_from_verified_continuation() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)
    retrieved = retrieve_top_k(SUPPORTED_QUESTION, chunks, k=2)
    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)

    assert [item.chunk.chunk_id for item in retrieved] == [
        "doc-1-chunk-0",
        "doc-2-chunk-0",
    ]
    assert result.citations == ["doc-1-chunk-0", "doc-1-chunk-1"]
    assert all(f"[{chunk_id}]" in result.answer for chunk_id in result.citations)
    assert "[doc-2-chunk-0]" not in result.answer


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


def test_top_k_one_keeps_existing_call_shape_and_allows_verified_continuation() -> None:
    chunks = build_chunks(load_default_corpus(), chunk_size=140, overlap=30)

    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=1)

    assert result.refused is False
    assert result.citations == ["doc-1-chunk-0", "doc-1-chunk-1"]


def test_one_hop_continuation_removes_exact_overlap_and_cites_both_chunks() -> None:
    chunks = [
        make_chunk("doc-chunk-0", "alpha beta supporting bridge words"),
        make_chunk("doc-chunk-1", "bridge words finish the answer."),
    ]

    result = build_grounded_answer("alpha beta", chunks, top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n"
        "- alpha beta supporting bridge words finish the answer. "
        "[doc-chunk-0] [doc-chunk-1]",
        ["doc-chunk-0", "doc-chunk-1"],
        False,
    )
    assert "bridge words bridge words" not in result.answer


def test_longest_repeated_word_overlap_is_used_once() -> None:
    chunks = [
        make_chunk("doc-chunk-0", "alpha beta echo echo bridge"),
        make_chunk("doc-chunk-1", "echo echo bridge finish."),
    ]

    result = build_grounded_answer("alpha beta", chunks, top_k=1)

    assert result.answer == (
        "Grounded answer:\n"
        "- alpha beta echo echo bridge finish. [doc-chunk-0] [doc-chunk-1]"
    )
    assert result.citations == ["doc-chunk-0", "doc-chunk-1"]
    assert "echo echo bridge echo echo bridge" not in result.answer


def test_source_adjacency_is_independent_of_retrieval_ranking() -> None:
    seed = make_chunk("a-seed", "alpha beta bridge")
    continuation = make_chunk("z-continuation", "bridge completed answer.")
    ranked_but_unrelated = make_chunk("b-ranked", "alpha beta unrelated details.", "other-doc")
    chunks = [seed, continuation, ranked_but_unrelated]

    retrieved = retrieve_top_k("alpha beta", chunks, k=2)
    result = build_grounded_answer("alpha beta", chunks, top_k=2)

    assert [item.chunk.chunk_id for item in retrieved] == ["a-seed", "b-ranked"]
    assert result == RagAnswer(
        "Grounded answer:\n"
        "- alpha beta bridge completed answer. [a-seed] [z-continuation]\n"
        "- alpha beta unrelated details. [b-ranked]",
        ["a-seed", "z-continuation", "b-ranked"],
        False,
    )


def test_zero_overlap_same_document_neighbor_is_not_appended() -> None:
    seed = make_chunk("doc-chunk-0", "alpha beta supported but incomplete")
    unrelated = make_chunk("doc-chunk-1", "different material must stay separate.")

    result = build_grounded_answer("alpha beta", [seed, unrelated], top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta supported but incomplete [doc-chunk-0]",
        ["doc-chunk-0"],
        False,
    )
    assert unrelated.text not in result.answer


def test_cross_document_neighbor_with_overlap_is_not_appended() -> None:
    seed = make_chunk("doc-a-chunk-0", "alpha beta shared boundary", "doc-a")
    other_document = make_chunk(
        "doc-b-chunk-0", "shared boundary must not continue.", "doc-b"
    )

    result = build_grounded_answer("alpha beta", [seed, other_document], top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta shared boundary [doc-a-chunk-0]",
        ["doc-a-chunk-0"],
        False,
    )
    assert "must not continue" not in result.answer


def test_wrong_order_continuation_is_not_searched_backward() -> None:
    continuation = make_chunk("doc-chunk-1", "shared boundary completed answer.")
    seed = make_chunk("doc-chunk-0", "alpha beta shared boundary")

    result = build_grounded_answer("alpha beta", [continuation, seed], top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta shared boundary [doc-chunk-0]",
        ["doc-chunk-0"],
        False,
    )
    assert "completed answer" not in result.answer


def test_missing_continuation_keeps_exact_incomplete_source_without_invention() -> None:
    seed = make_chunk("doc-chunk-0", "alpha beta source genuinely ends here")

    result = build_grounded_answer("alpha beta", [seed], top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta source genuinely ends here [doc-chunk-0]",
        ["doc-chunk-0"],
        False,
    )
    assert "here." not in result.answer


def test_multi_hop_continuation_stops_at_first_completed_sentence() -> None:
    chunks = [
        make_chunk("doc-chunk-0", "alpha beta one bridge"),
        make_chunk("doc-chunk-1", "one bridge two link"),
        make_chunk("doc-chunk-2", "two link completed sentence."),
        make_chunk("doc-chunk-3", "sentence. unrelated later text."),
    ]

    result = build_grounded_answer("alpha beta", chunks, top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n"
        "- alpha beta one bridge two link completed sentence. "
        "[doc-chunk-0] [doc-chunk-1] [doc-chunk-2]",
        ["doc-chunk-0", "doc-chunk-1", "doc-chunk-2"],
        False,
    )
    assert "unrelated later text" not in result.answer


def test_complete_seed_does_not_append_overlapping_neighbor() -> None:
    seed = make_chunk("doc-chunk-0", "alpha beta answer is complete.")
    neighbor = make_chunk("doc-chunk-1", "complete. unrelated next sentence.")

    result = build_grounded_answer("alpha beta", [seed, neighbor], top_k=1)

    assert result == RagAnswer(
        "Grounded answer:\n- alpha beta answer is complete. [doc-chunk-0]",
        ["doc-chunk-0"],
        False,
    )
    assert neighbor.text not in result.answer


def test_consumed_qualifying_continuation_is_not_emitted_or_cited_twice() -> None:
    chunks = [
        make_chunk("doc-chunk-0", "alpha beta bridge"),
        make_chunk("doc-chunk-1", "bridge alpha beta completed."),
    ]

    result = build_grounded_answer("alpha beta", chunks, top_k=2)

    assert result == RagAnswer(
        "Grounded answer:\n"
        "- alpha beta bridge alpha beta completed. [doc-chunk-0] [doc-chunk-1]",
        ["doc-chunk-0", "doc-chunk-1"],
        False,
    )
    assert result.answer.count("[doc-chunk-1]") == 1


@pytest.mark.parametrize(
    ("chunk_size", "overlap", "expected_citations"),
    [
        (140, 30, ["doc-1-chunk-0", "doc-1-chunk-1"]),
        (80, 20, ["doc-1-chunk-0", "doc-1-chunk-1", "doc-1-chunk-2"]),
    ],
)
def test_default_question_completes_under_outcome_one_chunking_configurations(
    chunk_size: int, overlap: int, expected_citations: list[str]
) -> None:
    chunks = build_chunks(
        load_default_corpus(), chunk_size=chunk_size, overlap=overlap
    )

    result = build_grounded_answer(SUPPORTED_QUESTION, chunks, top_k=2)

    inline_citations = " ".join(f"[{chunk_id}]" for chunk_id in expected_citations)
    assert result == RagAnswer(
        f"Grounded answer:\n- {DEFAULT_COMPLETE_TEXT} {inline_citations}",
        expected_citations,
        False,
    )


def test_training_rag_profile_completes_answer_with_adjacent_source() -> None:
    question = "Why are citations important in RAG?"
    chunks = build_chunks(load_training_rag_corpus(), chunk_size=140, overlap=30)

    result = build_grounded_answer(question, chunks, top_k=2)

    assert result == RagAnswer(
        "Grounded answer:\n"
        "- RAG with citations should retrieve relevant documents with source metadata and "
        "include references in the answer. Citations improve transparency and trust because "
        "users can verify evidence. [tr-doc-1-chunk-0] [tr-doc-1-chunk-1]",
        ["tr-doc-1-chunk-0", "tr-doc-1-chunk-1"],
        False,
    )


def test_adjacent_weak_chunks_cannot_combine_to_bypass_refusal() -> None:
    chunks = [
        make_chunk("doc-chunk-0", "alpha shared boundary"),
        make_chunk("doc-chunk-1", "shared boundary beta unsupported claim."),
    ]

    result = build_grounded_answer("alpha beta", chunks, top_k=2)

    assert result == RagAnswer(REFUSAL_MESSAGE, [], True)


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
