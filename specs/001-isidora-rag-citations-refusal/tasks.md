# Tasks: Grounded RAG Citations and Refusal

**Input**: `spec.md`, `plan.md`, and `research.md` in this feature directory
**Workflow**: RED -> GREEN -> REFACTOR -> VERIFY -> EVIDENCE -> COMMIT
**Authorization**: T001-T004 are complete. T005-T006 are authorized for Implementation Session 2;
T007 and later tasks remain unauthorized in this session.

## Phase 1: Specification Setup and Mandatory Review Gate

- [x] T001 Initialize official Spec Kit and validate the planning package in `.specify/`,
  `.agents/`, and `specs/001-isidora-rag-citations-refusal/`.
  - **Requirements/acceptance**: planning persistence, full traceability, preservation, and the
    explicit approval gate defined by the constitution and plan.
  - **Dependencies**: initial plan approval only.
  - **Files**: only authorized Spec Kit infrastructure and this feature specification directory.
  - **Actions**: install/check pinned Spec Kit 0.12.11; initialize Codex/PowerShell support;
    run constitution, specify, clarify, plan, checklist, tasks, and read-only analyze workflow;
    compare handoff hashes; inspect status and scoped diff.
  - **Verification**:
    `Get-ChildItem .\specs\001-isidora-rag-citations-refusal -Recurse -File`;
    `Get-FileHash .\docs\mateja_handoff.md -Algorithm SHA256`;
    `git diff --check`; `git diff -- src tests docs README.md requirements.txt`.
  - **Evidence**: report generated paths, infrastructure, hash comparison, status, analysis
    metrics/findings, and unresolved risks.
  - **Complete when**: artifacts exist, traceability is complete, no application/shared file
    changed, no commit exists, and work stops for Isidora's review.
  - **Commit boundary**: none; committing is prohibited before separate authorization.

## Mandatory Approval Checkpoint

**STOP after T001.** Do not execute T002 or modify application code, tests, existing documentation,
or Git history until Isidora explicitly approves the actual artifacts.

## Phase 2: Reconfirm Baseline

- [x] T002 Reconfirm the approved implementation baseline without file changes.
  - **Requirements/acceptance**: NFR-002, SC-004.
  - **Dependencies**: T001 complete plus explicit approval of actual Markdown artifacts.
  - **Files**: none.
  - **Verification**: `git status --short --branch`; `git log --oneline --decorate -4`;
    `.\.venv\Scripts\python.exe -m pytest -q`.
  - **Expected**: Mateja commits present and the pre-implementation suite reports 56 passing tests;
    any discrepancy stops execution.
  - **Observed baseline (2026-10-12)**: branch `feature/isidora-week6`, HEAD `f995412` before
    planning commits, handoff hash unchanged, and `56 passed in 0.12s`.
  - **Evidence**: retain actual output for later documentation.
  - **Complete when**: baseline and ownership boundaries are reconfirmed.
  - **Commit boundary**: none.

## Phase 3: User Story 1 - Grounded Answers and Citations (P1, MVP)

**Independent test**: the approved supported query cites only qualifying `doc-1-chunk-0`.

- [x] T003 [US1] Write and run RED Outcome 3 tests in `tests/test_rag.py`.
  - **Requirements/acceptance**: R3.1/AC3.1, R3.2/AC3.2, R3.3/AC3.3, R3.4/AC3.4.
  - **Dependencies**: T002.
  - **Test first**: exact excerpt, inline citation, exact citation list, unrelated-result exclusion,
    citation/retrieval relationship, duplicate-ID suppression, determinism, `top_k=1`, and current
    API shape.
  - **RED command**: `.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q`.
  - **Expected RED**: starter behavior cites a non-qualifying result and fails exact formatting or
    deduplication assertions; pre-existing assertions continue to run.
  - **Observed RED (2026-10-12)**: `4 failed, 4 passed in 0.11s`; failures covered exact
    extractive formatting, qualifying-only citations, weak-result exclusion, and duplicate-ID
    suppression. Determinism, `top_k=1`, public API shape, and the existing refusal test passed.
  - **Evidence**: capture failing test names and reasons without recording them as final results.
  - **Complete when**: failures demonstrate approved gaps rather than test mistakes.
  - **Suggested future commit**: `test: specify grounded answer and citation behavior`.

