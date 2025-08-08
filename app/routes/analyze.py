from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
import io

from utils.extract_text_pdf import extract_text_from_pdf
from services.llm import generate_response

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(..., description="Resume PDF file"),
    jd_file: Optional[UploadFile] = File(
        None, description="Optional JD PDF file if not providing jd_text"
    ),
    jd_text: Optional[str] = Form(
        None, description="Optional JD text if not uploading a JD PDF"
    ),
):
    # Validate resume (must be PDF)
    if not resume_file or resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")

    # Determine JD source: text or PDF
    jd_content: Optional[str] = None

    if jd_text and jd_text.strip():
        jd_content = jd_text.strip()
    else:
        if not jd_file:
            raise HTTPException(
                status_code=400,
                detail="Provide either jd_text (text) or jd_file (PDF)",
            )
        if jd_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="JD must be a PDF file")

    # Read files and extract text
    resume_bytes = io.BytesIO(await resume_file.read())
    resume_content = extract_text_from_pdf(resume_bytes)

    if jd_content is None:
        # mypy/pyright: jd_file is validated above when jd_content is None
        assert jd_file is not None
        jd_bytes = io.BytesIO(await jd_file.read())
        jd_content = extract_text_from_pdf(jd_bytes)

    return JSONResponse(generate_response(jd_content, resume_content))
