import time
from typing import Literal
from uuid import UUID

from app.core.config import get_settings
from app.repositories.base import AnalysisRepository, NewAnalysis
from app.schemas.analysis import AnalysisResult
from app.schemas.requirement import MatchStatus
from app.services.matching.base import Matcher
from app.services.matching.keyword_matcher import KeywordMatcher
from app.services.matching.llm_matcher import LLMMatcher
from app.services.scoring import calculate_score
from app.services.text_normalization import verify_evidence


def _get_matcher() -> Matcher:
    settings = get_settings()
    if settings.matcher == "keyword":
        return KeywordMatcher()
    return LLMMatcher()


def run_analysis(
    *,
    user_id: UUID,
    cv_text: str,
    cv_source: Literal["pdf", "docx", "text"],
    job_text: str,
    output_language: Literal["tr", "en"],
    repository: AnalysisRepository,
) -> AnalysisResult:
    settings = get_settings()
    matcher = _get_matcher()

    started_at = time.monotonic()
    result = matcher.match(job_text=job_text, cv_text=cv_text, output_language=output_language)

    verified_matches = []
    for match in result.matches:
        if match.status == MatchStatus.MET and not verify_evidence(match.evidence, cv_text):
            match = match.model_copy(update={"status": MatchStatus.PARTIAL, "evidence": None})
        verified_matches.append(match)

    overall_score = calculate_score(verified_matches)
    duration_ms = round((time.monotonic() - started_at) * 1000)

    return repository.save(
        user_id=user_id,
        analysis=NewAnalysis(
            job_title=result.job_title,
            company_name=result.company_name,
            job_text=job_text,
            cv_source=cv_source,
            overall_score=overall_score,
            output_language=output_language,
            matcher=settings.matcher,
            model=settings.gemini_model if settings.matcher == "llm" else None,
            duration_ms=duration_ms,
            matches=verified_matches,
        ),
    )
