from pathlib import Path

from app.schemas.document import ParsedDocument
from app.services.parsing.docx_parser import parse_docx
from app.services.parsing.pdf_parser import parse_pdf

MIN_TEXT_CHARS = 50


class UnsupportedFileTypeError(Exception):
    pass


class EmptyTextError(Exception):
    pass


def parse_document(filename: str, content: bytes) -> ParsedDocument:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text, page_count = parse_pdf(content)
        source = "pdf"
    elif extension == ".docx":
        text, page_count = parse_docx(content)
        source = "docx"
    else:
        raise UnsupportedFileTypeError(f"Desteklenmeyen dosya türü: {extension or 'uzantısız'}")

    if len(text.strip()) < MIN_TEXT_CHARS:
        raise EmptyTextError("Dosyadan metin çıkarılamadı, taranmış bir PDF olabilir")

    return ParsedDocument(text=text, source=source, char_count=len(text), page_count=page_count)
