# RAG Citation and Refusal Evidence

Contributor: Isidora Prica — grounded answers and citations (Outcome 3) and
unsupported-question refusal (Outcome 4).

## Scope and ownership

This evidence covers the RAG answer layer, its automated tests, and the existing CLI
integration. Mateja Miletic owns Outcome 1 and Outcome 2: chunking, retrieval, their tests,
`docs/chunking-retrieval-evidence.md`, and the comparison script. Those tracked files were
not changed. `docs/mateja_handoff.md` was preserved with SHA-256
`230543DC37628433F66F617B7CF4739DB8795C0E6F39C7AFC65BF678866508CB`.

Outcome 5, root `evidence.md`, README submission guidance, pair accountability, demo-lead
selection, remote operations, and integration remain outside this individual scope.

## Requirements and acceptance criteria

- R3.1/AC3.1: supported output uses exact qualifying chunk text without added factual prose.
- R3.2/AC3.2: inline and returned citation IDs are valid, qualifying retrieved IDs, ordered
  and deduplicated.
- R3.3/AC3.3 and R5.1/AC5.1: repeated calls are deterministic and the CLI exposes separate
  Question, Answer, Refused, and Citations sections through its existing arguments.
- R3.4/AC3.4: `RagAnswer` and `build_grounded_answer(question, chunks, top_k=2)` remain compatible.
- R4.1-R4.4/AC4.1-AC4.4: missing or insufficient evidence returns only the exact refusal,
  no citations, and `refused=True`.
- R4.5/AC4.5: invalid `top_k` errors from retrieval continue to propagate.

## Baseline and TDD history

The verified pre-implementation baseline on 2026-10-12 was 56 passing tests. Outcome 3
then followed a genuine RED/GREEN cycle:

```text
RED:   4 failed, 4 passed in 0.11s
GREEN: 8 passed in 0.04s
Full regression after Outcome 3: 62 passed in 0.09s
```

The four genuine failures covered exact extractive formatting, qualifying-only citations,
weak-result exclusion, and duplicate-ID suppression. Outcome 4 was different: all 16 newly
added cases passed immediately because T004 had already implemented the shared evidence gate.
The observed Outcome 4 result was `24 passed in 0.09s`; no false RED failure or unnecessary
application edit was introduced. Its later verification reported `24 passed in 0.05s` and
`78 passed in 0.11s` for the full suite.

T007 added five CLI cases. They passed on their first focused run (`29 passed in 0.16s`), so
`src/cli.py` required no change.

## Exact reproduction commands

Run these commands from the repository root in Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q -k "empty_or_whitespace or empty_chunk or no_retrieved or only_stopwords or irrelevant_common_word or only_one_distinct or below_half or at_half or duplicate_query or refusal_contains or invalid_top_k or supported_question_remains"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"
.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
```

The retrieval details not displayed by the CLI were obtained with these actual commands:

```powershell
.\.venv\Scripts\python.exe -c "from src.chunking import build_chunks; from src.corpus import load_default_corpus; from src.rag import build_grounded_answer; from src.retrieval import retrieve_top_k; q='What is retrieval augmented generation?'; chunks=build_chunks(load_default_corpus(), chunk_size=140, overlap=30); print([(x.chunk.chunk_id, round(x.score, 6), x.chunk.text) for x in retrieve_top_k(q, chunks, k=2)]); print(build_grounded_answer(q, chunks, top_k=2))"
.\.venv\Scripts\python.exe -c "from src.chunking import build_chunks; from src.corpus import load_default_corpus; from src.rag import build_grounded_answer; from src.retrieval import retrieve_top_k; q='Who won the world cup in 1958?'; chunks=build_chunks(load_default_corpus(), chunk_size=140, overlap=30); print([(x.chunk.chunk_id, round(x.score, 6), x.chunk.text) for x in retrieve_top_k(q, chunks, k=2)]); print(build_grounded_answer(q, chunks, top_k=2))"
```

## Outcome 3: supported-question evidence

Question: `What is retrieval augmented generation?`

Default configuration: corpus profile `default`, `chunk_size=140`, `overlap=30`, `top_k=2`.

Actual retrieval results:

| Rank | Chunk ID | Score | Retrieved text |
|---:|---|---:|---|
| 1 | `doc-1-chunk-0` | 0.294118 | Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than |
| 2 | `doc-2-chunk-0` | 0.052632 | Chunking splits documents into smaller parts. Good chunk size and overlap improve retrieval quality. Metadata helps filtering and source |

Actual RAG result:

```text
Answer: Grounded answer:
- Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than [doc-1-chunk-0]
Citations: ['doc-1-chunk-0']
Refused: False
```

`doc-1-chunk-0` matches all three meaningful query terms and qualifies. The weak second
retrieval result does not qualify and is absent from both the answer and citation list.

Actual CLI output:

```text
Question:
What is retrieval augmented generation?

Answer:
Grounded answer:
- Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than [doc-1-chunk-0]

Corpus profile: default

Refused: False
Citations: doc-1-chunk-0
```

## Outcome 4: unsupported-question evidence

Question: `Who won the world cup in 1958?`

Actual retrieval results show why a positive lexical score alone is insufficient:

| Rank | Chunk ID | Score | Retrieved text |
|---:|---|---:|---|
| 1 | `doc-1-chunk-0` | 0.058824 | Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than |
| 2 | `doc-3-chunk-0` | 0.047619 | If retrieved context does not support a claim, the system should refuse and ask for better evidence. This reduces hallucinations and |

The meaningful terms are `won`, `world`, `cup`, and `1958`. Neither retrieved chunk matches
any of them, so neither qualifies. The actual RAG result was:

```text
Answer: I do not have enough grounded evidence in the provided corpus to answer that question.
Citations: []
Refused: True
```

Actual CLI output:

```text
Question:
Who won the world cup in 1958?

Answer:
I do not have enough grounded evidence in the provided corpus to answer that question.

Corpus profile: default

Refused: True
Citations: None
```

## Edge cases and automated results

The focused edge-case command above produced:

```text
16 passed, 13 deselected in 0.05s
```

Those cases cover empty and whitespace-only questions, empty chunks, no retrieved result,
stopword/common-word false positives, only one distinct meaningful match, two matches below
50% coverage, the exact 50% boundary, duplicate query terms, safe refusal contents, all four
invalid `top_k` variants, and a supported regression case.

The latest T008 verification produced:

```text
29 passed in 0.06s
83 passed in 0.12s
```

The focused total includes the five new CLI cases; the full total includes the unchanged
chunking, corpus, and retrieval regression tests.

## Deterministic qualification rule

The RAG layer tokenizes with the existing ASCII-alphanumeric tokenizer, removes the frozen
question-stopword set, and considers distinct meaningful query terms. A retrieved chunk
qualifies only when it contains at least two distinct meaningful terms and covers at least
50% of all distinct meaningful query terms. Qualifying chunks retain retrieval order;
duplicate chunk IDs are emitted once. Answers contain exact qualifying text plus inline IDs.

This lexical overlap rule is deterministic, but it is not semantic entailment, factual
verification, or a guarantee of correctness. Passing the threshold may still yield partial
support, while valid short, synonymous, acronym-based, or paraphrased questions may be
refused. The system cannot verify facts beyond its local corpus.

## Integration handoff

Outcomes 3 and 4 are individually verified. T010 must re-run integrated tests and both CLI
examples before creating shared root evidence or marking Outcome 5, pair accountability,
demo-lead, README, or submission items complete. No push, merge, rebase, pull request, or
remote operation was performed in this work.
