# Implementation Plan: Complete Grounded Answers

**Branch**: `feature/isidora-week6` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary

Improve extractive answer completeness by extending an existing qualifying retrieval result
through verified adjacent source chunks. The minimal solution remains inside the RAG answer layer,
uses exact source words, requires original collection order, document identity, and exact overlap,
and preserves retrieval, refusal, API, CLI, and ownership boundaries.

## Technical Context

**Language/Version**: Existing Python 3.10 environment\
**Dependencies**: Python standard library and current project modules only\
**Storage**: Existing in-memory corpus; no persistence changes\
**Testing**: pytest 8.3.3 via `.venv\Scripts\python.exe`\
**Target**: Local library and Windows PowerShell CLI\
**Constraints**: Offline, deterministic, exact extraction, no new dependencies, no Mateja-owned edits\
**Baseline**: Historical `83 passed`; current pre-improvement HEAD `4ca231a546592f3e7bba60e2c0f4f622379819aa`

## Constitution Check

- **Strict TDD**: PASS. Q002 creates and observes focused RED tests before Q003.
- **Preserve completed work**: PASS. Feature 001 and Mateja-owned files are immutable in this plan.
- **Evidence honesty**: PASS. Historical and post-improvement results are separately labeled.
- **Minimal grounded design**: PASS. One private answer-side implementation, exact source text,
  no new dependency or external service.
- **Human approval gates**: PASS. Q001 stops for approval; later tasks require explicit authorization.
- **Citation provenance**: PASS WITH EXPLICIT INTERPRETATION. Verified adjacency is a secondary,
  deterministic source-retrieval step. Evidence will distinguish it from lexical top-k ranking.

## Technical Design

1. Call `retrieve_top_k` exactly once and apply the unchanged meaningful-term rule to choose seeds.
2. Preserve retrieval order and existing seed-ID deduplication.
3. For each seed, locate its source occurrence in the ordered input collection without parsing IDs.
4. If the excerpt lacks terminal punctuation, inspect only the immediate next list element.
5. Require the same document and the longest non-empty exact suffix/prefix word overlap.
6. Append only non-overlapping words; repeat for successive verified neighbors until the sentence
   completes or a check fails.
7. Render one bullet with separate citations for every contributing chunk. Deduplicate sources in
   first-use order and do not emit an already-consumed continuation as another bullet.
8. If no seed qualifies, return the existing exact refusal with empty citations.

The public `RagAnswer`, function signature, CLI arguments, headings, corpus profiles, retriever,
and chunker remain unchanged.

## Test Strategy

Q002 adds RED coverage in `tests/test_rag.py` for:

- Exact default answer and CLI layout.
- One-hop and multi-hop overlap completion.
- Repeated words and longest-overlap selection.
- Retrieval rank versus collection adjacency.
- Zero-overlap, unrelated same-document, different-document, out-of-order, missing, and exhausted
  continuation cases.
- Already-complete excerpts and genuinely incomplete sources.
- Source-use citation order and deduplication.
- Unsupported, empty, whitespace, stopword-only, weak evidence, and exact refusal behavior.
- Invalid `top_k`, public interfaces, determinism, `training-rag`, `(140,30)`, and `(80,20)`.

Q003 runs focused GREEN tests and the full RAG file. Q004 runs the full suite, CLI demonstrations,
comparison script, deterministic repeats, diff checks, and ownership checks.

## Traceability

| Requirement | Acceptance coverage | Tasks | Evidence destination |
|---|---|---|---|
| CGA-001 | Existing qualification regressions | Q002-Q004 | `docs/rag-evidence.md` |
| CGA-002 | Ranked-unrelated versus source-order test | Q002-Q003 | RAG evidence design notes |
| CGA-003 | Immediate-neighbor and same/cross-document tests | Q002-Q003 | RAG evidence limitations |
| CGA-004 | Exact boundary-overlap tests | Q002-Q003 | RAG evidence supported case |
| CGA-005 | Longest/repeated-overlap tests | Q002-Q003 | RAG evidence supported case |
| CGA-006 | Complete, multi-hop, and failed-boundary tests | Q002-Q004 | CLI and test transcript |
| CGA-007 | Zero-overlap and incomplete-source tests | Q002-Q004 | Known limitations |
| CGA-008 | Separate inline/list citation-order tests | Q002-Q004 | RAG and root evidence |
| CGA-009 | Consumed-continuation and duplicate-ID tests | Q002-Q004 | Focused test transcript |
| CGA-010 | Unrelated-adjacent refusal tests | Q002-Q004 | Refusal evidence |
| CGA-011 | Exact refusal and empty-citation regressions | Q002-Q004 | RAG and root evidence |
| CGA-012 | Retrieval ordering and invalid-`top_k` regressions | Q002-Q004 | Verification transcript |
| CGA-013 | API signature and CLI snapshot tests | Q002-Q004 | CLI transcript |
| CGA-014 | Repeated API and CLI determinism tests | Q002-Q004 | Verification transcript |
| CGA-015 | Dependency and scoped-diff review | Q003-Q005 | README and ownership notes |
| CGA-016 | Historical/new result labeling review | Q004-Q005 | README, root and RAG evidence |

## Expected File Scope

Implementation may change only:

- `src/rag.py`
- `tests/test_rag.py`
- `docs/rag-evidence.md`
- `docs/homework-checklist.md`
- `README.md`
- `evidence.md`

This feature's five planning artifacts are added under `specs/002-complete-grounded-answers/`.
No other file is planned to change.

## Risks and Controls

- **False continuity**: require all adjacency checks; no zero-overlap join.
- **Repeated overlap ambiguity**: choose the longest exact boundary overlap deterministically.
- **Citation confusion**: distinguish lexical seeds from adjacent-source retrieval in tests/evidence.
- **Evidence drift**: retain historical snapshots and record new results only after execution.
- **Ownership drift**: verify protected paths with Git status/diff before completing every task.
- **Scope creep**: offsets, semantic models, corpus changes, and CLI redesign remain out of scope.

## Approval and Commit Boundaries

- Q001 completes only these planning artifacts and stops for review.
- Q002-Q005 cannot begin without explicit approval.
- If commits are later authorized: use separate logical boundaries for Q001 planning, Q002 RED tests,
  Q003 implementation/GREEN, and Q005 verified documentation. No commit is authorized by this plan.
