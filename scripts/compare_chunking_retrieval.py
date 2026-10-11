"""Reproduce Mateja Miletic's Outcome 1 and Outcome 2 comparisons."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking import build_chunks
from src.corpus import load_corpus
from src.retrieval import lexical_score, retrieve_top_k


QUERY = "What is retrieval augmented generation?"
PROFILE = "default"
MIN_SCORE = 0.01


def verify_and_print(label: str, chunks, k: int) -> None:
    results = retrieve_top_k(QUERY, chunks, k=k, min_score=MIN_SCORE)
    eligible = [
        chunk
        for chunk in chunks
        if lexical_score(QUERY, chunk.text) > 0
        and lexical_score(QUERY, chunk.text) >= MIN_SCORE
    ]
    expected = sorted(eligible, key=lambda chunk: (-lexical_score(QUERY, chunk.text), chunk.chunk_id))

    assert len(results) <= k
    assert [result.score for result in results] == sorted(
        (result.score for result in results), reverse=True
    )
    assert [result.chunk.chunk_id for result in results] == [chunk.chunk_id for chunk in expected[:k]]
    assert all(result.chunk in chunks for result in results)

    print(f"{label}: top_k={k}")
    for rank, result in enumerate(results, start=1):
        print(
            f"  rank={rank} chunk_id={result.chunk.chunk_id} doc_id={result.chunk.doc_id} "
            f"score={result.score:.6f} text={result.chunk.text!r}"
        )


def main() -> None:
    corpus = load_corpus(PROFILE)
    print(f"query: {QUERY}")
    print(f"corpus_profile: {PROFILE}")
    print(f"min_score: {MIN_SCORE}")

    for label, chunk_size, overlap in (("Configuration A", 140, 30), ("Configuration B", 80, 20)):
        chunks = build_chunks(corpus, chunk_size=chunk_size, overlap=overlap)
        print(f"{label}: chunk_size={chunk_size}, overlap={overlap}, chunk_count={len(chunks)}")
        verify_and_print(label, chunks, k=3)
        if label == "Configuration B":
            verify_and_print(label, chunks, k=2)


if __name__ == "__main__":
    main()
