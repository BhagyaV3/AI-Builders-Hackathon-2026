from fastapi.testclient import TestClient

from app.main import app


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