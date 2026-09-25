from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)
FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_pdf_returns_200(authenticated_user):
    content = (FIXTURES / "cv_tr.pdf").read_bytes()

    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("cv_tr.pdf", content, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "pdf"
    assert "Ayşe Yılmaz" in body["text"]


def test_parse_unsupported_extension_returns_415(authenticated_user):
    content = (FIXTURES / "job_tr.txt").read_bytes()

    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("job_tr.txt", content, "text/plain")},
    )

    assert response.status_code == 415


def test_parse_scanned_pdf_returns_422(authenticated_user):
    content = (FIXTURES / "cv_scanned.pdf").read_bytes()

    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("cv_scanned.pdf", content, "application/pdf")},
    )

    assert response.status_code == 422


def test_parse_oversized_file_returns_413(authenticated_user):
    oversized = b"0" * (get_settings().max_upload_bytes + 1)

    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("cv_tr.pdf", oversized, "application/pdf")},
    )

    assert response.status_code == 413


def test_parse_without_auth_returns_401():
    content = (FIXTURES / "cv_tr.pdf").read_bytes()

    response = client.post(
        "/api/v1/documents/parse",
        files={"file": ("cv_tr.pdf", content, "application/pdf")},
    )

    assert response.status_code == 401
