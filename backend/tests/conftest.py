import os

# Testler asla gerçek Gemini'ye veya gerçek bir veritabanına bağlanmamalı
# (CLAUDE.md). Geliştiricinin backend/.env dosyasında MATCHER=llm ayarlı olsa
# bile, pydantic-settings OS ortam değişkenlerini .env dosyasından önce
# okuduğu için burada set edilen değerler .env'i ezer ve testleri güvenli
# varsayılanlara sabitler. conftest.py, pytest tarafından bu dizindeki diğer
# test modülleri (ve onların `app.main` import'ları) import edilmeden önce
# otomatik olarak yüklenir.
os.environ["MATCHER"] = "keyword"
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = ""

import pytest  # noqa: E402

from app.api.deps import get_repository  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.memory_repository import InMemoryAnalysisRepository  # noqa: E402


@pytest.fixture
def analysis_repository() -> InMemoryAnalysisRepository:
    """API testleri gerçek DB'ye değil, bu InMemory repoya yazar (CLAUDE.md)."""
    repository = InMemoryAnalysisRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    yield repository
    app.dependency_overrides.pop(get_repository, None)
