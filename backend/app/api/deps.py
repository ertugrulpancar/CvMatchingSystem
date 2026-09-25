from collections.abc import Iterator

from app.core.db import get_session
from app.repositories.base import AnalysisRepository
from app.repositories.sql_repository import SQLAnalysisRepository


def get_repository() -> Iterator[AnalysisRepository]:
    with get_session() as session:
        yield SQLAnalysisRepository(session)
