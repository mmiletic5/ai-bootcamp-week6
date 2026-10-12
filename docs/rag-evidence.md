# RAG Citation, Refusal, and Complete-Answer Evidence

Contributor: Isidora Prica - grounded answers and citations (Outcome 3), unsupported-question
refusal (Outcome 4), and the approved Feature 002 complete-grounded-answer quality improvement.

## Scope and ownership

This evidence covers the RAG answer layer, its automated tests, and CLI integration. Mateja
Miletic owns Outcomes 1 and 2: chunking, retrieval, their tests, the comparison script, and
`docs/chunking-retrieval-evidence.md`. Those files were not changed. The untracked
`docs/mateja_handoff.md` remained unchanged with SHA-256
`230543DC37628433F66F617B7CF4739DB8795C0E6F39C7AFC65BF678866508CB`.

Feature 002 is a post-homework quality improvement. Feature 001 and its T001-T010 history remain
accurate: the original implementation returned exact qualifying chunk text and valid citations,
but the default chunk boundary left its supported answer ending in `rather than`. Feature 002
completes that sentence only when adjacent source continuity can be verified.

## Requirements and behavior

The existing lexical evidence gate remains unchanged. A ranked chunk is an initial evidence seed
only when it contains at least two distinct meaningful question terms and covers at least 50% of
the distinct meaningful question terms. Retrieval order, scoring, top-k selection, refusal, and
invalid-`top_k` validation remain authoritative.

For a qualifying seed that ends without `.`, `?`, or `!`, the answer layer checks the original
ordered chunk collection rather than retrieval ranking. It considers only the immediate forward
neighbor, requires the same `doc_id`, and requires a non-empty exact suffix/prefix word overlap.
The longest valid overlap is removed once, and verified continuation may repeat across successive
neighbors until the first completed sentence. Every contributing chunk receives a separate
citation in first-use order. A continuation already consumed is not rendered as another bullet.

Zero-overlap, cross-document, backward, missing, or otherwise unverifiable boundaries are not
joined. Adjacency cannot create initial support or bypass refusal. No missing words or punctuation
are invented.

## Historical and Feature 002 TDD results

The completed Feature 001 history is preserved rather than relabeled as new verification:

```text
Original pre-implementation baseline: 56 passed
Original Outcome 3 RED: 4 failed, 4 passed in 0.11s
Original Outcome 3 GREEN: 8 passed in 0.04s
Original Outcome 3 full regression: 62 passed in 0.09s
Original Outcome 4 initial verification: 24 passed in 0.09s
Original Outcome 4 later focused verification: 24 passed in 0.05s
Original later full regression: 78 passed in 0.11s
Original CLI-focused initial verification: 29 passed in 0.16s
Historical pre-Feature-002 focused snapshot: 29 passed in 0.06s
Historical pre-Feature-002 full snapshot: 83 passed in 0.12s
```

Feature 002 followed a separate strict RED/GREEN cycle:

```text
Q002 RED: 13 failed, 30 passed in 0.30s
Q003 GREEN focused: 43 passed in 0.09s
Q003 GREEN full: 97 passed in 0.17s
Q004 final focused verification: 43 passed in 0.16s
Q004 final full verification: 97 passed in 0.28s
Q005 documentation verification focused: 43 passed in 0.13s
Q005 documentation verification full: 97 passed in 0.19s
```

The 13 RED failures were exact answer/citation differences caused by the absent continuation
behavior; there were no collection, syntax, fixture, refusal, or public-interface failures.

## Reproduction commands

