from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from app.core.config import get_settings
from app.schemas.analysis import AnalysisResult
from app.schemas.requirement import MatchStatus
from app.services.matching.base import Matcher
from app.services.matching.keyword_matcher import KeywordMatcher
from app.services.scoring import calculate_category_scores, calculate_score
from app.services.text_normalization import verify_evidence


def _get_matcher() -> Matcher:
    settings = get_settings()
    if settings.matcher == "keyword":
        return KeywordMatcher()
    raise NotImplementedError("LLM eşleştirici henüz eklenmedi (Faz 4)")


def run_analysis(
    cv_text: str, job_text: str, output_language: Literal["tr", "en"]
) -> AnalysisResult:
    settings = get_settings()
    matcher = _get_matcher()

    matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language=output_language)

    verified_matches = []
    for match in matches:
        if match.status == MatchStatus.MET and not verify_evidence(match.evidence, cv_text):
            match = match.model_copy(update={"status": MatchStatus.PARTIAL, "evidence": None})
        verified_matches.append(match)

    return AnalysisResult(
        id=uuid4(),
        created_at=datetime.now(UTC),
        job_title=None,
        company_name=None,
        overall_score=calculate_score(verified_matches),
        category_scores=calculate_category_scores(verified_matches),
        matches=verified_matches,
        output_language=output_language,
        matcher=settings.matcher,
    )
