from pathlib import Path

import pytest

from app.services.parsing import EmptyTextError, UnsupportedFileTypeError, parse_document

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_pdf_extracts_turkish_text():
    content = (FIXTURES / "cv_tr.pdf").read_bytes()

    result = parse_document("cv_tr.pdf", content)

    assert result.source == "pdf"
    assert result.page_count == 1
    assert "Ayşe Yılmaz" in result.text
    assert "İstanbul, Türkiye" in result.text
    assert result.char_count == len(result.text)


def test_parse_docx_reads_paragraphs_and_table_cells():
    content = (FIXTURES / "cv_en.docx").read_bytes()

    result = parse_document("cv_en.docx", content)

    assert result.source == "docx"
    assert result.page_count is None
    assert "John Smith" in result.text
    assert "Machine Learning" in result.text  # table cell


def test_parse_unsupported_extension_raises():
    with pytest.raises(UnsupportedFileTypeError):
        parse_document("job_tr.txt", (FIXTURES / "job_tr.txt").read_bytes())


def test_parse_scanned_pdf_raises_empty_text_error():
    content = (FIXTURES / "cv_scanned.pdf").read_bytes()

    with pytest.raises(EmptyTextError):
        parse_document("cv_scanned.pdf", content)