Run from the repository root in Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest .\tests\test_rag.py -q
.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"
.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
.\.venv\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
.\.venv\Scripts\python.exe .\scripts\compare_chunking_retrieval.py
git diff --check
```

## Outcome 3: default supported-question evidence

Question: `What is retrieval augmented generation?`

Default configuration: corpus profile `default`, `chunk_size=140`, `overlap=30`, `top_k=2`.

Lexical retrieval remains unchanged:

| Rank | Chunk ID | Score | Role |
|---:|---|---:|---|
| 1 | `doc-1-chunk-0` | 0.294118 | Qualifying lexical seed: 3/3 meaningful terms |
| 2 | `doc-2-chunk-0` | 0.052632 | Non-qualifying ranked result: 1/3 meaningful terms |

`doc-1-chunk-1` is not the second lexical result. It is selected separately as the immediate
same-document source neighbor of the qualifying seed. Its prefix `retrieved evidence rather than`
exactly overlaps the seed suffix, so only `unsupported assumptions.` is appended. Both chunks are
cited because both contribute source text.

Actual CLI output:

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

## Both approved chunking configurations

The same exact source sentence is completed under both Outcome 1 configurations:

| Configuration | Answer citations | Continuation behavior |
|---|---|---|
| `(140,30)` | `doc-1-chunk-0`, `doc-1-chunk-1` | One verified adjacent continuation |
| `(80,20)` | `doc-1-chunk-0`, `doc-1-chunk-1`, `doc-1-chunk-2` | Two verified successive continuations |

Actual `(80,20)` answer:

```text
Grounded answer:
- Retrieval augmented generation combines retrieval with text generation. The model should answer using retrieved evidence rather than unsupported assumptions. [doc-1-chunk-0] [doc-1-chunk-1] [doc-1-chunk-2]
```

The read-only comparison script still reports 6 chunks for `(140,30)`, 9 chunks for `(80,20)`,
and the original ranks and scores. Feature 002 changes answer construction, not chunking or retrieval.

## Alternative `training-rag` profile

Actual CLI output:

```text
Question:
Why are citations important in RAG?

Answer:
Grounded answer:
- RAG with citations should retrieve relevant documents with source metadata and include references in the answer. Citations improve transparency and trust because users can verify evidence. [tr-doc-1-chunk-0] [tr-doc-1-chunk-1]

Corpus profile: training-rag

Refused: False
Citations: tr-doc-1-chunk-0, tr-doc-1-chunk-1
```

## Outcome 4: unsupported-question evidence

Question: `Who won the world cup in 1958?`

The unchanged retrieval results are `doc-1-chunk-0` (`0.058824`) and `doc-3-chunk-0`
(`0.047619`). Their positive scores come only from common words; neither matches the meaningful
terms `won`, `world`, `cup`, or `1958`. No qualifying seed exists, so continuation is never used.

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

## Compatibility and determinism verification

Q004 observed:

```text
RagAnswer fields: ['answer', 'citations', 'refused']
build_grounded_answer parameters: ['question', 'chunks', 'top_k']
top_k default: 2
API deterministic: True
Supported CLI deterministic: True
Unsupported CLI deterministic: True
```

Invalid values retain the existing behavior:

```text
top_k=True: TypeError: k must be a positive integer
top_k=1.5: TypeError: k must be a positive integer
top_k=0: ValueError: k must be > 0
top_k=-1: ValueError: k must be > 0
```

Tests cover exact formatting, one-hop and multi-hop continuation, longest and repeated overlap,
zero-overlap rejection, unrelated same-document text, cross-document and wrong-order chunks,
missing continuation, already-complete excerpts, incomplete sources, citation deduplication,
consumed continuations, both corpus profiles, refusal, and API compatibility.

## Known limitations and risks

- Lexical qualification is not semantic entailment, factual verification, or external truth checking.
- Exact boundary overlap proves textual continuity, not semantic relevance by itself.
- A zero-overlap or otherwise unverifiable boundary remains incomplete by design because `Chunk`
  does not carry source offsets or the original document text.
- Sentence completion recognizes only trailing `.`, `?`, and `!`.
- Conservative evidence thresholds can refuse valid short, synonymous, acronym-based, or
  paraphrased questions.
- Tokenization remains ASCII-oriented, and the corpus is small and static.
- The system is deterministic and extractive; it does not use an LLM to generate or paraphrase answers.

## Integration status

Feature 002 Q001-Q005 are complete. [Pull request #1](https://github.com/mmiletic5/ai-bootcamp-week6/pull/1)
was merged into `develop` at commit `112c919`. The integrated full test suite was independently
verified on October 12, 2026 with `97 passed in 0.26s`. The GitHub repository link has not yet been
submitted to the professor, and the demo lead remains unassigned.
