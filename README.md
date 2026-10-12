# Week 6 RAG Homework

## Project overview

This project is a small, deterministic retrieval-augmented generation (RAG)
application. It loads an in-memory corpus, creates word-aware chunks, retrieves
lexically relevant evidence, and returns either a grounded extractive answer with
citations or a refusal when evidence is insufficient.

The pipeline is:

```text
Corpus -> word-aware chunking -> lexical top-k retrieval
       -> evidence qualification -> verified source continuation
       -> extractive answer with citations OR refusal -> CLI
```

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
  scripts/
    run_tests.sh
    compare_chunking_retrieval.py
  docs/
    evidence.md
    chunking-retrieval-evidence.md
    rag-evidence.md
    homework-checklist.md
  requirements.txt
```

## Setup

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

The project requires Python 3.10 or a compatible Python 3 version. The only
declared test dependency is `pytest==8.3.3`.

## Run tests

Activate the virtual environment first. The latest verified full-suite result is
97 passing tests; rerun the commands below to verify the current checkout.

Full suite:

```bash
./scripts/run_tests.sh
```

Focused tests:

```bash
# Chunking: word-aware splitting, chunk sizes, and overlap handling
python -m pytest tests/test_chunking.py -v

# Retrieval: top-k selection, scoring, ranking, and input validation
python -m pytest tests/test_retrieval.py -v

# RAG: grounded answers, citations, refusal behavior, and integration
python -m pytest tests/test_rag.py -v
```

Pytest verifies the implemented behavior and regression coverage.

## Run chunking and retrieval comparison

```bash
python scripts/compare_chunking_retrieval.py
```

This read-only comparison script reproduces the A/B chunking experiment and
top-k retrieval behavior. It compares Configuration A (`chunk_size=140`,
`overlap=30`, 6 chunks) with Configuration B (`chunk_size=80`, `overlap=20`,
9 chunks), and prints chunk IDs, document IDs, scores, text, and ranking checks
for `top_k=2` and `top_k=3`.

The script demonstrates experimental results; it is not a replacement for pytest.

## Run demo CLI

```bash
python -m src.cli --question "What is retrieval augmented generation?"
python -m src.cli --question "Who won the world cup in 1958?"
python -m src.cli --question "What is retrieval augmented generation?" --chunk-size 80 --overlap 20
python -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
```

These commands demonstrate, respectively: a supported grounded answer; an
unsupported-question refusal; the supported answer under alternate chunking; and
a supported answer over the training-focused corpus. Full verified command outputs
are in [`docs/evidence.md`](docs/evidence.md).

## Corpus profiles

- `default`: compact baseline corpus for Week 6 RAG fundamentals.
- `training-rag`: examples focused on citations, references, RAG evaluation, and
  grounded refusal behavior.

CLI options include `--chunk-size` (default `140`), `--overlap` (default `30`),
`--top-k` (default `2`), and `--corpus-profile`.

## Documentation and evidence

- [`docs/evidence.md`](docs/evidence.md): complete final evidence for all five homework outcomes, including
  the supported and unsupported CLI evidence pair.
- `docs/chunking-retrieval-evidence.md`: detailed chunking experiments,
  configuration comparison, retrieval ranking, top-k results, and related tests.
- `docs/rag-evidence.md`: grounded-answer behavior, citation validation, refusal
  cases, and RAG tests.
- `docs/homework-checklist.md`: homework requirements and submission checklist.

## Technical limitations

- Retrieval is lexical rather than semantic; the project does not use embeddings,
  a vector database, external LLMs, or factual-entailment verification.
- Whole-word chunking treats overlap as a character target, so effective overlap
  can be smaller when preserving word boundaries.
- Conservative evidence qualification can refuse valid synonym, acronym, or
  paraphrase questions.
- Verified continuation requires same-document forward source order and exact word
  overlap; sentence completion recognizes only `.`, `?`, and `!`.
- Tokenization is ASCII-oriented, and the in-memory corpus is intentionally small.
