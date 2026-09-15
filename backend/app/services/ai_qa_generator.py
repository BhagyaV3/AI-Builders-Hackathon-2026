"""
AI Guided Q&A & Accessibility Mode Generator

What this feature does:
Transforms dense, bureaucratic form fields into an interactive, step-by-step
guided questionnaire adapted to four distinct accessibility modes:
1. `simple_language`: Rewrites formal jargon into 5th-grade everyday English with friendly explanations.
2. `reduced_cognitive_load`: Strips away extraneous text, provides bite-sized, single-focus prompts and clear examples.
3. `screen_reader`: Includes verbose, descriptive labels, explicit aria guidance, and context for assistive tech.
4. `standard`: Preserves original formal phrasing for users who prefer legal precision.

How it connects to the rest of the project:
1. Connects to `app.routes.ai.generate_guided_questions_ai` to power `/api/ai/guided-questions`.
2. Serves the frontend guided question-by-question flow (Issue 3 & Issue 5).
3. Attaches source citations to every generated question so users can cross-reference the original form anytime.
"""

from __future__ import annotations

from app.schemas.ai import (
    AccessibilityMode,
    GuidedQuestion,
    GuidedQuestionsRequest,
    GuidedQuestionsResponse,
    SourceCitation,
)
from app.schemas.form import FormField, FormRule


# Plain language translation dictionary for common bureaucratic field names
PLAIN_LANGUAGE_MAP = {
    "applicant_name": {
        "simple_language": ("What is your full name?", "Type your first and last name, just as it appears on your ID."),
        "reduced_cognitive_load": ("Your Full Name", "Example: Jane Doe"),
        "screen_reader": ("Enter applicant's full legal name as it appears on official records.", "This field is required for applicant identification."),
    },
    "date_of_birth": {
        "simple_language": ("When were you born?", "Pick your birth date. This helps determine which program rules apply to you."),
        "reduced_cognitive_load": ("Date of Birth", "Example: 1990-05-15"),
        "screen_reader": ("Enter your date of birth in year-month-day format.", "Used to verify age eligibility and conditional requirements."),
    },
    "monthly_income": {
        "simple_language": ("How much money do you make each month before taxes?", "Include earnings from all jobs or benefits you receive in a typical month."),
        "reduced_cognitive_load": ("Monthly Income ($)", "Example: 2400"),
        "screen_reader": ("Enter total monthly gross income in US dollars.", "Gross income before taxes or deductions."),
    },
    "income": {
        "simple_language": ("How much money do you make each month before taxes?", "Include earnings from all jobs or benefits you receive in a typical month."),
        "reduced_cognitive_load": ("Monthly Income ($)", "Example: 2400"),
        "screen_reader": ("Enter total monthly gross income in US dollars.", "Gross income before taxes or deductions."),
    },
    "mailing_address": {
        "simple_language": ("Where should we send your mail?", "Enter your street address, apartment number, city, state, and zip code."),
        "reduced_cognitive_load": ("Mailing Address", "Example: 123 Main St, Springfield, IL 62701"),
        "screen_reader": ("Enter complete mailing address including street, city, state, and postal code.", "Used for written correspondence and notices."),
    },
    "address": {
        "simple_language": ("Where should we send your mail?", "Enter your street address, apartment number, city, state, and zip code."),
        "reduced_cognitive_load": ("Mailing Address", "Example: 123 Main St, Springfield, IL 62701"),
        "screen_reader": ("Enter complete mailing address including street, city, state, and postal code.", "Used for written correspondence and notices."),
    },
    "email": {
        "simple_language": ("What is your email address?", "We will send your confirmation and application status updates here."),
        "reduced_cognitive_load": ("Email Address", "Example: yourname@email.com"),
        "screen_reader": ("Enter your primary email address.", "Required to receive digital confirmation and notices."),
    },
    "phone_number": {
        "simple_language": ("What is the best phone number to reach you?", "A mobile or home phone number where a caseworker can reach you if needed."),
        "reduced_cognitive_load": ("Phone Number", "Example: 555-123-4567"),
        "screen_reader": ("Enter primary telephone number with area code.", "Used by caseworkers for follow-up questions."),
    },
    "signature": {
        "simple_language": ("Please sign your name to confirm everything is true.", "Type your full name as your electronic signature to certify your answers."),
        "reduced_cognitive_load": ("Electronic Signature", "Type your full name to sign"),
        "screen_reader": ("Electronic signature confirmation field.", "Typing your legal name here serves as an official electronic signature under penalty of perjury."),
    },
    "parent_guardian_signature": {
        "simple_language": ("Parent or Guardian signature (if you are under 18)", "If you are under 18 years old, a parent or legal guardian must type their name here."),
        "reduced_cognitive_load": ("Parent / Guardian Signature", "Only needed if under 18"),
        "screen_reader": ("Parent or legal guardian signature field for applicants under age 18.", "Required by regulation if the applicant is a minor."),
    },
    "academic_score": {
        "simple_language": ("What is your most recent GPA or grade average?", "Enter your overall grade point average or test score from your school."),
        "reduced_cognitive_load": ("GPA / Score", "Example: 3.5"),
        "screen_reader": ("Enter applicant's cumulative grade point average (GPA) or academic score.", "Academic verification requirement."),
    },
}


