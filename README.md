# AccessBridge

AccessBridge is an AI-powered accessibility project that turns complex forms and documents into a guided, personalized, and verifiable task experience.

## Try It Yourself

1. Clone the repository:

	git clone https://github.com/BhagyaV3/AccessBridge.git
	cd AccessBridge

2. Review the current planning files:

	- [plan.md](./plan.md)
	- [github-issues.md](./github-issues.md)

3. Once implementation starts, install the chosen frontend/backend dependencies and run the app locally using the team’s final stack.

4. Use the app with a difficult form or policy document:

	- upload the document
	- extract fields, rules, deadlines, and conditions
	- answer one plain-language question at a time
	- switch accessibility modes if needed
	- review the final draft with citations and warnings

## Features

| Feature | Description |
| --- | --- |
| Guided form transformation | Turns a dense form into an interactive, question-by-question experience. |
| Structured extraction | Pulls out fields, rules, deadlines, exceptions, and validation logic from the source document. |
| Cited answers | Shows where each requirement or answer came from in the original source. |
| Accessibility modes | Supports simple language, large text, reduced cognitive load, and screen-reader-friendly layout. |
| Fidelity checks | Flags missing or weakened requirements before the user reviews the final draft. |
| Final review flow | Lets the user inspect the completed draft before submission. |
| Focused MVP scope | Stays centered on one hard form so the live demo remains clear and reliable. |

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER UPLOADS A FORM OR POLICY                                      │
│                                                                     │
│  PDF/DOCX/TXT/HTML                                                  │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────────┐         ┌───────────────────────────────────┐    │
│  │ AccessBridge  │         │    Extraction + Structuring      │    │
│  │ UI            │────────▶│                                   │    │
│  │              │         │  • parse text / OCR fallback      │    │
│  │ upload +     │         │  • extract fields and rules       │    │
│  │ accessibility │         │  • detect deadlines/conditions    │    │
│  │ settings      │         │  • attach source citations        │    │
│  └──────────────┘         └───────────────────────────────────┘    │
│                                                                     │
│                               ▼                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Guided Q&A + Validation                                        │  │
│  │                                                               │  │
│  │ • asks one plain-language question at a time                  │  │
│  │ • maps answers to the correct field                           │  │
│  │ • checks formats, requirements, and conditional logic         │  │
│  │ • adapts explanations based on selected accessibility mode    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                               ▼                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Final Review                                                   │  │
│  │                                                               │  │
│  │ • filled draft                                                │  │
│  │ • citations and warnings                                      │  │
│  │ • fidelity checks                                             │  │
│  │ • user confirmation before submission                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Modules

- UI shell for upload, guided Q&A, and review
- Document parsing and OCR fallback
- Structured extraction of rules and conditions
- Validation and fidelity checking
- Accessibility preference handling

## Tech Stack

| Layer | Stack |
| --- | --- |
| Frontend | React |
| Backend | API service for document parsing, state, and validation |
| AI Models | LLM API for extraction, simplification, and verification |
| Document Parsing | PDF/text extraction with OCR fallback |
| Storage | Lightweight app state and document metadata |
| Testing | Unit and flow tests for extraction, validation, and UI behavior |

### AI runtime

The backend is wired for an OpenAI-compatible cloud model when `ACCESSBRIDGE_AI_MODE=cloud` and `OPENAI_API_KEY` is set. The default model name is `gpt-4.1-mini`, and the backend falls back to deterministic parsing if the cloud API is unavailable.

## Supported File Types

| File Type | Support |
| --- | --- |
| PDF (.pdf) | Primary input type; text extraction with OCR fallback if needed |
| DOCX (.docx) | Parsed into structured text and sections |
| TXT (.txt) | Read as-is |
| HTML (.html) | DOM text extraction with cleanup |
| Scanned forms | OCR route, if the page has no usable text |

## Screenshots

| View | Status |
| --- | --- |
| Upload | Planned form upload screen |
| Guided Q&A | Planned question-by-question flow |

| View | Status |
| --- | --- |
| Accessibility Modes | Planned simple-language / large-text views |
| Final Review | Planned citation-backed review screen |

See future screenshots in the repo once the application UI exists.

## Limits & Constraints

| Constraint | Details |
| --- | --- |
| Scope | One main form type first; keep the demo focused and feasible |
| Content | No generic document chatbot; the project is action-oriented |
| Time | One-week build window; prioritize the end-to-end flow |
| Accessibility | User-selected modes only; avoid unsupported assumptions |
| Fidelity | Preserve deadlines, exceptions, and conditions |

## Known Limitations

| Limitation | Details |
| --- | --- |
| The app is not fully built yet | The repository is still in planning and setup mode |
| Multi-document support is deferred | The MVP should stay focused on one hard form |
| Voice and multilingual support are optional | They are stretch ideas, not core dependencies |
| Some scanned forms may need OCR tuning | OCR quality varies by source image |
| Unsupported edge cases may require manual review | Fidelity matters more than perfect automation |

## Development

### Install dependencies

When the implementation starts, install the chosen frontend and backend dependencies for the final stack.

### Configure AI

Set `ACCESSBRIDGE_AI_MODE=cloud`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL` or `OPENAI_BASE_URL` to use the cloud LLM path. If you do not set those values, the backend uses the deterministic fallback extractor.

### Run the app

Once code exists, run the frontend and backend locally using the project setup agreed by the team.

### Build the project

Use the final build commands defined by the implementation stack.

### Run tests

Test the extraction pipeline, guided flow, validation logic, and review screen before merging.

## Team

| Owner | Area | Focus |
| --- | --- | --- |
| TBD | Integration / Backend | Upload flow, API wiring, state, deployment glue |
| TBD | AI / Extraction | Parsing, structured output, validation logic, verifier |
| TBD | Frontend / UX | Guided Q&A, accessibility modes, review UI |
| TBD | Demo / QA | Demo cases, edge cases, presentation polish |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed workflow and task breakdown.

## License

Built for the AI Builders Hackathon 2026.
