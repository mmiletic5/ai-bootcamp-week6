# Research: Complete Grounded Answers

## Decision 1: Extend at the answer layer

**Decision**: Implement continuation privately in `src/rag.py` using the original ordered chunk
collection already passed to `build_grounded_answer`.

**Rationale**: The defect is in answer construction, not chunking or lexical ranking. This keeps
Mateja-owned modules unchanged and preserves all public call signatures.

**Alternatives rejected**:

- Increase the default chunk size: changes Outcome 1 inputs and does not solve arbitrary boundaries.
- Return the second-ranked result: retrieval rank is relevance order, not source order.
- Modify `Chunk` with offsets: safer for zero-overlap reconstruction but expands the public model
  and Mateja-owned chunking scope.
- Load original documents inside the answer builder: introduces hidden corpus coupling and fails
  for caller-provided chunks.

## Decision 2: Establish adjacency from collection position and provenance

**Decision**: Locate the exact seed occurrence in the original list, consider only the immediate
next element, require the same `doc_id`, and require a non-empty exact suffix/prefix word overlap.
Do not parse chunk IDs to infer order.

**Rationale**: Collection position distinguishes source order from retrieval rank; document
identity prevents cross-document joins; exact overlap supplies textual continuity evidence.

**Limitation**: `Chunk` has no source offsets or original-document reference. Consequently, a
zero-overlap boundary cannot be proven safe from the current API.

## Decision 3: Conservative zero-overlap policy

**Decision**: Do not join when no exact boundary overlap exists. Return the exact supported seed
or already-verified partial excerpt without adding punctuation.

**Rationale**: Trusting list order or consecutive-looking IDs could combine unrelated passages.
Conservative incompleteness is preferable to unsupported synthesis.

## Decision 4: Longest exact word overlap

**Decision**: Compare tokenized-by-whitespace word sequences and select the longest non-empty
suffix of the current chunk equal to a prefix of the next chunk. Append only the unmatched suffix.

**Rationale**: It matches the current word-aware chunker, prevents duplicated overlap words, and
resolves repeated-word matches deterministically.

**Safety note**: A shared word alone is not semantic proof. Safety comes from the conjunction of
immediate collection adjacency, matching document identity, exact boundary overlap, and an
unfinished current sentence.

## Decision 5: Complete only the active trailing sentence

**Decision**: Continue while the assembled excerpt does not end in `.`, `?`, or `!`; stop at the
first verified sentence terminator or failed boundary.

**Rationale**: This fixes the observed readability defect without expanding answers indefinitely.
Existing complete chunks remain unchanged.

## Decision 6: Cite every contributing source separately

**Decision**: Render one bullet followed by one bracket per contributing chunk, for example
`[doc-1-chunk-0] [doc-1-chunk-1]`. Return the same IDs in first-use source order, globally deduplicated.

**Rationale**: Separate citations preserve the established syntax and make every source contribution
auditable. A continuation already used by an earlier bullet is not repeated.

## Decision 7: Preserve evidence qualification and refusal

**Decision**: Run existing retrieval and meaningful-term qualification before continuation.
Only a qualifying seed can start an excerpt. Adjacency never creates initial support.

**Rationale**: This preserves Outcome 4, the exact refusal, empty refusal citations, invalid
`top_k` propagation, and precision-oriented behavior.

## Verified Baseline

- Branch: `feature/isidora-week6`
- HEAD: `4ca231a546592f3e7bba60e2c0f4f622379819aa`
- Full suite observed during planning: `83 passed in 0.15s`
- Worktree before Q001: only untracked `docs/mateja_handoff.md`
- Default `(140,30)` requires chunks 0 and 1 for completion.
- Alternative `(80,20)` requires chunks 0, 1, and 2, exercising successive continuation.
- `training-rag` contains the same class of boundary in `tr-doc-1` and requires regression coverage.

These observations are planning inputs. They are not post-improvement evidence.
