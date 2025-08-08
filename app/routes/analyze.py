from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from time import sleep
from fastapi.responses import JSONResponse
from utils.extract_text_pdf import extract_text_from_pdf
import io

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    jd_text: UploadFile = File(...),
):
    if not resume_file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")
    if not jd_text.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")

    resume_bytes = io.BytesIO(await resume_file.read())
    jd_bytes = io.BytesIO(await jd_text.read())

    resume_content = extract_text_from_pdf(resume_bytes)
    jd_content = extract_text_from_pdf(jd_bytes)

    return JSONResponse(
        {
            "match_score": 0,
            "missing_skills": [],
            "strengths": [],
            "recommendation": "Processing logic coming soon...",
            "resume_content": resume_content[:500],
            "jd_content": jd_content[:500],
        }
    )
