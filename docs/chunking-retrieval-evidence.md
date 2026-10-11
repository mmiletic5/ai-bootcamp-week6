# Chunking and Retrieval Evidence

Contributor: Mateja Miletic — Chunking and Retrieval, Outcome 1 and Outcome 2.

This document covers only completed chunking and top-k retrieval work. Citation,
refusal, shared evidence, and final submission documentation are outside its scope.

## Initial Baseline and Implementation Changes

- Python: 3.10.12
- pytest: 8.3.3
- Original baseline: 9 passed
- Final verification: 56 passed

The starter chunker used fixed character windows and could split ordinary words at
chunk boundaries. The final chunker remains character-bounded but packs complete
words, treats overlap as a character target over complete trailing words, and uses
character windows only for a word longer than `chunk_size`.

The starter retriever used the same lightweight lexical score but validated only
non-positive `k`, could include zero-score chunks when `min_score=0`, and preserved
input order for equal scores. The final retriever validates positive integer `k`
and finite non-negative `min_score`, excludes zero-score chunks, and breaks score
ties by ascending chunk ID.

## Reproduction

All commands were run from the repository root with the local virtual environment
activated:

```bash
source .venv/bin/activate
python -m pytest tests/test_chunking.py -q
python -m pytest tests/test_retrieval.py -q
./scripts/run_tests.sh
python scripts/compare_chunking_retrieval.py
```

Results:

```text
21 passed in 0.05s
30 passed in 0.06s
56 passed in 0.11s
```

The evidence below uses the `default` corpus profile, query `What is retrieval
augmented generation?`, and `min_score=0.01`.

## Outcome 1: Chunking impact

The chunker normalizes whitespace and keeps ordinary words intact. It packs whole
words into character-bounded chunks. Overlap is a character target: it reuses the
largest trailing suffix of complete words that fits the target and can also fit
with the next new word. When no such suffix exists, the overlap is zero. A word
longer than the configured chunk size is the intentional exception and is split
into overlapping character windows.

### Configuration A

- `chunk_size=140`
- `overlap=30`
- Generated chunks: 6
- Retrieval setting: `k=3`, `min_score=0.01`

| Rank | Chunk ID | Document ID | Score | Retrieved text |
|---:|---|---|---:|---|
| 1 | `doc-1-chunk-0` | `doc-1` | 0.294118 | Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than |
| 2 | `doc-2-chunk-0` | `doc-2` | 0.052632 | Chunking splits documents into smaller parts. Good chunk size and overlap improve retrieval quality. Metadata helps filtering and source |

### Configuration B

- `chunk_size=80`
- `overlap=20`
- Generated chunks: 9
- Retrieval setting: `k=3`, `min_score=0.01`

| Rank | Chunk ID | Document ID | Score | Retrieved text |
|---:|---|---|---:|---|
| 1 | `doc-1-chunk-0` | `doc-1` | 0.555556 | Retrieval augmented generation combines retrieval with text generation. The |
| 2 | `doc-1-chunk-1` | `doc-1` | 0.090909 | text generation. The model should answer using retrieved evidence rather than |
| 3 | `doc-2-chunk-1` | `doc-2` | 0.090909 | size and overlap improve retrieval quality. Metadata helps filtering and source |

### Observed difference

Configuration A provides one longer, continuous RAG definition and grounding
excerpt. Configuration B divides that material into more focused, word-complete
chunks: the definition is rank 1 and its grounding continuation is rank 2. The
higher rank-1 score for B follows from the length-normalized lexical formula and
does not establish that B is universally better. For this question, A offers more
single-chunk contextual continuity, while B offers finer-grained evidence.

## Outcome 2: Top-k retrieval

The lexical score is calculated as:

```text
number of chunk-token occurrences present in the query-token set
----------------------------------------------------------------
total number of chunk tokens
```

Tokens are lowercase ASCII alphanumeric sequences. Repeated query tokens do not
increase the query set, while repeated matching chunk tokens are counted. Eligible
results require both `score > 0` and `score >= min_score`; therefore
`min_score=0` still excludes irrelevant zero-score chunks. Results are ordered by
descending score and, for equal scores, ascending chunk ID.

The following uses Configuration B from Outcome 1 (`chunk_size=80`, `overlap=20`),
the same corpus, query, and `min_score=0.01`.

### `top_k=2`

| Rank | Chunk ID | Document ID | Score | Retrieved text |
|---:|---|---|---:|---|
| 1 | `doc-1-chunk-0` | `doc-1` | 0.555556 | Retrieval augmented generation combines retrieval with text generation. The |
| 2 | `doc-1-chunk-1` | `doc-1` | 0.090909 | text generation. The model should answer using retrieved evidence rather than |

### `top_k=3`

| Rank | Chunk ID | Document ID | Score | Retrieved text |
|---:|---|---|---:|---|
| 1 | `doc-1-chunk-0` | `doc-1` | 0.555556 | Retrieval augmented generation combines retrieval with text generation. The |
| 2 | `doc-1-chunk-1` | `doc-1` | 0.090909 | text generation. The model should answer using retrieved evidence rather than |
| 3 | `doc-2-chunk-1` | `doc-2` | 0.090909 | size and overlap improve retrieval quality. Metadata helps filtering and source |

The rank-1 chunk has five matching token occurrences among nine chunk tokens,
giving `5 / 9 = 0.555556`. Each lower-ranked chunk has one matching occurrence
among eleven chunk tokens, giving `1 / 11 = 0.090909`. The equal-score results
are ordered by chunk ID: `doc-1-chunk-1` precedes `doc-2-chunk-1`.

Programmatic checks confirmed that result counts never exceed `k`, results are in
non-increasing score order, returned chunks are the highest-scoring eligible
chunks, and each result belongs to the generated corpus.

Additional observed behavior:

```text
retrieve_top_k("basketball playoffs", chunks, k=3, min_score=0.01) -> []
retrieve_top_k(query, chunks, k=True) -> TypeError: k must be a positive integer
retrieve_top_k(query, chunks, min_score=NaN) -> ValueError: min_score must be finite
```

## Edge-case verification

The focused chunking tests verify invalid zero/negative chunk sizes, invalid
overlap values, long-word character splitting, maximum chunk length, source-word
coverage, and forward progress. The focused retrieval tests verify empty queries
and corpora, invalid `k`, invalid `min_score`, zero-score exclusion at
`min_score=0`, and deterministic equal-score ordering by chunk ID. These checks
are included in the reproduction commands above.

## Limitations and Integration Handoff

Overlap is a character target rather than an exact guarantee: preserving whole
words can produce a smaller effective overlap. Retrieval is lexical rather than
semantic, and tokenization is ASCII-oriented. Public chunking and retrieval
interfaces, chunk IDs, document IDs, titles, and chunk text are preserved. The
completed behavior remains compatible with the existing RAG pipeline, which
continues to consume `retrieve_top_k` results and chunk metadata without changes.
