from fastapi.testclient import TestClient

from app.main import app
from app.schemas.form import FormDeadline, FormExtractionResponse, FormField, FormRule, FormWarning
from app.services import form_extractor


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_form_with_text() -> None:
    response = client.post(
        "/api/forms/process",
        data={
            "document_text": (
                "Application Form\n"
                "Applicant name is required.\n"
                "Monthly income must be provided.\n"
                "Submit by March 15.\n"
                "If the applicant is under 18, a parent signature is required."
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fields"]
    assert payload["deadlines"]
    assert payload["exceptions"]
    assert payload["warnings"]
    assert payload["next_steps"]


def test_process_form_with_uploaded_text_file(tmp_path) -> None:
    file_path = tmp_path / "sample_form.txt"
    file_path.write_text(
        "Sample Form\nName is required.\nDue April 1.\nIf you are under 18, parent approval is required.",
        encoding="utf-8",
    )

    with file_path.open("rb") as handle:
        response = client.post(
            "/api/forms/process",
            files={"file": ("sample_form.txt", handle, "text/plain")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "sample_form.txt"
    assert any(field["required"] for field in payload["fields"])


def test_process_form_with_pdf_upload() -> None:
    pdf_bytes = _build_pdf_bytes(
        "Income certificate\nApplicant name: Harsha Example\nMonthly income must be provided.\nSubmit by March 15."
    )

    response = client.post(
        "/api/forms/process",
        files={"file": ("income_certificate.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "income_certificate.pdf"
    assert any(field["name"] == "applicant_name" for field in payload["fields"])
    assert payload["deadlines"]
    assert payload["summary"]


def test_process_form_uses_cloud_ai_when_enabled(monkeypatch) -> None:
    expected_response = FormExtractionResponse(
        file_name="cloud-form.txt",
        title="Cloud Extracted Form",
        summary="Cloud extraction summary",
        fields=[
            FormField(
                name="applicant_name",
                label="Applicant name",
                required=True,
                source_excerpt="Applicant name is required.",
            )
        ],
        rules=[
            FormRule(
                kind="instruction",
                text="Fill the form carefully.",
                source_excerpt="Fill the form carefully.",
            )
        ],
        deadlines=[
            FormDeadline(
                text="Submit by March 15.",
                due_date="March 15",
                source_excerpt="Submit by March 15.",
            )
        ],
        exceptions=["No explicit exception detected."],
        warnings=[
            FormWarning(
                text="Required items must be completed carefully.",
                severity="medium",
                source_excerpt="required items",
            )
        ],
        next_steps=["Complete the form."],
        confidence=0.93,
    )

    monkeypatch.setenv("ACCESSBRIDGE_AI_MODE", "cloud")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(form_extractor, "_call_cloud_extraction", lambda parsed_form: expected_response)

    response = client.post(
        "/api/forms/process",
        data={"document_text": "Applicant name is required. Submit by March 15."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Cloud Extracted Form"
    assert payload["confidence"] == 0.93
    assert payload["fields"][0]["name"] == "applicant_name"


def _build_pdf_bytes(text: str) -> bytes:
    def escape_pdf_text(value: str) -> str:
        return value.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    content_stream = f"BT /F1 18 Tf 72 720 Td ({escape_pdf_text(text)}) Tj ET"

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(content_stream.encode('latin-1'))} >>\nstream\n{content_stream}\nendstream\nendobj\n".encode(
            "latin-1"
        ),
    ]

    header = b"%PDF-1.4\n"
    body = b""
    offsets = [0]

    current_offset = len(header)
    for obj in objects:
        offsets.append(current_offset)
        body += obj
        current_offset += len(obj)

    xref_offset = len(header) + len(body)
    xref_entries = [b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref_entries.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    xref = b"xref\n0 6\n" + b"".join(xref_entries)
    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
        b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )

    return header + body + xref + trailer