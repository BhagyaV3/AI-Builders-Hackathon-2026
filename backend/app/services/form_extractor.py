from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re

from app.schemas.form import (
    FormDeadline,
    FormExtractionResponse,
    FormField,
    FormRule,
    FormWarning,
)

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - fallback when dependency is unavailable
    PdfReader = None


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


def _extract_pdf_text(raw_bytes: bytes) -> str:
    if PdfReader is None:
        return ""

    try:
        reader = PdfReader(BytesIO(raw_bytes))
    except Exception:
        return ""

    pages: list[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        if page_text.strip():
            pages.append(page_text.strip())

    return "\n".join(pages)


def _extract_text_from_upload(file_name: str | None, content_type: str | None, raw_bytes: bytes) -> str:
    normalized_file_name = (file_name or "").lower()
    normalized_content_type = (content_type or "").lower()
    looks_like_pdf = "pdf" in normalized_content_type or normalized_file_name.endswith(".pdf")

    if looks_like_pdf:
        pdf_text = _extract_pdf_text(raw_bytes).strip()
        if pdf_text:
            return pdf_text

    return _decode_bytes(raw_bytes).strip()


def parse_uploaded_content(
    file_name: str | None,
    raw_bytes: bytes | None,
    text: str | None,
    content_type: str | None = None,
) -> ParsedForm:
    if text and text.strip():
        return ParsedForm(file_name=file_name or "pasted-text", text=text.strip())

    if raw_bytes:
        extracted_text = _extract_text_from_upload(file_name, content_type, raw_bytes)
        if extracted_text:
            return ParsedForm(file_name=file_name or "uploaded-file", text=extracted_text)

    return ParsedForm(
        file_name=file_name or "unknown-form",
        text=(
            "Sample form text. Applicant name is required. "
            "Submit by March 15. Income must be provided. "
            "If the applicant is under 18, a parent signature is required."
        ),
    )


def build_mock_extraction(parsed_form: ParsedForm) -> FormExtractionResponse:
    return build_form_extraction(parsed_form)


def build_form_extraction(parsed_form: ParsedForm) -> FormExtractionResponse:
    text = parsed_form.text
    lower_text = text.lower()

    fields: list[FormField] = []
    rules: list[FormRule] = []
    deadlines: list[FormDeadline] = []
    exceptions: list[str] = []
    warnings: list[FormWarning] = []

    _append_field_if_present(
        fields,
        lower_text,
        name="applicant_name",
        label="Applicant name",
        pattern=r"\b(name|full name|applicant name)\b",
        required=True,
        source_text=text,
    )
    _append_field_if_present(
        fields,
        lower_text,
        name="income",
        label="Monthly income",
        pattern=r"\b(income|monthly income|annual income)\b",
        required=True,
        source_text=text,
    )
    _append_field_if_present(
        fields,
        lower_text,
        name="signature",
        label="Signature",
        pattern=r"\b(signature|sign)\b",
        required=False,
        source_text=text,
    )
    _append_field_if_present(
        fields,
        lower_text,
        name="date_of_birth",
        label="Date of birth",
        pattern=r"\b(date of birth|dob)\b",
        required=True,
        source_text=text,
    )
    _append_field_if_present(
        fields,
        lower_text,
        name="address",
        label="Mailing address",
        pattern=r"\b(address|mailing address|home address)\b",
        required=True,
        source_text=text,
    )
    _append_field_if_present(
        fields,
        lower_text,
        name="academic_score",
        label="Academic score",
        pattern=r"\b(gpa|score|scores|marks|grade|grade card|score card)\b",
        required="required" in lower_text or "must" in lower_text,
        source_text=text,
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

    if "required" in lower_text or "must" in lower_text or "shall" in lower_text:
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


def _append_field_if_present(
    fields: list[FormField],
    lower_text: str,
    name: str,
    label: str,
    pattern: str,
    required: bool,
    source_text: str,
) -> None:
    if any(existing_field.name == name for existing_field in fields):
        return

    if not re.search(pattern, lower_text, flags=re.IGNORECASE):
        return

    fields.append(
        FormField(
            name=name,
            label=label,
            required=required,
            source_excerpt=_find_excerpt(source_text, pattern),
        )
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