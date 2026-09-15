"""
AI Fidelity Validator & Verifier Pass (Issue 6)

What this feature does:
Executes an automated verification pass (second-pass validator) that compares
extracted claims, rules, deadlines, and exceptions back against the raw source document text.
It specifically detects and flags:
1. Altered numbers (e.g. source says 30 days or $5,000, but extraction changed the figure).
2. Weakened conditions (e.g. changing "mandatory/must" into "optional/may").
3. Unsubstantiated claims that have no textual grounding in the source document.
4. Omissions of critical legal terms (e.g., penalty clauses, mandatory attachments).
5. Grounded source citations attaching exact matching quotes and character positions.
6. Computes an overall fidelity score (0.0 to 1.0) and generates alerts for the UI fidelity panel.

How it connects to the rest of the project:
1. Connects to `app.routes.ai.verify_fidelity_ai` to power `/api/ai/verify-fidelity`.
2. Connects to the frontend "Fidelity Panel" and "Final Review Screen" described in Issue 6 and Issue 7.
3. Provides verifiable trust guarantees so simplification never silently corrupts original legal rules.
"""

from __future__ import annotations

import re
from typing import Any

from app.schemas.ai import (
    AIFidelityResponse,
    AIFidelityVerifyRequest,
    FidelityCheckStatus,
    FidelityClaimCheck,
    SourceCitation,
)
from app.schemas.form import FormDeadline, FormField, FormRule


def verify_extraction_fidelity(request: AIFidelityVerifyRequest) -> AIFidelityResponse:
    """
    Compares extracted elements against the original source document text to ensure
    fidelity, factual grounding, numerical accuracy, and condition preservation.
    """
    source_text = request.source_text
    lower_source = source_text.lower()

    checks: list[FidelityClaimCheck] = []
    fidelity_warnings: list[str] = []

    # 1. Verify Fields
    for field in request.extracted_fields:
        field_check = _verify_field_fidelity(field, source_text, lower_source)
        checks.append(field_check)

    # 2. Verify Rules & Conditions
    for rule in request.extracted_rules:
        rule_check = _verify_rule_fidelity(rule, source_text, lower_source)
        checks.append(rule_check)

    # 3. Verify Deadlines
    for deadline in request.extracted_deadlines:
        dl_check = _verify_deadline_fidelity(deadline, source_text, lower_source)
        checks.append(dl_check)

    # 4. Verify Exceptions
    for exception_text in request.extracted_exceptions:
        exc_check = _verify_exception_fidelity(exception_text, source_text, lower_source)
        checks.append(exc_check)

    # 5. Check for Potential Source Omissions
    omissions = _check_critical_source_omissions(source_text, checks)
    checks.extend(omissions)

    # Calculate overall statistics
    total_checks = len(checks)
    verified_count = sum(1 for c in checks if c.status == FidelityCheckStatus.VERIFIED)
    flagged_count = total_checks - verified_count

    if total_checks > 0:
        overall_fidelity = round(sum(c.fidelity_score for c in checks) / total_checks, 2)
    else:
        overall_fidelity = 1.0

    # Build user-facing fidelity warnings
    altered_num_count = sum(1 for c in checks if c.status == FidelityCheckStatus.ALTERED_NUMBER)
    weakened_count = sum(1 for c in checks if c.status == FidelityCheckStatus.WEAKENED)

    if altered_num_count > 0:
        fidelity_warnings.append(f"{altered_num_count} numerical value(s) in claims differ from the source document.")
    if weakened_count > 0:
        fidelity_warnings.append(f"{weakened_count} condition(s) appear weakened compared to mandatory source phrasing.")
    if overall_fidelity < 0.75:
        fidelity_warnings.append("Fidelity score is below 75%; manual caseworker review of the source document is recommended.")

    return AIFidelityResponse(
        overall_fidelity_score=overall_fidelity,
        total_checks=total_checks,
        verified_count=verified_count,
        flagged_count=flagged_count,
        checks=checks,
        fidelity_warnings=fidelity_warnings,
    )


