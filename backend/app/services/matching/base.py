from typing import Literal, Protocol

from pydantic import BaseModel

from app.schemas.requirement import RequirementMatch


class MatchResult(BaseModel):
    job_title: str | None
    company_name: str | None
    matches: list[RequirementMatch]


class Matcher(Protocol):
    def match(
        self, job_text: str, cv_text: str, output_language: Literal["tr", "en"]
    ) -> MatchResult: ...
