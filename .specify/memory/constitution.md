<!--
Sync Impact Report
- Version change: template -> 1.0.0
- Added principles: Strict TDD; Preserve Completed Work; Evidence Honesty;
  Minimal Grounded Design; Human Approval Gates
- Added sections: Technical Constraints; Development Workflow and Quality Gates
- Removed sections: none
- Templates reviewed: plan-template.md, spec-template.md, tasks-template.md
- Template updates: none required; feature artifacts apply the principles directly
- Deferred items: none
-->
# SITA Week 6 RAG Homework Constitution

## Core Principles

### I. Strict Test-Driven Development (NON-NEGOTIABLE)
Every behavior change MUST follow RED -> GREEN -> REFACTOR -> VERIFY. A test MUST be
written and observed failing for the intended reason before implementation begins. Tests
MUST NOT be weakened to conceal a defect. Focused tests and the full regression suite MUST
pass before evidence is recorded.

### II. Preserve Completed Work and Interfaces
Mateja's completed chunking and retrieval implementation, tests, and evidence MUST remain
unchanged unless a demonstrated integration defect receives explicit approval. Existing
public call signatures and observable CLI arguments MUST remain compatible. Unrelated user
changes and untracked files MUST be preserved.

### III. Evidence Honesty and Reproducibility
Documentation MUST contain only commands, outputs, scores, citations, and test results that
were actually observed. Every completed requirement MUST trace to an acceptance criterion,
an automated test, an implementation task, and reproducible evidence. Planned results MUST
be clearly distinguished from verified results.

### IV. Minimal Grounded Design
The implementation MUST use the existing local corpus and lexical retrieval pipeline. It
MUST prefer the smallest deterministic solution satisfying the homework and MUST NOT add
external language models, embeddings, vector databases, APIs, or speculative generation.
Lexical grounding limitations MUST be stated without claiming semantic correctness.

### V. Human Approval Gates
Planning artifacts MUST be reviewed before application implementation. Material scope,
architecture, branch, integration, or requirement changes MUST stop for explicit approval.
Merges, rebases, pushes, pull requests, and commits MUST NOT occur without authorization.

## Technical Constraints

- Python and pytest already configured in `.venv` are the required runtime and test tools.
- Windows PowerShell commands MUST use `.venv\Scripts\python.exe`.
- The pipeline remains Corpus -> Chunking -> Retrieval -> RAG Answer -> Citation/Refusal -> CLI.
- Citation IDs MUST originate from retrieved chunks; refusals MUST contain no claims or citations.
- Outcome 5 remains shared work and MUST NOT be complete before integrated evidence is reproduced.

## Development Workflow and Quality Gates

1. Freeze `spec.md`, `plan.md`, and `tasks.md` before implementation.
2. Execute tasks in dependency order with the mandated TDD cycle.
3. Review the scoped diff and run focused tests after each logical phase.
4. Run the full suite before recording evidence.
5. Mark tasks and homework checklist items complete only after verification.
6. Preserve contributor-specific evidence and defer shared submission changes to integration.

## Governance

This constitution governs feature specifications, implementation plans, and task execution.
Amendments require explicit contributor approval, a documented rationale, an updated Sync
Impact Report, and semantic versioning: MAJOR for incompatible governance changes, MINOR for
new or expanded principles, and PATCH for clarifications. Every review MUST verify compliance
before proceeding to the next approval gate.

**Version**: 1.0.0 | **Ratified**: 2026-10-11 | **Last Amended**: 2026-10-11
