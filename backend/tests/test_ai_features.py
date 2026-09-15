"""
Tests for AccessBridge AI Components

Tests cover:
- Issue 2: AI extraction pipeline (fields, rules, conditions, deadlines, attachments, citations)
- Issue 4: AI validation & error recovery (missing fields, format errors, conditional logic, correction prompts)
- Issue 6: AI fidelity verifier (citations, altered number detection, weakened condition detection)
- Guided Q&A generator: accessibility mode adaptations
"""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai import AccessibilityMode, FidelityCheckStatus
from app.schemas.form import FormDeadline, FormField, FormRule
from tests.test_forms import _build_pdf_bytes


client = TestClient(app)

SAMPLE_FORM_DOCUMENT = (
    "STATE HOUSING AND NUTRITION ASSISTANCE APPLICATION\n\n"
    "Section 1: Applicant Details\n"
    "Full legal name is required for all applicants.\n"
    "Date of birth must be provided.\n"
    "Email address is required for digital notifications.\n"
    "Contact phone number is required.\n"
    "Mailing address must be provided.\n"
    "Monthly gross income must be stated under penalty of perjury.\n"
    "Applicant signature is required to certify statements.\n\n"
    "Section 2: Conditional Requirements & Exceptions\n"
    "If the applicant is under 18 years of age, a parent or guardian signature is required.\n"
    "Applicants with monthly income exceeding $5,000 must attach federal tax return schedule C.\n"
    "Fee waiver is available for households with zero income.\n\n"
    "Section 3: Deadlines & Attachments\n"
    "All application materials must be submitted by March 31, 2026.\n"
    "Applicants must attach recent pay stubs verifying income.\n"
    "A valid government photo ID is required.\n"
)


def test_ai_extract_endpoint_structured_output() -> None:
    """Tests Issue 2: AI extraction produces fields, rules, deadlines, attachments, and citations."""
    response = client.post(
        "/api/ai/extract",
        data={"document_text": SAMPLE_FORM_DOCUMENT},
    )
    assert response.status_code == 200
    data = response.json()

    # Verify structured fields
    field_names = [f["name"] for f in data["fields"]]
    assert "applicant_name" in field_names
    assert "date_of_birth" in field_names
    assert "email" in field_names
    assert "phone_number" in field_names
    assert "monthly_income" in field_names
    assert "signature" in field_names

    # Verify citations exist
    assert len(data["citations"]) > 0
    assert any("name" in c["quote"].lower() for c in data["citations"])

    # Verify rules and conditions
    assert len(data["rules"]) > 0
    assert any(r["kind"] == "condition" for r in data["rules"])

    # Verify deadlines
    assert len(data["deadlines"]) > 0
    assert any("march 31" in (d["due_date"] or "").lower() or "march 31" in d["text"].lower() for d in data["deadlines"])

    # Verify attachments
    assert len(data["required_attachments"]) >= 2
    attachment_names = [a["name"] for a in data["required_attachments"]]
    assert "Proof of Income" in attachment_names
    assert "Government Photo ID" in attachment_names

    # Verify exceptions & warnings
    assert any("18" in exc for exc in data["exceptions"])
    assert len(data["warnings"]) > 0
    assert data["confidence"] > 0.70


