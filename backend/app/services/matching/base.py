from typing import Literal, Protocol

from app.schemas.requirement import RequirementMatch


class Matcher(Protocol):
    def match(
        self, job_text: str, cv_text: str, output_language: Literal["tr", "en"]
    ) -> list[RequirementMatch]: ...
