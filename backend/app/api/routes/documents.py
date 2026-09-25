from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import get_settings
from app.schemas.document import ParsedDocument
from app.services.parsing import EmptyTextError, UnsupportedFileTypeError, parse_document

router = APIRouter()


@router.post("/documents/parse", response_model=ParsedDocument)
async def parse_document_endpoint(file: UploadFile) -> ParsedDocument:
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
