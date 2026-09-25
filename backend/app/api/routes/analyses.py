from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.schemas.analysis import AnalysisResult
from app.services.analysis_service import run_analysis
from app.services.parsing import EmptyTextError, UnsupportedFileTypeError, parse_document
from app.services.scoring import EmptyRequirementsError

router = APIRouter()


@router.post("/analyses", response_model=AnalysisResult, status_code=201)
async def create_analysis(
    job_text: str = Form(...),
    output_language: Literal["tr", "en"] = Form(...),
    cv_text: str | None = Form(None),
    cv_file: UploadFile | None = File(None),
) -> AnalysisResult:
    settings = get_settings()

    if bool(cv_file) == bool(cv_text):
        raise HTTPException(
            status_code=400,
            detail="cv_file veya cv_text alanlarından tam olarak biri gönderilmeli",
        )

    if cv_file is not None:
        content = await cv_file.read()
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="Dosya çok büyük")
        try:
            resolved_cv_text = parse_document(cv_file.filename or "", content).text
        except UnsupportedFileTypeError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc
        except EmptyTextError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    else:
        resolved_cv_text = cv_text or ""

    if len(resolved_cv_text) > settings.max_cv_chars:
        raise HTTPException(status_code=422, detail="CV metni çok uzun")
    if len(job_text) > settings.max_job_chars:
        raise HTTPException(status_code=422, detail="İlan metni çok uzun")

    try:
        return run_analysis(
            cv_text=resolved_cv_text, job_text=job_text, output_language=output_language
        )
    except EmptyRequirementsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
