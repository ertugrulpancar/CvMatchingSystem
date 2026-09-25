from pydantic import BaseModel

from app.schemas.requirement import Importance, MatchStatus, RequirementCategory

# Bu dosya app/schemas/'tan bilinçli olarak ayrı: Gemini'nin response_schema
# özelliği JSON Schema'nın yalnızca bir alt kümesini destekliyor (ör. alan
# varsayılan değerleri sorun çıkarabiliyor), bu yüzden hiçbir alanda default
# yok. API şemaları değişirse bu dosyanın değişmesi gerekmez (PLAN.md §2).


class ExtractedRequirement(BaseModel):
    requirement_text: str
    category: RequirementCategory
    importance: Importance


class JobExtraction(BaseModel):
    job_title: str | None
    company_name: str | None
    requirements: list[ExtractedRequirement]


class LLMMatchItem(BaseModel):
    requirement_index: int
    status: MatchStatus
    evidence: str | None
    explanation: str


class LLMMatchResponse(BaseModel):
    matches: list[LLMMatchItem]
