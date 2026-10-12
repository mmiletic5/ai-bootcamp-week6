# Implementation Plan: Grounded RAG Citations and Refusal

**Branch**: `feature/isidora-week6` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary

Implement Outcomes 3 and 4 with a conservative lexical evidence gate at the RAG layer. Supported
answers remain extractive and cite only qualifying retrieved chunks. Insufficient, empty, or weak
evidence produces the existing exact refusal. Work follows strict TDD and preserves Mateja's
chunking/retrieval implementation and all existing public interfaces.

## Technical Context

**Language/Version**: Existing local Python 3.10 environment
**Primary Dependencies**: Python standard library and existing project modules only
**Storage**: In-memory static corpus; no persistence change
**Testing**: pytest 8.3.3 via `.venv\Scripts\python.exe`
**Target Platform**: Local Windows PowerShell CLI
**Project Type**: Small Python library and CLI
**Performance Goals**: Preserve current small-corpus linear behavior; no new external I/O
**Constraints**: Offline, deterministic, no LLM/embedding/vector dependencies, compatible API
**Scale/Scope**: Outcomes 3 and 4 over existing corpus profiles and retrieval results

## Constitution Check

### Pre-design gate

- **Strict TDD**: PASS; tasks separate RED tests from GREEN implementation.
- **Preservation**: PASS; no planned changes to Mateja-owned source/tests/evidence.
- **Evidence honesty**: PASS; documentation follows successful full verification only.
- **Minimal design**: PASS; private RAG helpers reuse current tokenizer and retriever.
- **Approval gates**: PASS; T001 ends with mandatory review before T002.

### Post-design gate

PASS. The design adds no dependencies, public API changes, persistence, or speculative generation.

## Technical Design

### Evidence qualification

In `src/rag.py`, add private helpers that:

1. Normalize the question with `src.retrieval.tokenize`.
2. Remove the frozen stopword set defined in [research.md](research.md).
3. Compare distinct meaningful terms with distinct tokens from each retrieved chunk.
4. Qualify a chunk only for at least two matches and coverage `>= 0.50`.
5. Preserve retrieval order and skip repeated qualifying chunk IDs.

`build_grounded_answer` retrieves once with the current `retrieve_top_k`. If no unique result
qualifies, it returns `RagAnswer(REFUSAL_MESSAGE, [], True)`. Otherwise it renders:

```text
Grounded answer:
- <exact qualifying chunk text> [<chunk-id>]
```

`RagAnswer`, `REFUSAL_MESSAGE`, function parameters, and error propagation remain unchanged.

### CLI integration

The current CLI arguments and defaults remain unchanged. Tests call `main()` using patched
arguments and captured output. Change `src/cli.py` only if those tests demonstrate a formatting
gap; do not add flags or duplicate retrieval.

### Data flow

```text
question + chunks + top_k
  -> retrieve_top_k
  -> meaningful query terms
  -> per-result match count and coverage
  -> qualifying unique results
  -> extractive cited answer OR exact refusal
  -> existing CLI sections
```

## Project Structure

```text
src/
  rag.py                  # evidence qualification and answer/refusal behavior
  cli.py                  # modify only if a failing CLI contract test requires it
tests/
  test_rag.py             # all new unit, boundary, and CLI tests
docs/
  rag-evidence.md         # individual evidence after verification
  homework-checklist.md   # verified Outcome 3/4 items only
specs/001-isidora-rag-citations-refusal/
  spec.md
  plan.md
  research.md
  tasks.md
  checklists/requirements.md
```

## TDD and Verification Strategy

1. Reconfirm the baseline after artifact approval.
2. RED Outcome 3 tests; observe relevant failures.
3. GREEN minimal extractive citation implementation; REFACTOR private helpers.
4. RED Outcome 4 tests; observe weak-match failures.
5. GREEN refusal qualification; REFACTOR without changing public interfaces.
6. RED/GREEN CLI integration only as needed.
7. VERIFY focused tests, full suite, diff hygiene, and file ownership.
8. EVIDENCE with actual outputs only.
9. COMMIT only after explicit authorization.

