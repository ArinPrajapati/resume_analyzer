from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from time import sleep

from fastapi.responses import JSONResponse

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

    sleep(3)

    return JSONResponse(
        {
            "match_score": 0,
            "missing_skills": [],
            "strengths": [],
            "recommendation": "Processing logic coming soon...",
        }
    )
