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

|  |
|  |
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

|  |
|  |
| Frontend | React |
| Backend | API service for document parsing, state, and validation |
| AI Models | LLM API for extraction, simplification, and verification |
| Document Parsing | PDF/text extraction with OCR fallback |
| Storage | Lightweight app state and document metadata |
| Testing | Unit and flow tests for extraction, validation, and UI behavior |

## Supported File Types

|  |
|  |
| PDF (.pdf) | Primary input type; text extraction with OCR fallback if needed |
| DOCX (.docx) | Parsed into structured text and sections |
| TXT (.txt) | Read as-is |
| HTML (.html) | DOM text extraction with cleanup |
| Scanned forms | OCR route, if the page has no usable text |

## Screenshots

| Upload | Guided Q&A |
| --- | --- |
| Planned form upload screen | Planned question-by-question flow |

| Accessibility Modes | Final Review |
| --- | --- |
| Planned simple-language / large-text views | Planned citation-backed review screen |

See future screenshots in the repo once the application UI exists.

## Limits & Constraints

|  |
|  |
| Scope | One main form type first; keep the demo focused and feasible |
| Content | No generic document chatbot; the project is action-oriented |
| Time | One-week build window; prioritize the end-to-end flow |
| Accessibility | User-selected modes only; avoid unsupported assumptions |
| Fidelity | Preserve deadlines, exceptions, and conditions |

## Known Limitations

|  |
|  |
| The app is not fully built yet | The repository is still in planning and setup mode |
| Multi-document support is deferred | The MVP should stay focused on one hard form |
| Voice and multilingual support are optional | They are stretch ideas, not core dependencies |
| Some scanned forms may need OCR tuning | OCR quality varies by source image |
| Unsupported edge cases may require manual review | Fidelity matters more than perfect automation |

## Development

### Install dependencies

When the implementation starts, install the chosen frontend and backend dependencies for the final stack.

### Run the app

Once code exists, run the frontend and backend locally using the project setup agreed by the team.

### Build the project

Use the final build commands defined by the implementation stack.

### Run tests

Test the extraction pipeline, guided flow, validation logic, and review screen before merging:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest tests
```

## AI Components & Features

The AI subsystem addresses the core AI issues defined in [github-issues.md](./github-issues.md) and [plan.md](./plan.md):

| Feature | Endpoint | Description & Connection |
| --- | --- | --- |
| **Form Extraction Pipeline** (Issue 2) | `POST /api/ai/extract` | Accepts PDFs or raw document text. Extracts fields, labels, requirements, conditional branches (`if... then`), deadlines, exceptions, required attachments, and exact source citations. |
| **Validation & Error Recovery** (Issue 4) | `POST /api/ai/validate` | Validates user answers, evaluates cross-field conditional logic (e.g. minor signature requirements), checks deadlines, and generates plain-language, empathetic correction prompts for easy error recovery. |
| **Fidelity Verifier Pass** (Issue 6) | `POST /api/ai/verify-fidelity` | Compares extracted claims and simplified rules against the original source document. Detects altered numbers, weakened conditions, and omitted legal clauses, computing an overall fidelity trust score. |
| **Guided Q&A & Accessibility Presets** (Issues 3 & 5) | `POST /api/ai/guided-questions` | Converts bureaucratic form fields into bite-sized questions adapted to accessibility presets: `simple_language`, `reduced_cognitive_load`, `screen_reader`, and `standard`. |

### How to Run

1. Activate virtual environment and start the FastAPI server:
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```
2. Interactive API documentation is available at `http://localhost:8000/docs`.

### Dependencies & Environment Variables

- **Dependencies**: All core dependencies (`fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `pypdf`) are defined in `backend/requirements.txt`. Development/testing uses `pytest`.
- **Environment Variables (Optional)**:
  - `GEMINI_API_KEY`: (Optional) Connects to Google Gemini API for augmented LLM generation.
  - `OPENAI_API_KEY`: (Optional) Connects to OpenAI API for alternative LLM processing.
  - *Note*: If no API keys are set, the system seamlessly runs high-precision deterministic linguistic and pattern extraction and verification with zero external runtime dependencies.


## Team

|  |
|  |
| TBD | Integration / Backend | Upload flow, API wiring, state, deployment glue |
| TBD | AI / Extraction | Parsing, structured output, validation logic, verifier |
| TBD | Frontend / UX | Guided Q&A, accessibility modes, review UI |
| TBD | Demo / QA | Demo cases, edge cases, presentation polish |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed workflow and task breakdown.

## License

Built for the AI Builders Hackathon 2026.