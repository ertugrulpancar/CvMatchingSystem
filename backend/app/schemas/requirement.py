from enum import StrEnum

from pydantic import BaseModel


class RequirementCategory(StrEnum):
    TECHNICAL_SKILL = "technical_skill"
    TOOL = "tool"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    LANGUAGE = "language"
    SOFT_SKILL = "soft_skill"


class Importance(StrEnum):
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"


class MatchStatus(StrEnum):
    MET = "met"
    PARTIAL = "partial"
    MISSING = "missing"


class RequirementMatch(BaseModel):
    requirement_text: str
    category: RequirementCategory
    importance: Importance
    status: MatchStatus
    evidence: str | None
    explanation: str
