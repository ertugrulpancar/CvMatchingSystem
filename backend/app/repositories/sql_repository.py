from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import AnalysisItemModel, AnalysisModel
from app.repositories.base import NewAnalysis, build_analysis_result
from app.schemas.analysis import AnalysisResult, AnalysisSummary
from app.schemas.requirement import RequirementMatch


class SQLAnalysisRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, user_id: UUID, analysis: NewAnalysis) -> AnalysisResult:
        row = AnalysisModel(
            user_id=user_id,
            job_title=analysis.job_title,
            company_name=analysis.company_name,
            job_text=analysis.job_text,
            cv_source=analysis.cv_source,
            overall_score=analysis.overall_score,
            output_language=analysis.output_language,
            matcher=analysis.matcher,
            model=analysis.model,
            duration_ms=analysis.duration_ms,
            items=[
                AnalysisItemModel(
                    position=position,
                    requirement_text=match.requirement_text,
                    category=match.category.value,
                    importance=match.importance.value,
                    status=match.status.value,
                    evidence=match.evidence,
                    explanation=match.explanation,
                )
                for position, match in enumerate(analysis.matches)
            ],
        )
        self._session.add(row)
        self._session.commit()
        # id ve created_at Postgres tarafında üretiliyor (gen_random_uuid(),
        # now()); satırı DB'den yeniden okuyup gerçek değerleri alıyoruz.
        self._session.refresh(row)

        return build_analysis_result(
            analysis_id=row.id,
            created_at=row.created_at,
            job_title=row.job_title,
            company_name=row.company_name,
            overall_score=row.overall_score,
            matches=analysis.matches,
            output_language=analysis.output_language,
            matcher=analysis.matcher,
        )

    def list_summaries(
        self, user_id: UUID, before: datetime | None, limit: int
    ) -> list[AnalysisSummary]:
        stmt = select(AnalysisModel).where(AnalysisModel.user_id == user_id)
        if before is not None:
            stmt = stmt.where(AnalysisModel.created_at < before)
        stmt = stmt.order_by(AnalysisModel.created_at.desc()).limit(limit)

        rows = self._session.scalars(stmt).all()
        return [
            AnalysisSummary(
                id=row.id,
                created_at=row.created_at,
                job_title=row.job_title,
                company_name=row.company_name,
                overall_score=row.overall_score,
            )
            for row in rows
        ]

    def get(self, user_id: UUID, analysis_id: UUID) -> AnalysisResult | None:
        row = self._session.get(AnalysisModel, analysis_id)
        if row is None or row.user_id != user_id:
            return None

        matches = [
            RequirementMatch(
                requirement_text=item.requirement_text,
                category=item.category,
                importance=item.importance,
                status=item.status,
                evidence=item.evidence,
                explanation=item.explanation,
            )
            for item in row.items
        ]
        return build_analysis_result(
            analysis_id=row.id,
            created_at=row.created_at,
            job_title=row.job_title,
            company_name=row.company_name,
            overall_score=row.overall_score,
            matches=matches,
            output_language=row.output_language,
            matcher=row.matcher,
        )

    def delete(self, user_id: UUID, analysis_id: UUID) -> bool:
        row = self._session.get(AnalysisModel, analysis_id)
        if row is None or row.user_id != user_id:
            return False
        self._session.delete(row)
        self._session.commit()
        return True
