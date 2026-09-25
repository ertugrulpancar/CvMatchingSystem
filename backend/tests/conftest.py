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

from uuid import UUID, uuid4  # noqa: E402

import pytest  # noqa: E402

from app.api.deps import get_repository  # noqa: E402
from app.core.auth import get_current_user  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.memory_repository import InMemoryAnalysisRepository  # noqa: E402

TEST_USER_ID = uuid4()


@pytest.fixture
def analysis_repository() -> InMemoryAnalysisRepository:
    """API testleri gerçek DB'ye ve gerçek Supabase auth'a değil, InMemory
    repoya ve sahte bir kullanıcıya bağlanır (CLAUDE.md: `get_current_user`
    `app.dependency_overrides` ile değiştirilir)."""
    repository = InMemoryAnalysisRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_current_user] = lambda: TEST_USER_ID
    yield repository
    app.dependency_overrides.pop(get_repository, None)
    app.dependency_overrides.pop(get_current_user, None)


def override_current_user(user_id: UUID) -> None:
    app.dependency_overrides[get_current_user] = lambda: user_id
