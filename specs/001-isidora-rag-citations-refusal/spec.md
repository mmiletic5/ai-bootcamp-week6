# Feature Specification: Grounded RAG Citations and Refusal

**Feature Branch**: `feature/isidora-week6`
**Created**: 2026-10-11
**Status**: Planning Review
**Input**: Outcomes 3 and 4 of the SITA Week 6 RAG homework: return grounded answers
with explicit chunk citations and refuse questions when evidence is insufficient.

## User Scenarios & Testing

### User Story 1 - Grounded Answer with Valid Citations (Priority: P1)

As a homework reviewer, I want every supported answer to quote retrieved corpus evidence and
identify its source chunks so that I can verify the answer against retrieval output.

**Why this priority**: Outcome 3 establishes the grounding contract used by refusal behavior.

**Independent Test**: Ask `What is retrieval augmented generation?` with default settings.
The answer quotes only qualifying `doc-1-chunk-0`, cites it once, and excludes weak result
`doc-2-chunk-0`.

**Acceptance Scenarios**:

1. **Given** one sufficiently supported retrieved result, **When** an answer is built, **Then**
   the output reproduces only that chunk's exact text and citation ID.
2. **Given** additional non-qualifying results, **When** an answer is built, **Then** those
   chunks do not appear in the answer or citations.
3. **Given** identical inputs, **When** the operation is repeated, **Then** the result is identical.
4. **Given** duplicate qualifying chunk IDs, **When** citations are rendered, **Then** each
   excerpt and ID is emitted once in retrieval order.

---

### User Story 2 - Refusal for Insufficient Evidence (Priority: P2)

As a user, I want unsupported questions to receive a clear refusal without claims or citations
so that weak lexical overlap is not misrepresented as factual support.

**Why this priority**: Outcome 4 prevents the starter's false-answer behavior and depends on
the qualification contract from User Story 1.

**Independent Test**: Ask `Who won the world cup in 1958?` over the default corpus. Common words
may retrieve chunks, but none matches meaningful terms, so the result is the exact refusal,
no citations, and `refused=True`.

**Acceptance Scenarios**:

1. **Given** an empty or whitespace-only question, **When** an answer is requested, **Then**
   the system refuses with no citations.
2. **Given** empty chunks or no results, **When** an answer is requested, **Then** it refuses.
3. **Given** only stopword overlap or fewer than two meaningful matches per chunk, **When**
   an answer is requested, **Then** it refuses.
4. **Given** two meaningful matches below half of all meaningful query terms, **When** an
   answer is requested, **Then** it refuses.
5. **Given** invalid `top_k`, **When** an answer is requested, **Then** retrieval validation
   errors propagate instead of becoming refusals.

---

### User Story 3 - Reproducible CLI and Evidence (Priority: P3)

As a contributor or reviewer, I want deterministic supported and unsupported CLI demonstrations
and contributor-specific evidence so that Outcomes 3 and 4 can be reproduced and graded.

**Why this priority**: Evidence is meaningful only after the behavior is correct and tested.

**Independent Test**: Run the two approved PowerShell CLI commands and confirm their outputs
agree with automated tests and recorded evidence.

**Acceptance Scenarios**:

1. **Given** the supported example, **When** the CLI runs, **Then** Answer, Refused, and Citations
   are separate and show only valid citations.
2. **Given** the unsupported example, **When** the CLI runs, **Then** it prints the exact refusal,
   `Refused: True`, and `Citations: None`.
3. **Given** completed verification, **When** evidence is written, **Then** it contains only
   genuine commands and observed outputs.

### Edge Cases

- Empty, whitespace-only, or stopword-only questions.
- Empty chunks and retrieval with no positive matches.
- Positive scores produced only by common question words.
- One meaningful match, regardless of positive score.
- Exactly two matches at 50% coverage and two matches below that boundary.
- Repeated query tokens and duplicate qualifying chunk IDs.
- `top_k=1`, values larger than the eligible corpus, and invalid values.
- Multiple qualifying chunks whose order follows deterministic retrieval ranking.

