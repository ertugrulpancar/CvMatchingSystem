import io

import pdfplumber


def parse_pdf(content: bytes) -> tuple[str, int]:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages_text), len(pdf.pages)
