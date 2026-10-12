from dataclasses import fields
from inspect import signature

from src.chunking import Chunk
from src.chunking import build_chunks
from src.corpus import load_default_corpus
from src.rag import RagAnswer, build_grounded_answer
from src.retrieval import retrieve_top_k


SUPPORTED_QUESTION = "What is retrieval augmented generation?"


def make_chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id="doc", title="Title", text=text)


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