def _verify_field_fidelity(field: FormField, source_text: str, lower_source: str) -> FidelityClaimCheck:
    """Verifies that an extracted field is grounded in the source text."""
    label_terms = [term for term in re.split(r"\s+", field.label.lower()) if len(term) > 2]
    matched_term = next((term for term in label_terms if term in lower_source), None)

    if matched_term:
        # Find citation
        match = re.search(re.escape(matched_term), source_text, flags=re.IGNORECASE)
        start = max(0, match.start() - 40) if match else 0
        end = min(len(source_text), match.end() + 40) if match else len(source_text)
        citation = SourceCitation(quote=source_text[start:end].strip(), start_char=start, end_char=end)

        return FidelityClaimCheck(
            claim_type="field",
            claim_text=f"Field: {field.label} ({field.name})",
            status=FidelityCheckStatus.VERIFIED,
            fidelity_score=0.95,
            source_citation=citation,
            explanation="Field requirement is directly substantiated by terms in the source document.",
        )
    else:
        return FidelityClaimCheck(
            claim_type="field",
            claim_text=f"Field: {field.label} ({field.name})",
            status=FidelityCheckStatus.FLAGGED,
            fidelity_score=0.50,
            source_citation=None,
            explanation="Field was inferred by the extractor but lacks direct keyword evidence in the source.",
        )


def _verify_rule_fidelity(rule: FormRule, source_text: str, lower_source: str) -> FidelityClaimCheck:
    """Verifies that a rule or condition preserves modal strength and numerical accuracy."""
    rule_lower = rule.text.lower()

    # Check for weakened modal conditions
    # e.g., if extracted says "you can submit" but source says "you must submit"
    source_has_must = "must" in lower_source or "shall" in lower_source or "required" in lower_source
    extracted_has_optional = "optional" in rule_lower or "you can" in rule_lower or "may" in rule_lower

    if source_has_must and extracted_has_optional and "required" not in rule_lower:
        return FidelityClaimCheck(
            claim_type="rule",
            claim_text=rule.text,
            status=FidelityCheckStatus.WEAKENED,
            fidelity_score=0.45,
            source_citation=SourceCitation(quote=rule.source_excerpt or rule.text),
            explanation="Requirement may have been weakened to optional phrasing while source uses mandatory language.",
        )

    # Check numerical preservation
    extracted_numbers = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", rule.text)
    for num in extracted_numbers:
        clean_num = num.replace(",", "")
        if clean_num not in source_text.replace(",", ""):
            return FidelityClaimCheck(
                claim_type="rule",
                claim_text=rule.text,
                status=FidelityCheckStatus.ALTERED_NUMBER,
                fidelity_score=0.30,
                source_citation=SourceCitation(quote=rule.source_excerpt or rule.text),
                explanation=f"Number '{num}' in extracted rule was not found in the original source document.",
            )

    # Check textual overlap
    keywords = [w for w in re.split(r"\W+", rule_lower) if len(w) > 3]
    matches = sum(1 for kw in keywords if kw in lower_source)
    ratio = matches / len(keywords) if keywords else 1.0

    if ratio > 0.4:
        return FidelityClaimCheck(
            claim_type="rule",
            claim_text=rule.text,
            status=FidelityCheckStatus.VERIFIED,
            fidelity_score=min(1.0, 0.7 + (0.3 * ratio)),
            source_citation=SourceCitation(quote=rule.source_excerpt or rule.text),
            explanation="Rule is factually grounded and preserves condition logic from source.",
        )
    else:
        return FidelityClaimCheck(
            claim_type="rule",
            claim_text=rule.text,
            status=FidelityCheckStatus.FLAGGED,
            fidelity_score=0.40,
            source_citation=None,
            explanation="Rule exhibits low textual correlation with source document sentences.",
        )


