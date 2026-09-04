# Role Split and GitHub Issues

## Suggested role split
- AI / extraction: owns form parsing, structured output, validation rules, verifier logic.
- Frontend / UX: owns upload flow, guided Q&A UI, accessibility modes, review screen.
- Integration / backend: owns file handling, state storage, API wiring, and deployment glue.
- Demo / QA: owns test forms, evaluation cases, bug triage, and presentation polish.

## Issue 1: Build form upload and extraction pipeline
- Labels: `ai`, `backend`
- Owner: AI / extraction
- Goal: accept a PDF or pasted form text and extract the field/rule structure.
- Done when: uploaded forms produce structured JSON with fields, rules, deadlines, and required inputs.

## Issue 2: Create guided question-by-question flow
- Labels: `frontend`, `ux`
- Owner: Frontend / UX
- Goal: ask one plain-language question at a time and map the answer to the right form field.
- Done when: the user can complete a short guided form flow in the UI.

## Issue 3: Add validation and error recovery
- Labels: `ai`, `backend`
- Owner: AI / extraction
- Goal: detect missing required fields, invalid formats, deadlines, and conditional requirements.
- Done when: invalid or incomplete answers trigger clear correction prompts.

## Issue 4: Add accessibility modes
- Labels: `frontend`, `accessibility`
- Owner: Frontend / UX
- Goal: support simple language, large text, reduced cognitive load, and screen-reader-friendly layout.
- Done when: the same form can be shown in at least two visibly different accessibility modes.

## Issue 5: Add source citations and fidelity panel
- Labels: `ai`, `frontend`
- Owner: AI / extraction + Frontend / UX
- Goal: show where each requirement came from and surface deadlines, exceptions, and warnings.
- Done when: every important extracted rule has a source reference in the UI.

## Issue 6: Build final review and draft submission screen
- Labels: `frontend`, `backend`
- Owner: Frontend / UX
- Goal: show the filled draft before submission and let the user confirm it.
- Done when: the completed form can be reviewed end to end before final action.

## Issue 7: Prepare demo documents and evaluation cases
- Labels: `qa`, `demo`
- Owner: Demo / QA
- Goal: create 2 to 3 public-form test cases plus edge cases for deadlines, conditions, and required attachments.
- Done when: the team has a repeatable demo set and a simple pass/fail checklist.

## Issue 8: Polish the demo narrative
- Labels: `demo`, `ux`
- Owner: Demo / QA + Frontend / UX
- Goal: make the before -> during -> after story easy to follow in a live presentation.
- Done when: the demo can be explained in under 2 minutes and shown reliably.

## Recommended order
1. Extraction pipeline
2. Guided Q&A flow
3. Validation and fidelity checks
4. Accessibility modes
5. Review screen and demo polish

## Optional future issues
- Multilingual support
- Voice input/output
- Shareable export packet
- Broader document types beyond forms