- [x] T004 [US1] Implement, refactor, and verify Outcome 3 in `src/rag.py`.
  - **Requirements/acceptance**: R3.1-R3.4, NFR-001-NFR-003.
  - **Dependencies**: T003 with observed relevant RED failures.
  - **GREEN**: add private meaningful-term and per-result qualification helpers; retrieve once;
    render exact qualifying text with inline IDs; build matching deduplicated citations in order;
    preserve the public API.
  - **REFACTOR**: remove duplication and use `src.retrieval.tokenize`; do not alter retrieval.
  - **Verification**: `.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q`;
    `.\.venv\Scripts\python.exe -m pytest tests\test_retrieval.py tests\test_chunking.py -q`;
    `git diff --check`.
  - **Expected GREEN**: all Outcome 3 and Mateja regression tests pass.
  - **Observed GREEN (2026-10-12)**: RAG `8 passed in 0.04s`; retrieval/chunking
    `51 passed in 0.07s`; full suite `62 passed in 0.09s`; `git diff --check` passed.
  - **Evidence**: retain the actual supported result for T008.
  - **Complete when**: only qualifying retrieved text and IDs appear and Mateja files are unchanged.
  - **Suggested future commit**: `feat: enforce grounded extractive answers and citations`.

## Phase 4: User Story 2 - Unsupported-Question Refusal (P2)

**Independent test**: the approved World Cup query refuses with no citations.

- [x] T005 [US2] Write and run Outcome 4 tests in `tests/test_rag.py`.
  - **Requirements/acceptance**: R4.1/AC4.1 through R4.5/AC4.5.
  - **Dependencies**: T004.
  - **Test first**: empty/whitespace question, empty chunks, no match, stopword false positive,
    one meaningful match, two matches below 50%, exact 50% boundary, no meaningful terms,
    refusal safety, and invalid `top_k` propagation.
  - **RED command**: `.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q`.
  - **Expected RED**: weak positive matches answer instead of refusing before the evidence gate exists.
  - **Observed result (2026-10-12)**: `24 passed in 0.09s`. All 16 added test cases passed
    immediately because T004 had already introduced the shared evidence-qualification logic.
    The new coverage verifies empty and whitespace questions, empty chunks, no results,
    stopword/common-word false positives, one distinct match, both sides of the 50% boundary,
    duplicate query terms, exact safe refusal output, invalid `top_k`, and supported regression.
    No RED failure was manufactured and no application change was needed.
  - **Evidence**: capture relevant failures only.
  - **Complete when**: boundary and false-positive failures directly map to R4 requirements.
  - **Suggested future commit**: `test: specify unsupported question refusal`.

- [ ] T006 [US2] Implement, refactor, and verify Outcome 4 in `src/rag.py`.
  - **Requirements/acceptance**: R4.1-R4.5, NFR-001-NFR-003.
  - **Dependencies**: T005 with observed relevant RED failures.
  - **GREEN**: apply the exact stopword set, two-distinct-term minimum, and coverage `>= 0.50`;
    return only the existing exact refusal when no chunk qualifies; preserve retrieval errors.
  - **REFACTOR**: share qualification logic with Outcome 3 and keep helpers private.
  - **Verification**: `.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q`;
    `.\.venv\Scripts\python.exe -m pytest -q`; `git diff --check`.
  - **Expected GREEN**: all focused and full tests pass, including World Cup refusal.
  - **Evidence**: retain actual unsupported retrieval and refusal for T008.
  - **Complete when**: every insufficient path has no excerpt, claim, or citation.
  - **Suggested future commit**: `feat: reject insufficient RAG evidence`.

## Phase 5: User Story 3 - CLI and Individual Evidence (P3)

**Independent test**: supported and unsupported CLI results match automated behavior.

