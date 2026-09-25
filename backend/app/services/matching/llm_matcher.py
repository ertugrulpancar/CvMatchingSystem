from typing import Literal

from app.schemas.requirement import MatchStatus, RequirementMatch
from app.services.llm.client import generate_structured
from app.services.llm.prompts import build_extraction_prompt, build_matching_prompt
from app.services.llm.schemas import JobExtraction, LLMMatchResponse
from app.services.matching.base import MatchResult

_MISSING_INDEX_EXPLANATION = {
    "tr": "Bu gereksinim için LLM'den bir sonuç alınamadı.",
    "en": "No result was returned by the LLM for this requirement.",
}


class LLMMatcher:
    def match(
        self, job_text: str, cv_text: str, output_language: Literal["tr", "en"]
    ) -> MatchResult:
        extraction = generate_structured(build_extraction_prompt(job_text), JobExtraction)

        if not extraction.requirements:
            return MatchResult(
                job_title=extraction.job_title, company_name=extraction.company_name, matches=[]
            )

        match_response = generate_structured(
            build_matching_prompt(extraction.requirements, cv_text, output_language),
            LLMMatchResponse,
        )
        items_by_index = {item.requirement_index: item for item in match_response.matches}

        matches: list[RequirementMatch] = []
        for index, requirement in enumerate(extraction.requirements):
            item = items_by_index.get(index)
            if item is None:
                matches.append(
                    RequirementMatch(
                        requirement_text=requirement.requirement_text,
                        category=requirement.category,
                        importance=requirement.importance,
                        status=MatchStatus.MISSING,
                        evidence=None,
                        explanation=_MISSING_INDEX_EXPLANATION[output_language],
                    )
                )
                continue

            matches.append(
                RequirementMatch(
                    requirement_text=requirement.requirement_text,
                    category=requirement.category,
                    importance=requirement.importance,
                    status=item.status,
                    evidence=item.evidence,
                    explanation=item.explanation,
                )
            )

        return MatchResult(
            job_title=extraction.job_title, company_name=extraction.company_name, matches=matches
        )
