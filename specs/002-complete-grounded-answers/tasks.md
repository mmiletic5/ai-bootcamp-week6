# Tasks: Complete Grounded Answers

**Input**: [spec.md](spec.md), [plan.md](plan.md), and [research.md](research.md)\
**Workflow**: Strict RED -> GREEN -> REFACTOR -> VERIFY -> EVIDENCE\
**Approval**: Q001 only is authorized. Q002-Q005 remain blocked pending explicit approval.

## Q001 - Specification and Baseline Review

**Goal**: Freeze a consistent, reviewable feature definition without changing application behavior.

- [x] Q001.1 Confirm branch `feature/isidora-week6`, HEAD
  `4ca231a546592f3e7bba60e2c0f4f622379819aa`, and initial worktree state.
- [x] Q001.2 Confirm the pre-improvement full suite result `83 passed in 0.15s` and label it
  historical/planning evidence rather than post-improvement evidence.
- [x] Q001.3 Review the constitution, feature 001, implementation, tests, evidence, README,
  checklist, comparison configurations, and official assignment.
- [x] Q001.4 Record the approved answer-side approach, conservative zero-overlap policy,
  separate citations, ownership boundaries, risks, and alternatives in feature 002.
- [x] Q001.5 Create `spec.md`, `plan.md`, `research.md`, `tasks.md`, and
  `checklists/requirements.md` under `specs/002-complete-grounded-answers/`.
- [x] Q001.6 Verify cross-artifact requirement, acceptance, test, task, and evidence traceability.
- [x] Q001.7 Verify Git scope: exactly the five new planning files plus the preserved pre-existing
  untracked `docs/mateja_handoff.md`; no protected file changes.
- [x] Q001.8 Report results and stop for explicit approval before Q002.

**Q001 acceptance**: Planning artifacts contain no unresolved design decisions, use repository
conventions, and leave all pre-existing files unchanged.

**Commit boundary**: Optional planning-only commit after separate authorization; no commit now.

## Q002 - RED Tests for Complete Grounded Excerpts

**Depends on**: Q001 approval.\
**Goal**: Express the approved behavior in failing tests before application changes.

- [x] Q002.1 Update the old incomplete default API and CLI expectations in `tests/test_rag.py`.
- [x] Q002.2 Replace the retrieved-only citation-subset assertion with lexical-seed plus verified
  continuation provenance assertions.
- [x] Q002.3 Add one-hop overlap, longest/repeated overlap, and duplicate-removal tests.
- [x] Q002.4 Add zero-overlap, unrelated same-document, cross-document, wrong-order, missing
  continuation, and incomplete-source safety tests.
- [x] Q002.5 Add multi-hop, already-complete, duplicate-citation, and determinism tests.
- [x] Q002.6 Add default `(140,30)`, alternative `(80,20)`, and `training-rag` coverage.
- [x] Q002.7 Preserve and run empty, stopword-only, weak-evidence, unsupported, exact-refusal,
  invalid-`top_k`, public-interface, and non-qualifying-result regressions.
- [x] Q002.8 Run focused tests and record genuine failures caused by missing continuation behavior.
- [x] Q002.9 Review the diff to confirm only `tests/test_rag.py` changed; stop before implementation.

**RED command**:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_rag.py -q
```

**Commit boundary**: Optional test-only commit after authorization and genuine RED observation.

## Q003 - Minimal Implementation and GREEN Verification

**Depends on**: Approved Q002 with genuine RED failures.\
**Goal**: Implement only the private answer-side behavior necessary to pass the approved tests.

- [x] Q003.1 Add private source-position and terminal-sentence helpers in `src/rag.py`.
- [x] Q003.2 Add deterministic longest exact suffix/prefix word-overlap detection.
- [x] Q003.3 Add immediate same-document continuation with zero-overlap rejection.
- [x] Q003.4 Add multi-hop completion, source-use citation ordering, and global deduplication.
- [x] Q003.5 Ensure only an existing qualifying seed can trigger continuation.
- [x] Q003.6 Run focused tests to GREEN, then refactor private code without public changes.
- [x] Q003.7 Run all `tests/test_rag.py` and confirm API, refusal, and invalid-`top_k` regressions.
- [x] Q003.8 Verify only `src/rag.py` and the approved test file changed.

**GREEN commands**:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_rag.py -q
git diff --check
```

**Commit boundary**: Optional implementation/GREEN commit after authorization.

## Q004 - Complete Regression, CLI, and Integration Verification

**Depends on**: Q003 GREEN.\
**Goal**: Reproduce all behavior before documentation claims are changed.

- [x] Q004.1 Run the complete pytest suite and record the actual post-improvement result.
- [x] Q004.2 Run supported and unsupported default CLI demonstrations and capture exact output.
- [x] Q004.3 Run the `training-rag` supported demonstration and capture exact output.
- [x] Q004.4 Verify answers using `(140,30)` and `(80,20)`, including multi-hop citations.
- [x] Q004.5 Run `scripts/compare_chunking_retrieval.py` read-only and confirm Mateja's results remain stable.
- [x] Q004.6 Repeat deterministic API/CLI cases and verify identical outputs.
- [x] Q004.7 Verify refusal text, empty refusal citations, invalid `top_k`, API signatures, and CLI layout.
- [x] Q004.8 Run `git diff --check`, inspect the complete scoped diff, and verify protected files remain unchanged.

**Verification commands**:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest .\tests\test_rag.py -q
.\.venv\Scripts\python.exe -m src.cli --question "What is retrieval augmented generation?"
.\.venv\Scripts\python.exe -m src.cli --question "Who won the world cup in 1958?"
.\.venv\Scripts\python.exe -m src.cli --corpus-profile training-rag --question "Why are citations important in RAG?"
.\.venv\Scripts\python.exe .\scripts\compare_chunking_retrieval.py
git diff --check
```

**Commit boundary**: None unless verification exposes an approved in-scope defect.

## Q005 - Verified Evidence and Documentation

**Depends on**: Successful Q004 with captured outputs.\
**Goal**: Update only affected Isidora/shared documentation using observed results.

- [x] Q005.1 Update `docs/rag-evidence.md` with new supported output, adjacent-source provenance,
  actual tests, commands, risks, and limitations.
- [x] Q005.2 Update only applicable extension/readiness entries in `docs/homework-checklist.md`.
- [x] Q005.3 Update README architecture, examples, verified counts, and limitation text.
- [x] Q005.4 Update only Outcomes 3 and 5 plus verification in `docs/evidence.md`.
- [x] Q005.5 Preserve historical `83 passed`, `29 passed`, earlier RED/GREEN results, retrieval
  rankings, and Mateja's Outcome 1/2 evidence as explicitly historical facts.
- [x] Q005.6 Confirm every documented ID, output, and count was actually observed in Q004.
- [x] Q005.7 Run the full suite and demonstrations again if documentation changes depend on them.
- [x] Q005.8 Perform final traceability, ownership, Git-scope, and `git diff --check` review.

**Commit boundary**: Optional documentation-only commit after explicit authorization.

## Dependencies and Stop Gates

```text
Q001 planning + approval
  -> Q002 RED tests + review
  -> Q003 minimal GREEN implementation
  -> Q004 full verification
  -> Q005 evidence from observed results
```

No later task may start early. Q001 must stop after its report. Push, pull, merge, rebase,
cherry-pick, pull requests, and external publication are outside every task.
