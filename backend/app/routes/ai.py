"""
AI API Routes

What this file does:
Exposes REST endpoints for all AI components:
1. `POST /api/ai/extract`: Executes the structured extraction pipeline on uploaded files or text.
2. `POST /api/ai/validate`: Validates user answers, checks conditional branches and deadlines, and returns plain-language correction prompts (Issue 4).
3. `POST /api/ai/verify-fidelity`: Executes the second-pass verifier comparing extracted claims against original source text to detect altered numbers, weakened conditions, and omissions (Issue 6).
4. `POST /api/ai/guided-questions`: Generates plain-language guided questions adapted to accessibility modes (Issue 3 & Issue 5).

How it connects to the rest of the project:
Provides the HTTP interface that the AccessBridge frontend and integration pipeline call to transform forms into interactive, verified workflows.
"""

from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.ai import (
    AIExtractionResponse,
    AIFidelityResponse,
    AIFidelityVerifyRequest,
    AIValidationRequest,
    AIValidationResponse,
    GuidedQuestionsRequest,
    GuidedQuestionsResponse,
)
from app.services.ai_extractor import extract_form_ai
from app.services.ai_qa_generator import generate_guided_questions
from app.services.ai_validator import validate_user_answers
from app.services.ai_verifier import verify_extraction_fidelity
from app.services.form_extractor import parse_uploaded_content


router = APIRouter()


@router.post("/extract", response_model=AIExtractionResponse)
async def extract_form_endpoint(
    file: UploadFile | None = File(default=None),
    document_text: str | None = Form(default=None),
) -> AIExtractionResponse:
    """
    Issue 2: AI extraction endpoint.
    Accepts an uploaded file (PDF/TXT) or pasted document text and returns a rich
    structured schema with fields, rules, deadlines, attachments, and source citations.
    """
    raw_bytes = await file.read() if file is not None else None
    parsed_form = parse_uploaded_content(
        file_name=file.filename if file is not None else None,
        raw_bytes=raw_bytes,
        text=document_text,
        content_type=file.content_type if file is not None else None,
    )
    return extract_form_ai(parsed_form)


@router.post("/validate", response_model=AIValidationResponse)
def validate_answers_endpoint(payload: AIValidationRequest) -> AIValidationResponse:
    """
    Issue 4: AI validation & error recovery endpoint.
    Validates user answers against form constraints, evaluates conditional rules
    (such as minor signature requirements), and provides clear correction guidance.
    """
    return validate_user_answers(payload)


@router.post("/verify-fidelity", response_model=AIFidelityResponse)
def verify_fidelity_endpoint(payload: AIFidelityVerifyRequest) -> AIFidelityResponse:
    """
    Issue 6: AI fidelity verifier endpoint.
    Compares extracted claims and rules against the original source document to ensure
    no numbers were altered and no conditions were weakened during simplification.
    """
    return verify_extraction_fidelity(payload)


@router.post("/guided-questions", response_model=GuidedQuestionsResponse)
def guided_questions_endpoint(payload: GuidedQuestionsRequest) -> GuidedQuestionsResponse:
    """
    Guided Q&A endpoint.
    Transforms extracted form fields into step-by-step plain-language questions
    adapted to the user's selected accessibility mode.
    """
    return generate_guided_questions(payload)
