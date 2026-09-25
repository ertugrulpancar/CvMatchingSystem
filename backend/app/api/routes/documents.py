from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.schemas.document import ParsedDocument
from app.services.parsing import EmptyTextError, UnsupportedFileTypeError, parse_document

router = APIRouter()


@router.post("/documents/parse", response_model=ParsedDocument)
async def parse_document_endpoint(
    file: UploadFile,
    # Değeri kullanılmıyor; tek amacı bu route'u da PLAN.md §4'teki "tüm
    # /api/v1/* rotaları auth ister" kuralına tabi kılmak (kimliksiz istekler
    # 401 alır).
    _user_id: UUID = Depends(get_current_user),
) -> ParsedDocument:
    settings = get_settings()
    content = await file.read()

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Dosya çok büyük")

    try:
        return parse_document(file.filename or "", content)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except EmptyTextError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
