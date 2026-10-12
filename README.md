# Week 6 RAG Homework

This completed local project demonstrates the Week 6 RAG learning goals:

- corpus preparation
- chunking with overlap
- simple retrieval
- answer generation with citations
- refusal behavior when evidence is missing

## Learning goals

By the end of this homework, a student pair should be able to:

1. Explain how chunking strategy affects retrieval quality.
2. Implement a retrieval pipeline that returns top-k relevant chunks.
3. Return answers with explicit citations to source chunks.
4. Refuse unsupported questions instead of hallucinating.
5. Show evidence for one supported and one unsupported question.

## Architecture

The deterministic pipeline is:

```text
Corpus -> word-aware chunking -> lexical top-k retrieval
       -> evidence qualification -> extractive answer with citations OR refusal -> CLI
```

- `src/corpus.py` provides the `default` and `training-rag` in-memory corpus profiles.
- `src/chunking.py` creates character-bounded, word-aware chunks with overlap and stable IDs.
- `src/retrieval.py` scores lexical overlap, excludes zero-score results, and sorts by descending
  score with chunk ID as the deterministic tie-breaker.
- `src/rag.py` requires at least two distinct meaningful query-term matches and at least 50%
  meaningful-term coverage per chunk. It copies qualifying chunk text exactly and cites its ID;
  otherwise it returns the fixed refusal.
- `src/cli.py` exposes the pipeline without external services.

This project does **not** use an external LLM, embeddings, a vector database, semantic retrieval,
or factual-entailment verification.

## Project structure

```text
ai-bootcamp-week6/
  src/
    corpus.py
    chunking.py
    retrieval.py
    rag.py
    cli.py
  tests/
    test_chunking.py
    test_retrieval.py
    test_rag.py
  docs/
    chunking-retrieval-evidence.md
    rag-evidence.md
    homework-checklist.md
  evidence.md
  scripts/
    compare_chunking_retrieval.py
    run_tests.sh
  requirements.txt
```

## Prerequisites

- Python 3.10 or a compatible Python 3 version
- `pip`
- Git is useful for review but not required to run the project

The only declared test dependency is `pytest==8.3.3`.

## Setup on Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

## Setup on Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run tests

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest .\tests\test_rag.py -q
```

Linux/macOS:

```bash
./scripts/run_tests.sh
```

The final verified snapshot is `83 passed` for the complete suite and `29 passed` for
`tests/test_rag.py`.

## Run the CLI demonstrations

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"
.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
.\.venv\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
```

Linux/macOS after activation:

```bash
python -m src.cli --question "What is retrieval augmented generation?"
python -m src.cli --question "Who won the world cup in 1958?"
python -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
```

## Corpus profiles

- `default`: compact baseline corpus for Week 6 fundamentals.
- `training-rag`: examples focused on citations, references, evaluation framing, and refusal.

CLI options include `--chunk-size` (default `140`), `--overlap` (default `30`), `--top-k`
(default `2`), and `--corpus-profile`.

## Reproduce the chunking and retrieval comparison

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe .\scripts\compare_chunking_retrieval.py
```

Linux/macOS:

```bash
python scripts/compare_chunking_retrieval.py
```

The script compares `(chunk_size=140, overlap=30)` with `(chunk_size=80, overlap=20)`, reports
chunk counts and exact ranked results, and shows both `top_k=2` and `top_k=3` behavior.

## Evidence and contributions

- Root `evidence.md`: self-contained Outcomes 1-5 and the final supported/unsupported pair.
- `docs/chunking-retrieval-evidence.md`: detailed Outcomes 1-2 evidence by Mateja Miletic.
- `docs/rag-evidence.md`: detailed Outcomes 3-4 evidence by Isidora Prica.
- `docs/homework-checklist.md`: verified submission-readiness state.

Mateja Miletic completed Outcomes 1 and 2. Isidora Prica completed Outcomes 3 and 4, then
performed final technical integration and prepared shared Outcome 5 evidence with Mateja's
permission. A final Mateja review is not claimed. The demo lead remains to be agreed.

## Known limitations

- Lexical overlap is not semantic understanding, entailment, or external fact verification.
- Conservative qualification can refuse valid one-keyword, synonym, acronym, or paraphrase queries.
- A threshold-passing excerpt may still be incomplete; the supported default excerpt ends with
  `rather` at its real chunk boundary.
- Exact extractive answers favor provenance over fluency.
- Tokenization is ASCII-oriented and the corpus is small and static.

## Submission readiness

Before packaging, rerun the full tests, focused RAG tests, both CLI commands, the comparison
script, and `git diff --check`. Review `evidence.md` and the homework checklist. The technical
materials are locally review-ready, but the demo lead and any external submission/publishing
decision remain deliberately unresolved.
