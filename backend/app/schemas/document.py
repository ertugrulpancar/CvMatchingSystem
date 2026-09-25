from typing import Literal

from pydantic import BaseModel


class ParsedDocument(BaseModel):
    text: str
    source: Literal["pdf", "docx", "text"]
    char_count: int
    page_count: int | None = None
