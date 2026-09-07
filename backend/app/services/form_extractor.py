from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from app.schemas.form import (
    FormDeadline,
    FormExtractionResponse,
    FormField,
    FormRule,
    FormWarning,
)


@dataclass
class ParsedForm:
    file_name: str
    text: str


def _decode_bytes(raw_bytes: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


def parse_uploaded_content(file_name: str | None, raw_bytes: bytes | None, text: str | None) -> ParsedForm:
    if text and text.strip():
        return ParsedForm(file_name=file_name or "pasted-text", text=text.strip())

    if raw_bytes:
        decoded = _decode_bytes(raw_bytes).strip()
        if decoded:
            return ParsedForm(file_name=file_name or "uploaded-file", text=decoded)

    return ParsedForm(
        file_name=file_name or "unknown-form",
        text=(
            "Sample form text. Applicant name is required. "
            "Submit by March 15. Income must be provided. "
            "If the applicant is under 18, a parent signature is required."
        ),
    )


def build_mock_extraction(parsed_form: ParsedForm) -> FormExtractionResponse:
    text = parsed_form.text
    lower_text = text.lower()

    fields: list[FormField] = []
    rules: list[FormRule] = []
    deadlines: list[FormDeadline] = []
    exceptions: list[str] = []
    warnings: list[FormWarning] = []
    next_steps: list[str] = []

    if "name" in lower_text:
        fields.append(
            FormField(
                name="applicant_name",
                label="Applicant name",
                required=True,
                source_excerpt=_find_excerpt(text, r"name"),
            )
        )

    if "income" in lower_text:
        fields.append(
            FormField(
                name="income",
                label="Monthly income",
                required=True,
                source_excerpt=_find_excerpt(text, r"income"),
            )
        )

    if "signature" in lower_text:
        fields.append(
            FormField(
                name="signature",
                label="Signature",
                required=False,
                source_excerpt=_find_excerpt(text, r"signature"),
            )
        )

    if "submit" in lower_text or "due" in lower_text or "deadline" in lower_text:
        deadline_text = _find_sentence(text, ["submit", "due", "deadline"]) or "Submit by the listed deadline."
        deadlines.append(
            FormDeadline(
                text=deadline_text,
                due_date=_extract_date_hint(deadline_text),
                source_excerpt=deadline_text,
            )
        )

    if "if" in lower_text or "unless" in lower_text:
        condition_text = _find_sentence(text, ["if", "unless"]) or "Conditional requirement present."
        rules.append(
            FormRule(
                kind="condition",
                text=condition_text,
                source_excerpt=condition_text,
            )
        )

    if "under 18" in lower_text or "parent" in lower_text:
        exceptions.append("If the applicant is under 18, a parent or guardian signature is required.")

    if not fields:
        fields.extend(
            [
                FormField(name="field_1", label="Primary field", required=True, source_excerpt="Mocked from source"),
                FormField(name="field_2", label="Secondary field", required=False, source_excerpt="Mocked from source"),
            ]
        )

    if not rules:
        rules.append(
            FormRule(
                kind="instruction",
                text="Answer each guided question using the most direct information from the form.",
                source_excerpt="Mocked from source",
            )
        )

    if not deadlines:
        deadlines.append(
            FormDeadline(
                text="No explicit deadline detected; review the document for submission timing.",
                due_date=None,
                source_excerpt="Mocked from source",
            )
        )

    if not exceptions:
        exceptions.append("No explicit exception detected in the parsed text.")

    if "required" in lower_text or "must" in lower_text:
        warnings.append(
            FormWarning(
                text="The form contains required items that must be completed carefully.",
                severity="medium",
                source_excerpt=_find_sentence(text, ["required", "must"]) or "Mocked from source",
            )
        )

    if not warnings:
        warnings.append(
            FormWarning(
                text="This is a mocked extraction result. Replace with real parsing when document processing is implemented.",
                severity="low",
                source_excerpt="Mocked from source",
            )
        )

    next_steps = [
        "Fill in the required fields.",
        "Review the deadline and any conditional requirements.",
        "Check the final draft before submission.",
    ]

    title = _derive_title(parsed_form.file_name, text)
    summary = _build_summary(fields, deadlines, rules, exceptions)

    return FormExtractionResponse(
        file_name=parsed_form.file_name,
        title=title,
        summary=summary,
        fields=fields,
        rules=rules,
        deadlines=deadlines,
        exceptions=exceptions,
        warnings=warnings,
        next_steps=next_steps,
        confidence=0.62,
    )


def _find_excerpt(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    start = max(0, match.start() - 40)
    end = min(len(text), match.end() + 40)
    return text[start:end].strip()


def _find_sentence(text: str, keywords: list[str]) -> str | None:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in keywords):
            return sentence.strip()
    return None


def _extract_date_hint(text: str) -> str | None:
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _derive_title(file_name: str, text: str) -> str:
    path_stem = Path(file_name).stem.replace("_", " ").strip()
    if path_stem and path_stem != "unknown-form":
        return path_stem.title()
    sentence = _find_sentence(text, ["form", "application", "request"])
    if sentence:
        return sentence[:80].strip().rstrip(".")
    return "Untitled Form"


def _build_summary(
    fields: list[FormField],
    deadlines: list[FormDeadline],
    rules: list[FormRule],
    exceptions: list[str],
) -> str:
    pieces: list[str] = []
    if fields:
        pieces.append(f"{len(fields)} field(s) detected")
    if deadlines:
        pieces.append("deadline information detected")
    if any(rule.kind == "condition" for rule in rules):
        pieces.append("conditional logic detected")
    if exceptions:
        pieces.append("at least one exception or special case detected")
    return ", ".join(pieces) if pieces else "Mocked extraction completed."