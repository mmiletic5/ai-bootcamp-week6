# Research: Grounded RAG Citations and Refusal

## Verified Baseline

- Branch: `feature/isidora-week6`; HEAD: `f9954121ac3094b8c6690912fdcbf1977e0a9d5a`.
- Mateja commits `a71ff793`, `7d0bfac`, and `f9954121` are present.
- Initial working tree contained only untracked `docs/mateja_handoff.md`.
- Handoff SHA-256 before Spec Kit initialization:
  `230543DC37628433F66F617B7CF4739DB8795C0E6F39C7AFC65BF678866508CB`.
- Verified automated baseline before T001: `56 passed in 0.15s`.
- The requested starter ZIP is absent; initial commit `2996b4a` is the comparison baseline.
- The instructor PDF and README agree on Outcomes 1-5 and the required evidence structure.

## Architecture and Gap Analysis

The verified pipeline is:

`Corpus -> Chunking -> Retrieval -> RAG Answer -> Citation/Refusal -> CLI`

Mateja completed word-aware chunking and deterministic validated lexical top-k retrieval.
Those interfaces expose stable chunk IDs, metadata, text, and score and are preserved.

`src/rag.py` remains starter code. It refuses only when retrieval is empty or the best raw
score is below `0.02`; otherwise it quotes and cites every returned result. This permits common
words to produce unsupported answers. `tests/test_rag.py` checks only citation presence and one
unrelated refusal, not grounding, citation identity, weak matches, formatting, or determinism.

## Decisions

### D-001 - Conservative per-chunk lexical sufficiency

Use `src.retrieval.tokenize`. Remove these normalized stopwords from the distinct query terms:

`a, an, and, are, as, at, be, by, did, do, does, for, from, how, i, in, is, it, of, on, or,
that, the, this, to, was, were, what, when, where, which, who, why, with`

A retrieved chunk qualifies only if it matches at least two distinct meaningful terms and
at least 50% of all distinct meaningful query terms. At least one qualifying chunk is required.

**Rationale**: This blocks the observed stopword false positive while keeping the algorithm
small, local, deterministic, and compatible with existing retrieval.

**Rejected alternatives**:

- Raw retrieval-score threshold: score depends on chunk length and can reward common words.
- Coverage alone: a one-word match can qualify a short or vague query.
- Exact phrase matching: unnecessarily rejects word-order variation.
- External semantic models: outside homework scope and dependency constraints.

### D-002 - Extractive answer construction

Render each unique qualifying result as `- <exact chunk text> [<chunk-id>]` beneath
`Grounded answer:`. Build `citations` from the same results in retrieval order.

**Rationale**: Exact excerpts provide auditable provenance and prevent new factual prose.

### D-003 - Preserve public interfaces

Keep the three-field `RagAnswer`, `REFUSAL_MESSAGE`, and
`build_grounded_answer(question, chunks, top_k=2)`. Add only private helpers in `src/rag.py`.
Do not change retrieval thresholds or signatures.

### D-004 - CLI changes only when a failing test requires them

The existing CLI already separates Answer, Refused, and Citations. Test it directly; modify
`src/cli.py` only if the approved observable contract is not met.

### D-005 - Official Spec Kit setup

Spec Kit `0.12.11` was installed through `uv` and initialized in place with Codex skills and
PowerShell scripts. This pinned version does not expose the newer `--non-interactive` option;
explicit integration, skill, script, and force options supplied equivalent deterministic input.
The active feature directory is independent of the existing Git branch through
`.specify/feature.json`.

## Verified Example Calculations

With the default corpus, `chunk_size=140`, `overlap=30`, and `top_k=2`:

| Question | Meaningful terms | Retrieved chunk | Matches | Coverage | Decision |
|---|---|---|---|---:|---|
| What is retrieval augmented generation? | retrieval, augmented, generation | `doc-1-chunk-0` | 3 | 1.000 | qualify |
| Same | same | `doc-2-chunk-0` | 1 | 0.333 | exclude |
| Who won the world cup in 1958? | won, world, cup, 1958 | `doc-1-chunk-0` | 0 | 0.000 | exclude |
| Same | same | `doc-3-chunk-0` | 0 | 0.000 | exclude |

The rule therefore supports only `doc-1-chunk-0` for the supported demonstration and refuses
the unsupported demonstration.

## Limitations

- This is a lexical heuristic, not semantic entailment.
- Passing the threshold does not prove that a chunk fully answers the question.
- The system cannot verify truth beyond the local corpus.
- Valid one-keyword, acronym-only, synonymous, or paraphrased questions may be refused.
- Exact excerpts may be incomplete or stylistically awkward.
- Existing tokenization is ASCII-oriented.
- The design intentionally prioritizes avoiding unsupported answers over recall.
- No artifact or evidence may claim semantic correctness is guaranteed.

## Unresolved Shared Decisions

- The final demo lead must be agreed by both contributors.
- Outcome 5, root `evidence.md`, README changes, merge strategy, and submission remain shared work.
