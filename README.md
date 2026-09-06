# AccessBridge

AccessBridge is an AI-powered accessibility project that turns complex forms and documents into a guided, personalized, and verifiable task experience.

## Overview

The goal of AccessBridge is not to build another generic document chatbot. Instead, it focuses on helping users actually complete forms and understand requirements by combining document parsing, guided questions, accessibility-aware presentation, and fidelity checks.

## Description

AccessBridge is being designed around one core flow:

1. Upload a form or document.
2. Extract the field structure, rules, deadlines, and conditions.
3. Ask the user one plain-language question at a time.
4. Adapt the experience for accessibility preferences.
5. Show a reviewable draft with citations and warnings before final submission.

The current repository is in planning and setup mode, so the emphasis is on defining the product, issues, and implementation order before the full application is built.

## Planned MVP

- Form upload and text extraction
- Structured extraction of fields, rules, and conditions
- Guided question-by-question flow
- Accessibility modes such as simple language and large text
- Source citations and a fidelity check before review

## Repository Structure

```text
AccessBridge/
├── README.md
├── CONTRIBUTING.md
├── plan.md
└── github-issues.md
```

## Working With the Project

At this stage, the repo is documentation-first. The main files to review are:

- [plan.md](./plan.md) - project concept, feature scope, risks, and one-week plan
- [github-issues.md](./github-issues.md) - issue breakdown and role split

## Development Notes

- Keep the MVP narrow.
- Focus on one form type first.
- Favor reliability and clarity over breadth.
- Keep accessibility preferences explicit and user-controlled.

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening issues or pull requests.

## Contact

Project team contact details can be added here once roles are finalized.

## License

No license has been specified yet.