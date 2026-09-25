from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.repositories.base import NewAnalysis, build_analysis_result
from app.schemas.analysis import AnalysisResult, AnalysisSummary


class InMemoryAnalysisRepository:
    def __init__(self) -> None:
        self._analyses: dict[UUID, tuple[UUID, AnalysisResult]] = {}

    def save(self, user_id: UUID, analysis: NewAnalysis) -> AnalysisResult:
        analysis_id = uuid4()
        result = build_analysis_result(
            analysis_id=analysis_id,
            created_at=datetime.now(UTC),
            job_title=analysis.job_title,
            company_name=analysis.company_name,
            overall_score=analysis.overall_score,
            matches=analysis.matches,
            output_language=analysis.output_language,
            matcher=analysis.matcher,
        )
        self._analyses[analysis_id] = (user_id, result)
        return result

    def list_summaries(
        self, user_id: UUID, before: datetime | None, limit: int
    ) -> list[AnalysisSummary]:
        results = [
            result
            for owner_id, result in self._analyses.values()
            if owner_id == user_id and (before is None or result.created_at < before)
        ]
        results.sort(key=lambda result: result.created_at, reverse=True)

        return [
            AnalysisSummary(
                id=result.id,
                created_at=result.created_at,
                job_title=result.job_title,
                company_name=result.company_name,
                overall_score=result.overall_score,
            )
            for result in results[:limit]
        ]

    def get(self, user_id: UUID, analysis_id: UUID) -> AnalysisResult | None:
        entry = self._analyses.get(analysis_id)
        if entry is None or entry[0] != user_id:
            return None
        return entry[1]

    def delete(self, user_id: UUID, analysis_id: UUID) -> bool:
        entry = self._analyses.get(analysis_id)
        if entry is None or entry[0] != user_id:
            return False
        del self._analyses[analysis_id]
        return True

    def count_since(self, user_id: UUID, since: datetime) -> int:
        return sum(
            1
            for owner_id, result in self._analyses.values()
            if owner_id == user_id and result.created_at > since
        )