- [ ] T007 [US3] Test and minimally correct CLI integration in `tests/test_rag.py` and, only if
  demonstrated necessary, `src/cli.py`.
  - **Requirements/acceptance**: R3.3/AC3.3 and R5.1/AC5.1.
  - **Dependencies**: T006.
  - **Test first**: call `main()` with patched arguments and capture supported/unsupported output.
  - **RED/GREEN**: observe a relevant failure before any CLI edit; retain all flags and defaults;
    do not add duplicate retrieval or new arguments.
  - **Verification**: `.\.venv\Scripts\python.exe -m pytest tests\test_rag.py -q`;
    `.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"`;
    `.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"`.
  - **Evidence**: capture exact CLI outputs.
  - **Complete when**: Answer, Refused, and Citations are deterministic and clearly separated.
  - **Suggested future commit**: `test: verify RAG CLI output`, plus a feature commit only if needed.

- [ ] T008 [US3] Verify and document individual evidence in `docs/rag-evidence.md` and verified
  Outcome 3/4 items only in `docs/homework-checklist.md`.
  - **Requirements/acceptance**: D1/AC-D1 and verified R3/R4 behavior.
  - **Dependencies**: T007.
  - **VERIFY**: rerun every command before recording scope, starting baseline, implementation,
    supported retrieval/text/answer/citations, unsupported retrieval/refusal, focused/full tests,
    limitations, and integration handoff.
  - **EVIDENCE**: use actual output only; distinguish lexical grounding from semantic correctness.
  - **Verification**: reproduce all documented commands and compare documentation to output.
  - **Complete when**: every evidence statement is traceable and only verified checklist items change.
  - **Suggested future commit**: `docs: add RAG evidence and update homework checklist`.

## Phase 6: Cross-Cutting Verification

- [ ] T009 Complete regression and integration-readiness review across `src/rag.py`, optional
  `src/cli.py`, `tests/test_rag.py`, `docs/rag-evidence.md`, and `docs/homework-checklist.md`.
  - **Requirements/acceptance**: SC-003-SC-005 and NFR-001-NFR-004.
  - **Dependencies**: T008.
  - **Verification**: focused RAG tests; full pytest; `git diff --check`; `git status --short`;
    scoped diff; handoff hash; confirm Mateja-owned source, tests, and evidence unchanged.
  - **Evidence**: record actual final counts and any authorized commit references.
  - **Complete when**: tests, traceability, evidence, ownership, and diff hygiene all pass.
  - **Commit boundary**: only explicitly authorized corrections or logical phase commits.

## Phase 7: Shared Integration and Submission (Planned Only)

- [ ] T010 Plan and later execute shared Outcome 5 integration in `evidence.md`, `README.md`, and
  remaining `docs/homework-checklist.md` items.
  - **Requirements/acceptance**: R5.1 plus all five instructor outcomes.
  - **Dependencies**: T009, Mateja coordination, and separate authorization.
  - **Actions**: integrate through updated `develop`; verify all outcomes; reproduce both CLI cases;
    create the exact five-section root evidence; add Windows setup/testing/evidence guidance,
    contributor attribution, and agreed demo lead.
  - **Verification**: full integrated suite, CLI reproduction, checklist and diff review.
  - **Evidence**: root evidence only after genuine integrated verification.
  - **Complete when**: Outcome 5 is reproduced and submission materials are review-ready.
  - **Restrictions**: no merge, rebase, push, PR, or completion claim without authorization.
  - **Suggested future commit**: `docs: finalize Week 6 RAG submission evidence`.

## Dependencies and Execution Order

`T001 -> APPROVAL -> T002 -> T003 -> T004 -> T005 -> T006 -> T007 -> T008 -> T009 -> T010`

- T005-T006 are the only currently authorized tasks in Implementation Session 2.
- T003/T004 complete User Story 1 independently.
- T005/T006 complete User Story 2 after the shared qualification contract exists.
- T007/T008 complete User Story 3 after answer/refusal behavior is stable.
- T009 is the individual-scope release gate; T010 is separately authorized shared work.
- No tasks are marked parallel because TDD evidence and shared-file sequencing require strict order.

## Implementation Strategy

The MVP is User Story 1 after baseline approval. Deliver each story through its complete RED,
GREEN, REFACTOR, and VERIFY cycle before proceeding. Evidence follows all functional work, and
commits occur only when explicitly authorized.