def generate_guided_questions(request: GuidedQuestionsRequest) -> GuidedQuestionsResponse:
    """
    Transforms extracted form fields into plain-language, step-by-step questions
    adapted to the chosen accessibility mode.
    """
    fields = request.fields
    mode = request.mode
    questions: list[GuidedQuestion] = []

    for index, field in enumerate(fields, start=1):
        field_key = field.name.lower()

        # Check if mapped to a known plain-language preset
        preset = PLAIN_LANGUAGE_MAP.get(field_key)

        if preset and mode in preset:
            q_text, explanation = preset[mode]
        else:
            # Fallback dynamic adaptation based on mode
            q_text, explanation = _adapt_dynamically(field, mode)

        # Detect input type
        input_type = _infer_input_type(field.name)

        citation = SourceCitation(quote=field.source_excerpt) if field.source_excerpt else None

        questions.append(
            GuidedQuestion(
                step_number=index,
                field_name=field.name,
                label=field.label,
                question_text=q_text,
                explanation=explanation,
                input_type=input_type,
                required=field.required,
                accessibility_mode=mode,
                citation=citation,
            )
        )

    return GuidedQuestionsResponse(
        mode=mode,
        total_steps=len(questions),
        questions=questions,
    )


def _adapt_dynamically(field: FormField, mode: AccessibilityMode) -> tuple[str, str]:
    """Generates dynamic phrasing if field is not in the static map."""
    label = field.label

    if mode == AccessibilityMode.SIMPLE_LANGUAGE:
        q_text = f"Please provide your {label.lower()}."
        explanation = f"Answer this step according to your records. This is {'required' if field.required else 'optional'}."
    elif mode == AccessibilityMode.REDUCED_COGNITIVE_LOAD:
        q_text = label
        explanation = "Required" if field.required else "Optional"
    elif mode == AccessibilityMode.SCREEN_READER:
        q_text = f"Form input {field.name}: {label}."
        explanation = f"{'Mandatory required input' if field.required else 'Optional input'}. Please provide value."
    else:  # STANDARD
        q_text = f"Enter {label}"
        explanation = f"Official form requirement for {label}."

    return q_text, explanation


def _infer_input_type(field_name: str) -> str:
    """Infers appropriate HTML input type for the field."""
    name_lower = field_name.lower()
    if "date" in name_lower or "dob" in name_lower:
        return "date"
    if "email" in name_lower:
        return "email"
    if "phone" in name_lower or "tel" in name_lower:
        return "tel"
    if "income" in name_lower or "amount" in name_lower or "salary" in name_lower or "gpa" in name_lower:
        return "number"
    if "signature" in name_lower:
        return "text"
    if "checkbox" in name_lower or "agree" in name_lower or "is_" in name_lower:
        return "boolean"
    return "text"