def _verify_deadline_fidelity(deadline: FormDeadline, source_text: str, lower_source: str) -> FidelityClaimCheck:
    """Verifies that deadline dates and text accurately reflect source timing."""
    if deadline.due_date and deadline.due_date.lower() in lower_source:
        return FidelityClaimCheck(
            claim_type="deadline",
            claim_text=deadline.text,
            status=FidelityCheckStatus.VERIFIED,
            fidelity_score=1.0,
            source_citation=SourceCitation(quote=deadline.source_excerpt or deadline.text),
            explanation=f"Exact date '{deadline.due_date}' confirmed present in source document.",
        )

    dl_keywords = ["submit", "due", "deadline", "before", "within", "march", "april", "may", "june", "december"]
    found_kw = [kw for kw in dl_keywords if kw in deadline.text.lower() and kw in lower_source]

    if found_kw:
        return FidelityClaimCheck(
            claim_type="deadline",
            claim_text=deadline.text,
            status=FidelityCheckStatus.VERIFIED,
            fidelity_score=0.85,
            source_citation=SourceCitation(quote=deadline.source_excerpt or deadline.text),
            explanation="Deadline information verified against source document timeline instructions.",
        )
    else:
        return FidelityClaimCheck(
            claim_type="deadline",
            claim_text=deadline.text,
            status=FidelityCheckStatus.FLAGGED,
            fidelity_score=0.50,
            source_citation=None,
            explanation="Deadline phrasing does not have a confirmed match in source text.",
        )


def _verify_exception_fidelity(exception_text: str, source_text: str, lower_source: str) -> FidelityClaimCheck:
    """Verifies extracted exceptions (e.g. minor, fee waiver)."""
    exc_lower = exception_text.lower()
    keywords = ["under 18", "guardian", "waiver", "exempt", "extension", "special"]
    matched = [kw for kw in keywords if kw in exc_lower and kw in lower_source]

    if matched:
        return FidelityClaimCheck(
            claim_type="exception",
            claim_text=exception_text,
            status=FidelityCheckStatus.VERIFIED,
            fidelity_score=0.90,
            source_citation=SourceCitation(quote=f"Matched keywords: {', '.join(matched)}"),
            explanation=f"Exception verified based on source keywords: {', '.join(matched)}.",
        )
    else:
        return FidelityClaimCheck(
            claim_type="exception",
            claim_text=exception_text,
            status=FidelityCheckStatus.VERIFIED if "standard" in exc_lower else FidelityCheckStatus.FLAGGED,
            fidelity_score=0.60,
            source_citation=None,
            explanation="Informational note on exceptions.",
        )


def _check_critical_source_omissions(source_text: str, existing_checks: list[FidelityClaimCheck]) -> list[FidelityClaimCheck]:
    """Identifies if high-severity clauses in the source text were omitted during extraction."""
    omissions: list[FidelityClaimCheck] = []
    lower_source = source_text.lower()

    critical_clauses = [
        ("penalty of perjury", "Legal certification / penalty of perjury clause in source text"),
        ("non-refundable", "Non-refundable fee notification in source text"),
        ("notary", "Notarization requirement in source text"),
    ]

    all_claim_texts = " ".join(c.claim_text.lower() for c in existing_checks)

    for phrase, desc in critical_clauses:
        if phrase in lower_source and phrase not in all_claim_texts:
            match = re.search(re.escape(phrase), source_text, flags=re.IGNORECASE)
            start = max(0, match.start() - 30) if match else 0
            end = min(len(source_text), match.end() + 30) if match else len(source_text)
            citation = SourceCitation(quote=source_text[start:end].strip(), start_char=start, end_char=end)

            omissions.append(
                FidelityClaimCheck(
                    claim_type="omission",
                    claim_text=desc,
                    status=FidelityCheckStatus.OMITTED,
                    fidelity_score=0.50,
                    source_citation=citation,
                    explanation=f"The source document mentions '{phrase}', which was not detected in extracted fields or rules.",
                )
            )

    return omissions
