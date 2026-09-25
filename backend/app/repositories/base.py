from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel

from app.schemas.analysis import AnalysisResult, AnalysisSummary
from app.schemas.requirement import RequirementMatch
from app.services.scoring import calculate_category_scores


class NewAnalysis(BaseModel):
    job_title: str | None
    company_name: str | None
    job_text: str
    cv_source: Literal["pdf", "docx", "text"]
    overall_score: int
    output_language: Literal["tr", "en"]
    matcher: Literal["llm", "keyword"]
    model: str | None
    duration_ms: int
    matches: list[RequirementMatch]


class AnalysisRepository(Protocol):
    def save(self, user_id: UUID, analysis: NewAnalysis) -> AnalysisResult: ...

    def list_summaries(
        self, user_id: UUID, before: datetime | None, limit: int
    ) -> list[AnalysisSummary]: ...

    def get(self, user_id: UUID, analysis_id: UUID) -> AnalysisResult | None: ...

    def delete(self, user_id: UUID, analysis_id: UUID) -> bool: ...

    def count_since(self, user_id: UUID, since: datetime) -> int: ...

    def try_reserve_quota(self, user_id: UUID, since: datetime, limit: int) -> bool:
        """`count_since(...) < limit` ile aynı sonucu döner, ama bunu aynı
        kullanıcının eşzamanlı istekleri arasında atomik yapar (bkz. SQL
        implementasyonundaki advisory lock). Route katmanı artık "say, sonra
        karşılaştır" yapmak yerine bu tek metodu çağırır; aradaki fark, sayma
        ve karşılaştırmanın artık bölünemez (aynı anda başka bir isteğin araya
        giremeyeceği) bir işlem olması."""
        ...


def build_analysis_result(
    *,
    analysis_id: UUID,
    created_at: datetime,
    job_title: str | None,
    company_name: str | None,
    overall_score: int,
    matches: list[RequirementMatch],
    output_language: Literal["tr", "en"],
    matcher: Literal["llm", "keyword"],
) -> AnalysisResult:
    # category_scores DB'de saklanmaz, her okumada matches'tan hesaplanır
    # (PLAN.md §3b) — bu yüzden save() ve get() aynı yardımcıyı paylaşır.
    return AnalysisResult(
        id=analysis_id,
        created_at=created_at,
        job_title=job_title,
        company_name=company_name,
        overall_score=overall_score,
        category_scores=calculate_category_scores(matches),
        matches=matches,
        output_language=output_language,
        matcher=matcher,
    )
