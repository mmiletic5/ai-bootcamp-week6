# Feature Specification: Complete Grounded Answers

**Feature Branch**: `feature/isidora-week6`\
**Created**: 2026-10-12\
**Status**: Planned - Q001 complete; implementation awaiting approval\
**Input**: Improve supported extractive answers by safely completing a sentence across verified adjacent chunks without changing retrieval, refusal, or CLI contracts.

## Relationship to Completed Feature 001

`specs/001-isidora-rag-citations-refusal/` is an approved historical record of the completed
Week 6 Outcome 3 and Outcome 4 implementation. Its behavior was correct for the homework:
supported answers copied qualifying retrieved chunks exactly, citations were valid, and weak
evidence caused the exact refusal. This feature is a separately approved quality improvement
because a real chunk boundary can leave that correct extractive output hard to read. It does
not retroactively classify feature 001 or T001-T010 as failing, and feature 001 must not be
edited.

The historical pre-improvement snapshot is `83 passed`. It remains historical evidence and
must not be overwritten or presented as a new post-improvement result.

## User Scenarios & Testing

### User Story 1 - Complete a Verified Grounded Sentence (Priority: P1)

As a reviewer, I want a supported answer to continue through genuinely adjacent source chunks
until its current sentence is complete, so that the answer remains verbatim and becomes useful
to a reader.

**Independent Test**: Ask `What is retrieval augmented generation?` over the default corpus
with `chunk_size=140`, `overlap=30`, and `top_k=2`. The single bullet ends with
`unsupported assumptions.` and cites `doc-1-chunk-0` and `doc-1-chunk-1` separately.

**Acceptance Scenarios**:

1. **Given** a qualifying retrieved seed ending mid-sentence and its immediate same-document
   source neighbor has an exact suffix/prefix overlap, **When** the answer is built, **Then**
   append only the non-overlapping continuation through the sentence terminator.
2. **Given** more than one successive verified neighbor is required, **When** each boundary
   passes the same checks, **Then** continue in original collection order and cite every used chunk.
3. **Given** a seed already ending in `.`, `?`, or `!`, **When** the answer is built, **Then**
   do not add a continuation.
4. **Given** overlapping repeated words, **When** multiple suffix/prefix lengths match, **Then**
   use the longest exact word overlap deterministically and emit the overlap once.

### User Story 2 - Refuse Unsafe Continuation (Priority: P1)

As a reviewer, I want continuation to require verified source adjacency so that unrelated text
is never joined merely because it ranked nearby or has a convenient chunk ID.

**Independent Test**: Supply an incomplete qualifying seed followed by zero-overlap,
same-document, different-document, and unrelated candidates. None is appended; the supported
seed remains exact and no continuation citation is added.

**Acceptance Scenarios**:

1. **Given** the next retrieval-ranked result is unrelated, **Then** retrieval rank does not
   make it a continuation.
2. **Given** a collection neighbor belongs to another document, **Then** it is not appended.
3. **Given** a same-document neighbor has no non-empty exact boundary overlap, **Then** it is
   not appended, even when its chunk ID appears consecutive.
4. **Given** a genuinely incomplete final source chunk, **Then** return its exact supported
   text without invented continuation or punctuation.
5. **Given** no seed passes the existing evidence gate, **Then** adjacency is not inspected to
   create support and the exact refusal is returned with no citations.

### User Story 3 - Preserve Interfaces and Reproducible Evidence (Priority: P2)

As a project contributor, I want the improvement to preserve the public API, CLI layout,
retrieval behavior, and historical evidence so that the completed homework remains auditable.

**Independent Test**: Run focused and full tests plus the approved CLI demonstrations; verify
the existing sections and errors remain unchanged while new outputs and test totals are recorded
separately from historical results.

**Acceptance Scenarios**:

1. The CLI retains `Question:`, `Answer:`, `Grounded answer:`, bullet formatting,
   `Corpus profile:`, `Refused:`, and `Citations:`.
