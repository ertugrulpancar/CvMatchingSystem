from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

# libpq/psycopg bu parametreyi tanımıyor ve bağlantıyı reddediyor. Supabase
# dashboard'unun "ORM" sekmesi Prisma'ya özel bu parametreyi ekliyor; biz
# psycopg kullandığımız için temizliyoruz.
_UNSUPPORTED_QUERY_PARAMS = {"pgbouncer"}


def normalize_database_url(url: str) -> str:
    # SQLAlchemy sürücü belirtilmezse psycopg2'yi arar; biz psycopg (v3)
    # kullandığımız için şemayı açıkça belirtiyoruz (PLAN.md §7). Alembic'in
    # env.py'si de aynı URL'i kullandığı için bu fonksiyon dışa açık.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in _UNSUPPORTED_QUERY_PARAMS]
    return urlunsplit(parts._replace(query=urlencode(query)))


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        normalize_database_url(settings.database_url),
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
    )


@contextmanager
def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
