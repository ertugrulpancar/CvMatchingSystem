from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.requirement import RequirementCategory, RequirementMatch


class CategoryScore(BaseModel):
    category: RequirementCategory
    score: int


class AnalysisResult(BaseModel):
    id: UUID
    created_at: datetime
    job_title: str | None
    company_name: str | None
    overall_score: int
    category_scores: list[CategoryScore]
    matches: list[RequirementMatch]
    output_language: Literal["tr", "en"]
    matcher: Literal["llm", "keyword"]


class AnalysisSummary(BaseModel):
    id: UUID
    created_at: datetime
    job_title: str | None
    company_name: str | None
    overall_score: int
