from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.form import FormExtractionResponse
from app.services.form_extractor import build_mock_extraction, parse_uploaded_content


router = APIRouter()


@router.post("/process", response_model=FormExtractionResponse)
async def process_form(
    file: UploadFile | None = File(default=None),
    document_text: str | None = Form(default=None),
) -> FormExtractionResponse:
    raw_bytes = await file.read() if file is not None else None
    parsed_form = parse_uploaded_content(
        file_name=file.filename if file is not None else None,
        raw_bytes=raw_bytes,
        text=document_text,
        content_type=file.content_type if file is not None else None,
    )
    return build_mock_extraction(parsed_form)