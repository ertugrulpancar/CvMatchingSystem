from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.api.deps import get_repository
from app.core.auth import get_current_user
from app.core.config import get_settings
from app.repositories.base import AnalysisRepository
from app.schemas.analysis import AnalysisResult, AnalysisSummary
from app.services.analysis_service import run_analysis
from app.services.llm.client import GeminiError
from app.services.parsing import EmptyTextError, UnsupportedFileTypeError, parse_document
from app.services.scoring import EmptyRequirementsError

router = APIRouter()


@router.post("/analyses", response_model=AnalysisResult, status_code=201)
async def create_analysis(
    job_text: str = Form(...),
    output_language: Literal["tr", "en"] = Form(...),
    cv_text: str | None = Form(None),
    cv_file: UploadFile | None = File(None),
    user_id: UUID = Depends(get_current_user),
    repository: AnalysisRepository = Depends(get_repository),
) -> AnalysisResult:
    settings = get_settings()

    quota_available = repository.try_reserve_quota(
        user_id=user_id,
        since=datetime.now(UTC) - timedelta(days=1),
        limit=settings.daily_analysis_limit,
    )
    if not quota_available:
        raise HTTPException(status_code=429, detail="Günlük analiz kotası aşıldı")

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
            parsed = parse_document(cv_file.filename or "", content)
        except UnsupportedFileTypeError as exc:
            raise HTTPException(status_code=415, detail=str(exc)) from exc
        except EmptyTextError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        resolved_cv_text, cv_source = parsed.text, parsed.source
    else:
        resolved_cv_text, cv_source = cv_text or "", "text"

    if len(resolved_cv_text) > settings.max_cv_chars:
        raise HTTPException(status_code=422, detail="CV metni çok uzun")
    if len(job_text) > settings.max_job_chars:
        raise HTTPException(status_code=422, detail="İlan metni çok uzun")

    try:
        return run_analysis(
            user_id=user_id,
            cv_text=resolved_cv_text,
            cv_source=cv_source,
            job_text=job_text,
            output_language=output_language,
            repository=repository,
        )
    except EmptyRequirementsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except GeminiError as exc:
        # str(exc) kasıtlı olarak kullanıcıya dönülmüyor: SDK'nın ham hata
        # mesajı iç sistem detayları içerebilir. `from exc` sayesinde asıl
        # sebep sunucu taraflı traceback'te hâlâ görünür kalır.
        raise HTTPException(
            status_code=502, detail="Gemini isteği başarısız oldu, lütfen tekrar deneyin"
        ) from exc


@router.get("/analyses", response_model=list[AnalysisSummary])
def list_analyses(
    before: datetime | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user),
    repository: AnalysisRepository = Depends(get_repository),
) -> list[AnalysisSummary]:
    return repository.list_summaries(user_id=user_id, before=before, limit=limit)


@router.get("/analyses/{analysis_id}", response_model=AnalysisResult)
def get_analysis(
    analysis_id: UUID,
    user_id: UUID = Depends(get_current_user),
    repository: AnalysisRepository = Depends(get_repository),
) -> AnalysisResult:
    result = repository.get(user_id=user_id, analysis_id=analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
    return result


@router.delete("/analyses/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: UUID,
    user_id: UUID = Depends(get_current_user),
    repository: AnalysisRepository = Depends(get_repository),
) -> None:
    deleted = repository.delete(user_id=user_id, analysis_id=analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analiz bulunamadı")