2. `RagAnswer` and `build_grounded_answer(question, chunks, top_k=2)` retain their public shape.
3. Invalid `top_k` values retain the retriever's current exception types and messages.
4. The default and `training-rag` profiles and both Outcome 1 configurations `(140,30)` and
   `(80,20)` behave deterministically.
5. Documentation labels `83 passed` and `29 passed` as historical pre-improvement snapshots and
   records post-improvement results only after they are actually observed.

## Requirements

### Functional Requirements

- **CGA-001**: Initial support MUST still come only from unique ranked results satisfying the
  existing meaningful-term qualification rule.
- **CGA-002**: Continuation MUST use the original ordered `chunks` collection, not retrieval rank.
- **CGA-003**: A continuation candidate MUST be the immediate collection neighbor and have the
  same `doc_id` as the current source chunk.
- **CGA-004**: Every joined boundary MUST have a non-empty exact word-sequence overlap between
  the current chunk suffix and candidate prefix.
- **CGA-005**: Joining MUST use the longest exact overlap and MUST append only the candidate's
  non-overlapping words.
- **CGA-006**: Continuation MUST stop when the assembled excerpt ends in `.`, `?`, or `!`, or
  when any adjacency check fails.
- **CGA-007**: Zero-overlap boundaries MUST NOT be joined. No source offsets, punctuation, words,
  or other missing content may be invented.
- **CGA-008**: Every contributing chunk MUST be cited once, in first-use source order, using
  separate brackets in the bullet and the same ordered IDs in `RagAnswer.citations`.
- **CGA-009**: A chunk already consumed as continuation MUST NOT be emitted again as a duplicate
  bullet or duplicate citation.
- **CGA-010**: Continuation MUST NOT cause a non-qualifying question or chunk to bypass refusal.
- **CGA-011**: The exact refusal message, `refused=True`, and empty citations MUST remain unchanged
  whenever initial evidence is insufficient.
- **CGA-012**: Retrieval ordering, scoring, top-k selection, and validation MUST remain unchanged.
- **CGA-013**: The public RAG API and observable CLI arguments and section organization MUST remain
  compatible.
- **CGA-014**: Behavior MUST be deterministic for identical ordered inputs.
- **CGA-015**: The implementation MUST remain local and dependency-free and MUST NOT modify
  Mateja-owned chunking or retrieval work.
- **CGA-016**: Historical verification results MUST remain distinguishable from newly executed
  post-improvement results.

### Key Entities

- **Qualifying seed**: A unique lexical retrieval result passing the existing evidence rule.
- **Source neighbor**: The immediate next chunk in the caller-provided ordered collection.
- **Verified continuation**: A same-document source neighbor with a non-empty exact boundary overlap.
- **Completed excerpt**: Exact source words assembled from a seed and zero or more verified continuations.
- **Source-use citations**: Deduplicated chunk IDs in the order their text first contributes.

## Success Criteria

- **SC-001**: The default supported answer exactly ends `unsupported assumptions.` and cites
  `[doc-1-chunk-0] [doc-1-chunk-1]`.
- **SC-002**: No test joins a zero-overlap, unrelated, out-of-order, or cross-document chunk.
- **SC-003**: Overlapping words occur once across every joined boundary.
- **SC-004**: All refusal, invalid-`top_k`, public-interface, determinism, corpus-profile, and
  existing regression tests pass.
- **SC-005**: Every requirement maps to acceptance coverage, a Q-task, and an evidence destination.
- **SC-006**: Final scoped-diff review confirms Mateja-owned files and feature 001 are unchanged.

## Assumptions and Scope Boundaries

- The caller-provided chunk list is the authoritative source order, but order alone is insufficient
  to permit a join; document identity and exact overlap are also required.
- Validated source-neighbor continuation is a deterministic secondary retrieval step. It is
  distinct from lexical top-k ranking and satisfies the constitution's provenance requirement.
- Sentence completion uses only trailing `.`, `?`, or `!`; broader linguistic parsing is out of scope.
- Adding offsets to `Chunk`, changing chunk generation, modifying retrieval, external models,
  embeddings, semantic entailment, and corpus expansion are out of scope.
- Q002-Q005 require separate explicit approval after Q001 review.