## Requirements

### Functional Requirements

- **R3.1**: Non-refusal answers MUST use only exact qualifying chunk text. **AC3.1**: Every
  answer bullet reproduces qualifying text without adding factual prose.
- **R3.2**: Citations MUST be explicit and valid. **AC3.2**: Every bullet ends in `[chunk-id]`;
  the citation list exactly matches emitted qualifying IDs in retrieval order without unrelated
  or duplicate IDs.
- **R3.3**: Output MUST be deterministic and clear. **AC3.3**: Identical inputs produce equal
  `answer`, `citations`, and `refused`; CLI sections remain separate.
- **R3.4**: Public interfaces MUST remain compatible. **AC3.4**: The three-field `RagAnswer` and
  `build_grounded_answer(question, chunks, top_k=2)` retain their existing shape.
- **R4.1**: Missing evidence MUST cause refusal. **AC4.1**: Empty/whitespace questions, empty
  chunks, or no results return the exact refusal, `[]`, and `refused=True`.
- **R4.2**: Weak overlap MUST be insufficient. **AC4.2**: Stopword-only overlap or fewer than
  two distinct meaningful matches in every result causes refusal.
- **R4.3**: Meaningful coverage MUST be sufficient. **AC4.3**: A qualifying chunk matches at
  least two distinct meaningful terms and at least 50% of all distinct meaningful query terms.
- **R4.4**: Refusals MUST contain no unsupported material. **AC4.4**: Refusal output contains
  only `REFUSAL_MESSAGE`, no excerpt or claim, and no citations.
- **R4.5**: Retrieval validation MUST remain authoritative. **AC4.5**: Invalid `top_k` retains
  existing `TypeError` or `ValueError` behavior.
- **R5.1**: CLI behavior MUST be reproducible. **AC5.1**: Both approved examples expose
  deterministic answer/refusal and citation states through existing arguments.
- **D1**: Evidence MUST be genuine and contributor-specific. **AC-D1**: `docs/rag-evidence.md`
  contains only outputs observed after verification and changes only verified Outcome 3/4 items.

### Non-Functional Requirements

- **NFR-001**: The feature MUST remain local, deterministic, and dependency-free beyond current
  project requirements.
- **NFR-002**: Mateja-owned code, tests, evidence, and handoff MUST remain unchanged unless an
  integration defect is demonstrated and approved.
- **NFR-003**: Work MUST follow RED -> GREEN -> REFACTOR -> VERIFY -> EVIDENCE.
- **NFR-004**: Documentation MUST NOT claim semantic correctness, factual verification, or entailment.

### Key Entities

- **Question**: Input normalized into distinct meaningful terms for evidence qualification.
- **Retrieved chunk**: Ranked corpus excerpt with stable ID, metadata, text, and score.
- **Qualifying chunk**: Retrieved chunk satisfying both evidence thresholds.
- **RAG answer**: Result containing answer text, citation IDs, and refusal state.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The supported example cites exactly `doc-1-chunk-0` and no unrelated chunk.
- **SC-002**: The World Cup example returns the exact refusal and zero citations.
- **SC-003**: Every acceptance scenario has automated coverage before evidence is completed.
- **SC-004**: The full pytest suite passes without changes to Mateja-owned files.
- **SC-005**: Every requirement maps to an acceptance criterion, test, task, and evidence location.

## Assumptions

- The current corpus, chunk IDs, and deterministic retrieval ordering remain stable.
- Precision is preferred over recall; valid one-keyword or paraphrased questions may be refused.
- Extractive output is acceptable and avoids unsupported synthesis.
- Outcome 5, root evidence, README, integration, and demo-lead selection remain shared later work.
- The missing starter ZIP is represented by the initial Git commit.

## Out of Scope

- External LLMs, embeddings, vector databases, APIs, semantic reranking, or corpus expansion.
- Modification of Mateja-owned work without separate approval.
- Claims that the lexical rule guarantees semantic correctness.
- Commits, pushes, merges, rebases, pull requests, or Outcome 5 completion during T001.
