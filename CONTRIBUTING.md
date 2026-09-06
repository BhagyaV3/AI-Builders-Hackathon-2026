# CONTRIBUTING.md

## Team Collaboration Guide

AccessBridge is a short-horizon hackathon project, so the collaboration model should stay lightweight, explicit, and easy to follow.

## Team Members & Responsibilities

|  |
|  |
| TBD | TBD | Integration & Backend | Upload pipeline, API wiring, state handling, deployment glue |
| TBD | TBD | AI & Extraction | Field extraction, rule detection, validation logic, verifier |
| TBD | TBD | Frontend & UX | Guided flow, accessibility modes, review screen |
| TBD | TBD | Demo & QA | Test cases, edge cases, walkthrough, presentation polish |

## Branching Strategy

We use feature branches + pull requests to `main`. Never push directly to `main`.

### Branch naming convention

```
<your-name>/<short-description>
```

Examples:

```
backend/form-pipeline
backend/validation-rules
ai/extraction-schema
ai/fidelity-check
frontend/guided-flow
frontend/accessibility-modes
demo/test-cases
demo/presentation-polish
```

### Workflow per task

1. `git checkout main && git pull origin main`
2. `git checkout -b your-name/task-description`
3. Do your work, commit often
4. `git push -u origin your-name/task-description`
5. Open a PR to `main` on GitHub
6. Self-merge or request review based on team agreement
7. Delete the branch after merge

## Execution Order (Wave-Based)

Tasks have dependencies. Follow this order so the team can work in parallel without blocking each other.

### Wave 1 — Foundation

|  |
|  |
| Integration & Backend | Project structure, shared state, upload API skeleton |

> Everyone is blocked until Wave 1 is merged. This creates the shared structure and interfaces that the other tasks depend on.

### Wave 2 — Core Modules (All 4 in parallel)

|  |
|  |
| Integration & Backend | API wiring and state storage |
| AI & Extraction | Extraction schema and rule detection |
| Frontend & UX | Layout planning, accessibility states, mock UI |
| Demo & QA | Test documents and evaluation checklist |

### Wave 3 — Feature Implementation (All 4 in parallel)

|  |
|  |
| Integration & Backend | Upload pipeline and structured payload handling |
| AI & Extraction | Extraction pipeline and citation data |
| Frontend & UX | Guided question-by-question flow |
| Demo & QA | Edge cases and demo scripts |

### Wave 4 — Orchestration & UI Completion

|  |
|  |
| Integration & Backend | Validation wiring and final review payload |
| Frontend & UX | Accessibility modes and review screen |
| AI & Extraction | Fidelity checks and warning data |
| Demo & QA | End-to-end rehearsal and bug list |

### Wave 5 — Final Integration (Everyone)

|  |
|  |
| All members | Integration testing, bug fixes, polish, demo prep |

## Ground Rules

1. Pull from `main` before starting each wave.
2. Do not modify shared structure files without notifying the group.
3. Merge foundation work first so the rest of the team can move.
4. Use small, frequent PRs.
5. If you are blocked, say so early.
6. Keep optional ideas optional until the core flow works.
7. Do not remove deadlines, conditions, or exceptions from simplified output.
8. Keep accessibility settings user-controlled and explicit.

## Quick Git Commands

### Start a new task

git checkout main
git pull origin main
git checkout -b your-name/task-name

### Save progress

git add .
git commit -m "feat: description of what you did"
git push -u origin your-name/task-name

### Create PR

gh pr create --title "Task X: Short description" --base main

### After PR is merged, clean up

git checkout main
git pull origin main
git branch -d your-name/task-name

## Tech Stack Reference

|  |
|  |
| Runtime | Web app with API backend |
| UI | React |
| Backend | Document parsing, validation, and review APIs |
| AI | LLM-based extraction and fidelity checking |
| Parsing | PDF/OCR/text extraction |
| Testing | Unit and flow tests |

## Key Architecture Notes

• Keep the MVP centered on one form caseworker flow
• Extract structure before simplifying anything
• Preserve source meaning, especially deadlines, conditions, and exceptions
• Use citations and warnings in the UI where possible
• Keep accessibility preferences user-controlled

## Additional Links

- [Code](https://github.com/BhagyaV3/AccessBridge)
- [Issues](./github-issues.md)
- [Plan](./plan.md)
- [README](./README.md)

## About

AccessBridge is a form-focused accessibility project for the AI Builders Hackathon 2026.

### Topics

[accessibility](https://github.com/topics/accessibility) [ai](https://github.com/topics/ai) [forms](https://github.com/topics/forms) [hackathon](https://github.com/topics/hackathon) [llm](https://github.com/topics/llm) [productivity](https://github.com/topics/productivity) [react](https://github.com/topics/react)

### Resources

Readme

### Contributing

Contributing

### Stars

0 stars

### Watchers

0 watching

### Forks

0 forks

## License

Built for the AI Builders Hackathon 2026.