def test_ai_extract_endpoint_with_pdf() -> None:
    """Tests Issue 2: PDF binary extraction via AI endpoint."""
    pdf_bytes = _build_pdf_bytes(
        "Application Form\nFull name is required.\nSubmit by April 15, 2026.\nPay stubs required."
    )
    response = client.post(
        "/api/ai/extract",
        files={"file": ("application.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "application.pdf"
    assert any(f["name"] == "applicant_name" for f in data["fields"])
    assert len(data["deadlines"]) > 0


def test_ai_validate_missing_required_fields() -> None:
    """Tests Issue 4: Validation detects missing required fields and generates correction prompts."""
    fields = [
        {"name": "applicant_name", "label": "Full Legal Name", "required": True, "source_excerpt": "Full legal name is required"},
        {"name": "email", "label": "Email Address", "required": True, "source_excerpt": "Email is required"},
    ]
    payload = {
        "fields": fields,
        "rules": [],
        "deadlines": [],
        "user_answers": {"applicant_name": ""},  # missing name and email
        "user_context": {},
    }
    response = client.post("/api/ai/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["can_submit"] is False
    assert len(data["issues"]) >= 2

    # Check that clear correction prompts are present
    prompts = [i["correction_prompt"] for i in data["issues"]]
    assert any("full legal name" in p.lower() for p in prompts)
    assert any("email" in p.lower() for p in prompts)


def test_ai_validate_format_checks() -> None:
    """Tests Issue 4: Validation checks format of email, income, and dates."""
    fields = [
        {"name": "email", "label": "Email Address", "required": True},
        {"name": "monthly_income", "label": "Monthly Income", "required": True},
    ]
    payload = {
        "fields": fields,
        "rules": [],
        "deadlines": [],
        "user_answers": {
            "email": "not-an-email",
            "monthly_income": "invalid_number_abc",
        },
        "user_context": {},
    }
    response = client.post("/api/ai/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False

    issue_types = [i["issue_type"] for i in data["issues"]]
    assert "invalid_format" in issue_types


def test_ai_validate_conditional_minor_logic() -> None:
    """Tests Issue 4: Conditional logic requires parent signature if applicant is under 18."""
    fields = [
        {"name": "applicant_name", "label": "Full Name", "required": True},
        {"name": "date_of_birth", "label": "Date of Birth", "required": True},
        {"name": "parent_guardian_signature", "label": "Parent Signature", "required": False},
    ]
    rules = [
        {"kind": "condition", "text": "If the applicant is under 18, a parent or guardian signature is required."}
    ]

    # Case A: Under 18 with no parent signature -> should fail
    payload_fail = {
        "fields": fields,
        "rules": rules,
        "deadlines": [],
        "user_answers": {
            "applicant_name": "Alex Minor",
            "date_of_birth": "2012-05-10",  # Under 18
        },
        "user_context": {"applicant_age": 14},
    }
    res_fail = client.post("/api/ai/validate", json=payload_fail)
    assert res_fail.status_code == 200
    data_fail = res_fail.json()
    assert data_fail["is_valid"] is False
    assert any(i["field_name"] == "parent_guardian_signature" for i in data_fail["issues"])
    assert any("parent or legal guardian must sign" in i["correction_prompt"].lower() for i in data_fail["issues"])

    # Case B: Under 18 with parent signature -> should pass
    payload_pass = {
        "fields": fields,
        "rules": rules,
        "deadlines": [],
        "user_answers": {
            "applicant_name": "Alex Minor",
            "date_of_birth": "2012-05-10",
            "parent_guardian_signature": "Parent Mary Minor",
        },
        "user_context": {"applicant_age": 14},
    }
    res_pass = client.post("/api/ai/validate", json=payload_pass)
    assert res_pass.status_code == 200
    data_pass = res_pass.json()
    assert data_pass["is_valid"] is True
    assert data_pass["can_submit"] is True


def test_ai_fidelity_verifier_pass() -> None:
    """Tests Issue 6: Fidelity verifier verifies matching rules and fields against source text."""
    payload = {
        "source_text": SAMPLE_FORM_DOCUMENT,
        "extracted_fields": [
            {"name": "applicant_name", "label": "Full legal name", "required": True},
            {"name": "date_of_birth", "label": "Date of birth", "required": True},
        ],
        "extracted_rules": [
            {"kind": "condition", "text": "If the applicant is under 18 years of age, a parent or guardian signature is required."}
        ],
        "extracted_deadlines": [
            {"text": "All application materials must be submitted by March 31, 2026.", "due_date": "March 31, 2026"}
        ],
        "extracted_exceptions": [
            "Applicants under 18 require parental or legal guardian consent."
        ],
    }
    response = client.post("/api/ai/verify-fidelity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_fidelity_score"] >= 0.85
    assert data["verified_count"] >= 3
    assert len(data["checks"]) >= 4
    # Ensure source citations are attached
    assert any(c["source_citation"] is not None for c in data["checks"])


def test_ai_fidelity_verifier_detects_altered_numbers() -> None:
    """Tests Issue 6: Fidelity verifier detects corrupted/altered numbers in rules."""
    payload = {
        "source_text": "Applicants with monthly income exceeding $5,000 must attach federal tax return.",
        "extracted_fields": [],
        "extracted_rules": [
            # Altered number: $50,000 instead of $5,000
            {"kind": "condition", "text": "Applicants with monthly income exceeding $50,000 must attach federal tax return."}
        ],
        "extracted_deadlines": [],
        "extracted_exceptions": [],
    }
    response = client.post("/api/ai/verify-fidelity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any(c["status"] == FidelityCheckStatus.ALTERED_NUMBER for c in data["checks"])
    assert any("differ from the source" in w for w in data["fidelity_warnings"])


def test_ai_fidelity_verifier_detects_weakened_conditions() -> None:
    """Tests Issue 6: Fidelity verifier detects when mandatory requirement is weakened to optional."""
    payload = {
        "source_text": "Applicant must submit 3 recent pay stubs.",
        "extracted_fields": [],
        "extracted_rules": [
            # Weakened to optional
            {"kind": "rule", "text": "It is optional for applicant to submit 3 recent pay stubs."}
        ],
        "extracted_deadlines": [],
        "extracted_exceptions": [],
    }
    response = client.post("/api/ai/verify-fidelity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any(c["status"] == FidelityCheckStatus.WEAKENED for c in data["checks"])
    assert any("weakened" in w for w in data["fidelity_warnings"])


def test_guided_questions_accessibility_modes() -> None:
    """Tests Guided Q&A: transforms fields into step questions adapted to accessibility presets."""
    fields = [
        {"name": "applicant_name", "label": "Full Legal Name", "required": True},
        {"name": "monthly_income", "label": "Monthly Gross Income", "required": True},
    ]

    # Test Simple Language Mode
    res_simple = client.post(
        "/api/ai/guided-questions",
        json={"fields": fields, "rules": [], "mode": AccessibilityMode.SIMPLE_LANGUAGE},
    )
    assert res_simple.status_code == 200
    simple_data = res_simple.json()
    assert simple_data["mode"] == "simple_language"
    assert simple_data["total_steps"] == 2
    assert "What is your full name?" in simple_data["questions"][0]["question_text"]

    # Test Reduced Cognitive Load Mode
    res_cog = client.post(
        "/api/ai/guided-questions",
        json={"fields": fields, "rules": [], "mode": AccessibilityMode.REDUCED_COGNITIVE_LOAD},
    )
    assert res_cog.status_code == 200
    cog_data = res_cog.json()
    assert cog_data["mode"] == "reduced_cognitive_load"
    assert "Your Full Name" in cog_data["questions"][0]["question_text"]
    assert "Example:" in cog_data["questions"][0]["explanation"]

    # Test Screen Reader Mode
    res_sr = client.post(
        "/api/ai/guided-questions",
        json={"fields": fields, "rules": [], "mode": AccessibilityMode.SCREEN_READER},
    )
    assert res_sr.status_code == 200
    sr_data = res_sr.json()
    assert sr_data["mode"] == "screen_reader"
    assert "official records" in sr_data["questions"][0]["question_text"]

    # Test Standard Mode
    res_std = client.post(
        "/api/ai/guided-questions",
        json={"fields": fields, "rules": [], "mode": AccessibilityMode.STANDARD},
    )
    assert res_std.status_code == 200
    std_data = res_std.json()
    assert std_data["mode"] == "standard"
    assert "Full Legal Name" in std_data["questions"][0]["question_text"]


def test_ai_fidelity_verifier_detects_omitted_critical_clause() -> None:
    """Tests Issue 6: Fidelity verifier detects critical legal clauses omitted in extraction."""
    payload = {
        "source_text": "Applicant must sign under penalty of perjury. Application fee is non-refundable.",
        "extracted_fields": [],
        "extracted_rules": [],
        "extracted_deadlines": [],
        "extracted_exceptions": [],
    }
    response = client.post("/api/ai/verify-fidelity", json=payload)
    assert response.status_code == 200
    data = response.json()
    statuses = [c["status"] for c in data["checks"]]
    assert FidelityCheckStatus.OMITTED in statuses


def test_ai_validate_deadline_warning() -> None:
    """Tests Issue 4: Validation warns if a submission deadline has already expired."""
    fields = [{"name": "applicant_name", "label": "Full Name", "required": True}]
    deadlines = [{"text": "Submit by 2020-01-01", "due_date": "2020-01-01"}]
    payload = {
        "fields": fields,
        "rules": [],
        "deadlines": deadlines,
        "user_answers": {"applicant_name": "Jane Doe"},
        "user_context": {},
    }
    response = client.post("/api/ai/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any(i["issue_type"] == "deadline_passed" for i in data["issues"])

