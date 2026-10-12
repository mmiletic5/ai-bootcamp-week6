# Requirements Checklist: Complete Grounded Answers

**Purpose**: Validate that feature 002 is complete, testable, traceable, and consistent with the
project constitution before Q002 begins.\
**Created**: 2026-10-12\
**Feature**: [Complete Grounded Answers](../spec.md)

## Specification Quality

- [x] CHK001 Feature 002 is explicitly a quality improvement, not a retroactive homework failure.
- [x] CHK002 Feature 001 and historical T001-T010 results are immutable.
- [x] CHK003 All requirements use mandatory, testable language without implementation ambiguity.
- [x] CHK004 Default-answer text and separate citation format are exact.
- [x] CHK005 Conservative zero-overlap behavior is explicit.
- [x] CHK006 Public API, CLI, refusal, retrieval, and ownership constraints are explicit.

## Safety and Provenance

- [x] CHK007 Initial support still requires the existing meaningful-term qualification rule.
- [x] CHK008 Source adjacency is distinguished from retrieval ranking.
- [x] CHK009 Immediate collection order, same document, and exact overlap are all required.
- [x] CHK010 Chunk IDs alone never establish adjacency.
- [x] CHK011 Longest exact overlap and repeated-word behavior are deterministic.
- [x] CHK012 Every contributing source is cited once in first-use order.
- [x] CHK013 Adjacency cannot bypass refusal or fabricate missing content.

## Test and Evidence Coverage

- [x] CHK014 Default, multi-hop, complete, and incomplete source cases are specified.
- [x] CHK015 Zero-overlap, unrelated, out-of-order, and cross-document cases are specified.
- [x] CHK016 Refusal, empty/stopword-only, invalid-`top_k`, duplicate, API, and determinism
  regressions are specified.
- [x] CHK017 Both Outcome 1 configurations and `training-rag` are included.
- [x] CHK018 Historical and post-improvement evidence are required to remain separate.
- [x] CHK019 Requirements map to acceptance coverage, Q-tasks, and evidence destinations.

## Governance and Scope

- [x] CHK020 Strict RED -> GREEN -> REFACTOR -> VERIFY -> EVIDENCE ordering is mandatory.
- [x] CHK021 Q001 is the only authorized task and includes a stop gate before Q002.
- [x] CHK022 No new dependency, external service, corpus change, or public model change is planned.
- [x] CHK023 Mateja-owned files, feature 001, and `docs/mateja_handoff.md` are protected.
- [x] CHK024 No commit, push, pull, merge, rebase, cherry-pick, PR, or publication is authorized.

## Q001 Exit Review

- [x] CHK025 Exactly five feature-002 planning files are newly created.
- [x] CHK026 Cross-artifact terminology and requirement IDs are consistent.
- [x] CHK027 Git scope contains no unexpected or protected-file changes.
- [x] CHK028 Q001 completion is reported and execution stops before Q002.