## Automated Test Matrix

| Test scenario | Requirement | Expected behavior |
|---|---|---|
| Supported default query | R3.1 | Exact qualifying excerpt only |
| Inline citation and list | R3.2 | Same real ID in body/list |
| Weak second result | R3.2 | Omitted from answer/citations |
| Repeat call | R3.3 | Equal result |
| Existing call shape and `top_k=1` | R3.4 | Compatible behavior |
| Duplicate chunk ID | R3.2 | Emitted once |
| Empty/whitespace query | R4.1 | Exact refusal, no citations |
| Empty chunks/no result | R4.1 | Exact refusal, no citations |
| World Cup stopword trap | R4.2 | Refusal |
| One meaningful match | R4.2 | Refusal |
| Two matches below 50% | R4.3 | Refusal |
| Two matches at 50% | R4.3 | Supported boundary |
| No meaningful terms | R4.2 | Refusal |
| Refusal safety | R4.4 | No excerpt/claim/citation |
| Invalid `top_k` | R4.5 | Existing error propagates |
| Supported/unsupported CLI | R5.1 | Deterministic separated output |
| Full suite | NFR-002/SC-004 | All tests pass; Mateja files unchanged |

## Traceability Matrix

| Requirement | Acceptance | Automated coverage | Tasks | Evidence |
|---|---|---|---|---|
| R3.1 | AC3.1 | Exact excerpt | T003-T004 | Supported output |
| R3.2 | AC3.2 | Inline/list/subset/dedup | T003-T004 | Retrieved vs cited IDs |
| R3.3 | AC3.3 | Determinism and CLI | T003, T007 | CLI transcript |
| R3.4 | AC3.4 | API shape and regression | T003, T009 | Full suite |
| R4.1 | AC4.1 | Empty query/chunks/no result | T005-T006 | Refusal cases |
| R4.2 | AC4.2 | Stopword/one-match/no-terms | T005-T006 | Weak-match explanation |
| R4.3 | AC4.3 | Below/exact boundary | T005-T006 | Coverage calculation |
| R4.4 | AC4.4 | Refusal safety | T005-T006 | Actual refusal |
| R4.5 | AC4.5 | Invalid `top_k` | T005-T006 | Regression output |
| R5.1 | AC5.1 | CLI tests | T007, T010 | Reproducible commands |
| D1 | AC-D1 | Documentation cross-check | T008-T009 | Individual evidence |
| NFR-001 | local/minimal | dependency/diff review | T004, T006, T009 | Diff record |
| NFR-002 | preservation | full regression/hash review | T002, T009 | Handoff notes |
| NFR-003 | TDD | observed RED/GREEN | T003-T009 | Test log |
| NFR-004 | honest limitations | documentation review | T008-T010 | Limitations section |

## Evidence and Integration

`docs/rag-evidence.md` will record the verified starting baseline, Outcome 3 tests and supported
output, retrieved/cited IDs, Outcome 4 tests and unsupported output, exact PowerShell commands,
real results, limitations, and handoff notes. Only verified Outcome 3/4 checklist items may change.

Shared Outcome 5 work is planned in T010 but requires separate team authorization. It includes
integrated regression, root `evidence.md`, README, contributor attribution, demo lead, final
checklist, and `develop` integration. No push, merge, rebase, or PR is implied.

## Risks and Limitations

- Lexical qualification is not semantic entailment and cannot guarantee correctness.
- Passing the threshold may still leave a question only partially answered.
- Conservative thresholds may refuse valid short, acronym, synonym, or paraphrase queries.
- Exact excerpts trade fluency for provenance.
- Tokenization remains ASCII-oriented.
- The current corpus and stable chunk identifiers are assumed.

## Approval Gate

T001 ends after these artifacts pass consistency analysis. T002 and all application changes,
test changes, evidence changes, and commits require a new explicit approval.
