# Week 6 RAG Evidence

Verified locally on 2026-10-12 from `feature/isidora-week6` at pre-T010 HEAD
`40fb6a8904f9ccd5241ee3fbf4cc276d12d6609a`. All scores below are produced by the
deterministic lexical retriever; they do not establish semantic entailment or external factual truth.
Feature 002 was later verified in the working tree at HEAD
`4ca231a546592f3e7bba60e2c0f4f622379819aa`; its results are labeled separately below.

## 1. Outcome 1: Chunking impact

Question: `What is retrieval augmented generation?`

Corpus: `default`; `top_k=3`; minimum score `0.01`.

| Configuration | Parameters | Chunk count | Retrieved results in rank order |
|---|---|---:|---|
| A | `chunk_size=140`, `overlap=30` | 6 | `doc-1-chunk-0` (0.294118), `doc-2-chunk-0` (0.052632) |
| B | `chunk_size=80`, `overlap=20` | 9 | `doc-1-chunk-0` (0.555556), `doc-1-chunk-1` (0.090909), `doc-2-chunk-1` (0.090909) |

Configuration A returns a longer first chunk:

```text
Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than
```

Configuration B splits that passage. Its first result is shorter and more concentrated, so the
same five matching token occurrences make up a larger fraction of the chunk (`0.555556` rather
than `0.294118`). The continuation becomes a separate second result. The two `0.090909` results
are ordered by chunk ID, so `doc-1-chunk-1` precedes `doc-2-chunk-1`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe .\scripts\compare_chunking_retrieval.py
```

Detailed evidence: `docs/chunking-retrieval-evidence.md`.

## 2. Outcome 2: Top-k retrieval

Query: `rag citation`

| Rank | Chunk ID | Text | Score | In top 2 | In top 3 |
|---:|---|---|---:|:---:|:---:|
| 1 | `chunk-a` | `rag citation` | 1.000000 | yes | yes |
| 2 | `chunk-b` | `rag citation filler` | 0.666667 | yes | yes |
| 3 | `chunk-c` | `rag retrieval citation evidence extra` | 0.400000 | no | yes |

The score is the count of chunk-token occurrences that appear in the query-token set, divided
by the number of chunk tokens. Results are sorted by descending score and then ascending stable
chunk ID. A verified equal-score example returned `a-id`, `m-id`, `z-id`, independent of input
order. Results with score zero are ineligible, even when `min_score=0`; every returned ID belongs
to an input chunk.

The project tests reproduce `top_k=2`, `top_k=3`, score ordering, tie-breaking, zero-score
exclusion, validation, metadata preservation, and input immutability:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_retrieval.py -q
```

## 3. Outcome 3: Citation quality

Supported question: `What is retrieval augmented generation?`

Retrieved with the default settings:

| Rank | Chunk ID | Score | Qualifies for the answer |
|---:|---|---:|:---:|
| 1 | `doc-1-chunk-0` | 0.294118 | yes: 3/3 meaningful query terms |
| 2 | `doc-2-chunk-0` | 0.052632 | no: 1/3 meaningful query terms |

Exact answer:

```text
Grounded answer:
- Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than unsupported assumptions. [doc-1-chunk-0] [doc-1-chunk-1]
```

Citation list: `doc-1-chunk-0`, `doc-1-chunk-1`

Refused: `False`

`doc-1-chunk-0` remains the only qualifying lexical seed; the weak ranked result
`doc-2-chunk-0` remains absent. The answer layer finds `doc-1-chunk-1` independently as the
immediate same-document neighbor in original source order, verifies the exact boundary overlap,
appends only `unsupported assumptions.`, and cites both contributing chunks. Retrieval ranking
and source adjacency are not treated as the same order.

## 4. Outcome 4: Refusal behavior

Unsupported question: `Who won the world cup in 1958?`

Retrieved context:

| Rank | Chunk ID | Score | Meaningful matches (`won`, `world`, `cup`, `1958`) |
|---:|---|---:|---:|
| 1 | `doc-1-chunk-0` | 0.058824 | 0 |
| 2 | `doc-3-chunk-0` | 0.047619 | 0 |

The positive raw scores come only from common words removed by the evidence-qualification rule.
Neither chunk reaches two distinct meaningful matches or 50% meaningful-term coverage.

Exact refusal:

```text
I do not have enough grounded evidence in the provided corpus to answer that question.
```

Refused: `True`

Citations: `None`

No retrieved excerpt, citation, or World Cup claim appears in the answer.

## 5. Outcome 5: Final supported and unsupported evidence pair

### Supported case

Command:

```powershell
.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"
```

Retrieved results: `doc-1-chunk-0` (0.294118), `doc-2-chunk-0` (0.052632). Only the first
qualifies as the lexical seed. `doc-1-chunk-1` is a separately verified adjacent source continuation.

```text
Question:
What is retrieval augmented generation?

Answer:
Grounded answer:
- Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than unsupported assumptions. [doc-1-chunk-0] [doc-1-chunk-1]

Corpus profile: default

Refused: False
Citations: doc-1-chunk-0, doc-1-chunk-1
```

The command was run twice during final verification and produced identical output.

### Unsupported case

Command:

```powershell
.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
```

Retrieved results: `doc-1-chunk-0` (0.058824), `doc-3-chunk-0` (0.047619). Neither qualifies.

```text
Question:
Who won the world cup in 1958?

Answer:
I do not have enough grounded evidence in the provided corpus to answer that question.

Corpus profile: default

Refused: True
Citations: None
```

### Verification snapshot

Historical pre-Feature-002 results are preserved:

```text
.\.venv\Scripts\python.exe -m pytest -q
83 passed in 0.12s

.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q
29 passed in 0.06s
```

Feature 002 TDD and final verification were observed separately:

```text
Q002 RED: 13 failed, 30 passed in 0.30s
Q003 GREEN: 43 passed in 0.09s; 97 passed in 0.17s
Q004 final: 43 passed in 0.16s; 97 passed in 0.28s
Q005 documentation verification: 43 passed in 0.13s; 97 passed in 0.19s
```

The default supported and unsupported CLI commands produced identical output on repeated runs.
The `training-rag` supported command completed its answer with citations
`tr-doc-1-chunk-0`, `tr-doc-1-chunk-1`. Under `(80,20)`, the default answer required and cited
`doc-1-chunk-0`, `doc-1-chunk-1`, and `doc-1-chunk-2`.

## Contributions

- Mateja Miletic: Outcomes 1 and 2 (chunking, retrieval, tests, comparison script, and detailed evidence).
- Isidora Prica: Outcomes 3 and 4 (grounded extractive answers, citations, refusal behavior, tests, and detailed evidence).
- Isidora Prica: final technical integration and shared Outcome 5 evidence preparation, completed independently with Mateja's permission.
- Isidora Prica: Feature 002 verified adjacent-source continuation, tests, and updated Outcome 3/5 evidence.

No claim is made that Mateja reviewed or approved this final integrated document. The demo lead
has not been agreed or recorded. No external submission, merge, rebase, push, or pull request was performed.
