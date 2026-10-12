# Week 6 Homework Checklist (RAG)

Use this checklist when preparing your submission.

## A. Baseline setup

- [x] Project installs and tests run locally.
- [x] You can run the CLI with a custom question.
- [x] You understand where chunking, retrieval, and answer behavior are implemented.

## B. Outcome 1: Explain chunking effect on retrieval quality

- [x] You ran at least two chunking configurations (for example: `chunk_size=140, overlap=30` and one alternative).
- [x] You compared retrieval output for the same question under both configurations.
- [x] You wrote a short explanation of the observed difference in retrieval quality.

## C. Outcome 2: Implement top-k retrieval pipeline

- [x] Retrieval returns top-k chunks sorted by relevance score.
- [x] You show one example output with `top_k=2` and one with `top_k=3`.
- [x] You explain how your scoring approach decides relevance.

## D. Outcome 3: Return answers with explicit citations

- [x] Supported answer includes explicit citations to chunk IDs.
- [x] Citation IDs identify the qualifying lexical seed and every verified adjacent source chunk.
- [x] Answer format clearly separates answer body and citations/references.
- [x] The default supported answer completes the source sentence without duplicated overlap text.

## E. Outcome 4: Refuse unsupported questions

- [x] For an unsupported question, the system refuses instead of generating an unsupported claim.
- [x] Refusal message is clear and consistent with grounded RAG behavior.
- [x] You explain briefly why retrieved evidence was insufficient.

## F. Outcome 5: Show supported and unsupported evidence

- [x] You provide one supported query with: question, retrieved chunks, answer, citations.
- [x] You provide one unsupported query with: question, retrieved chunks (or empty result), refusal output.
- [x] Evidence for both examples is reproducible from CLI commands or tests.

## G. Pair accountability

- [x] Pair report includes contribution of both members.
- [ ] The designated demo lead for this week is recorded.

## H. Suggested extension (optional)

- [x] Improve grounded-answer completeness and multi-source citation formatting.
- [x] Add at least 3 tests for the extension, including unsafe-continuation regressions.

## I. Submission bundle (recommended)

- [x] `docs/evidence.md` with Outcome 1-5 sections.
- [x] CLI commands used for both example queries.
- [x] Historical `83`/`29` and current `97`/`43` test snapshots are labeled separately.
- [x] Pull request #1 was merged into `develop` at commit `112c919`.
- [x] The integrated full suite was independently verified on October 12, 2026: `97 passed in 0.26s`.

## J. Remaining decisions

- [ ] Agree and record the designated demo lead.
- [ ] Submit the GitHub repository link to the professor.

