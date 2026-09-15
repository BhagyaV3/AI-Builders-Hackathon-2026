"""
AI Schemas for AccessBridge

This module defines Pydantic models for the AI components:
- Issue 2: AI structured extraction (fields, conditions, deadlines, attachments, citations)
- Issue 4: AI validation & error recovery (missing fields, format checks, conditional logic, correction prompts)
- Issue 6: AI fidelity checking & citation grounding (fidelity score, weakened conditions, altered numbers)
- Guided Q&A & Accessibility Presets (simple language, reduced cognitive load, screen reader)

Connection to project:
Provides typed data contracts between AI service implementations (in app/services/),
REST API endpoints (in app/routes/ai.py), and frontend consuming clients.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.schemas.form import FormDeadline, FormField, FormRule, FormWarning


class AccessibilityMode(str, Enum):
    SIMPLE_LANGUAGE = "simple_language"
    REDUCED_COGNITIVE_LOAD = "reduced_cognitive_load"
    SCREEN_READER = "screen_reader"
    STANDARD = "standard"


class SourceCitation(BaseModel):
    """Pinpoints where a requirement, field, or condition originated in the source document."""
    quote: str
    start_char: int | None = None
    end_char: int | None = None
    page_number: int | None = None
    section_title: str | None = None


class ExtractedAttachment(BaseModel):
    """Documents or proofs required by the form (e.g., paystub, photo ID)."""
    name: str
    description: str
    required: bool = True
    citation: SourceCitation | None = None


class AIExtractionRequest(BaseModel):
    """Request payload for AI document extraction from raw text or uploaded content."""
    document_text: str | None = None
    file_name: str | None = "document"
    domain_preset: str | None = "general"


class AIExtractionResponse(BaseModel):
    """
    Issue 2 structured extraction response.
    Contains fields, rules, deadlines, conditional branches, exceptions, required attachments,
    and citations back to the source text.
    """
    file_name: str
    title: str
    summary: str
    fields: list[FormField]
    rules: list[FormRule]
    deadlines: list[FormDeadline]
    exceptions: list[str]
    warnings: list[FormWarning]
    required_attachments: list[ExtractedAttachment] = Field(default_factory=list)
    next_steps: list[str]
    confidence: float
    citations: list[SourceCitation] = Field(default_factory=list)


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """
    Issue 4 error recovery model.
    Detects invalid or missing answers and provides plain-language correction guidance.
    """
    field_name: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    issue_type: str = Field(description="missing_required, invalid_format, conditional_requirement, or deadline_passed")
    message: str
    correction_prompt: str = Field(description="Empathetic, actionable guidance instructing the user how to fix the issue")
    citation: SourceCitation | None = None


class AIValidationRequest(BaseModel):
    """Validates user inputs against extracted form structure and conditional requirements."""
    fields: list[FormField]
    rules: list[FormRule] = Field(default_factory=list)
    deadlines: list[FormDeadline] = Field(default_factory=list)
    user_answers: dict[str, Any] = Field(default_factory=dict)
    user_context: dict[str, Any] = Field(default_factory=dict, description="Metadata such as applicant age, residency, etc.")


class AIValidationResponse(BaseModel):
    """Result of validating user answers with actionable recovery prompts."""
    is_valid: bool
    can_submit: bool
    total_fields: int
    completed_fields: int
    issues: list[ValidationIssue]
    summary_message: str


class FidelityCheckStatus(str, Enum):
    VERIFIED = "verified"
    FLAGGED = "flagged"
    WEAKENED = "weakened"
    ALTERED_NUMBER = "altered_number"
    OMITTED = "omitted"


class FidelityClaimCheck(BaseModel):
    """
    Issue 6 fidelity checker item.
    Compares an extracted item against the source text to ensure no conditions or numbers were corrupted.
    """
    claim_type: str = Field(description="field, rule, deadline, condition, exception")
    claim_text: str
    status: FidelityCheckStatus
    fidelity_score: float = Field(ge=0.0, le=1.0)
    source_citation: SourceCitation | None = None
    explanation: str


class AIFidelityVerifyRequest(BaseModel):
    """Request payload for the second-pass fidelity verifier."""
    source_text: str
    extracted_fields: list[FormField]
    extracted_rules: list[FormRule] = Field(default_factory=list)
    extracted_deadlines: list[FormDeadline] = Field(default_factory=list)
    extracted_exceptions: list[str] = Field(default_factory=list)


class AIFidelityResponse(BaseModel):
    """Fidelity report flagging omissions, altered numbers, or weakened requirements."""
    overall_fidelity_score: float
    total_checks: int
    verified_count: int
    flagged_count: int
    checks: list[FidelityClaimCheck]
    fidelity_warnings: list[str]


class GuidedQuestion(BaseModel):
    """A single plain-language question adapted to the user's accessibility mode."""
    step_number: int
    field_name: str
    label: str
    question_text: str
    explanation: str
    input_type: str = Field(default="text", description="text, number, date, boolean, select")
    options: list[str] | None = None
    required: bool = False
    accessibility_mode: AccessibilityMode
    citation: SourceCitation | None = None


class GuidedQuestionsRequest(BaseModel):
    """Request to transform extracted form fields into step-by-step guided questions."""
    fields: list[FormField]
    rules: list[FormRule] = Field(default_factory=list)
    mode: AccessibilityMode = AccessibilityMode.SIMPLE_LANGUAGE


class GuidedQuestionsResponse(BaseModel):
    """Response containing ordered questions tailored to the requested accessibility mode."""
    mode: AccessibilityMode
    total_steps: int
    questions: list[GuidedQuestion]
