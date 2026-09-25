from app.schemas.requirement import Importance, MatchStatus, RequirementCategory
from app.services.llm.schemas import (
    ExtractedRequirement,
    JobExtraction,
    LLMMatchItem,
    LLMMatchResponse,
)
from app.services.matching.llm_matcher import LLMMatcher


def test_llm_matcher_combines_extraction_and_matching(monkeypatch):
    extraction = JobExtraction(
        job_title="Junior Backend Developer",
        company_name="Acme",
        requirements=[
            ExtractedRequirement(
                requirement_text="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=Importance.MUST_HAVE,
            ),
            ExtractedRequirement(
                requirement_text="Docker",
                category=RequirementCategory.TOOL,
                importance=Importance.NICE_TO_HAVE,
            ),
        ],
    )
    match_response = LLMMatchResponse(
        matches=[
            LLMMatchItem(
                requirement_index=0,
                status=MatchStatus.MET,
                evidence="Python ile 2 yıl çalıştım",
                explanation="Karşılanıyor.",
            ),
            LLMMatchItem(
                requirement_index=1,
                status=MatchStatus.MISSING,
                evidence=None,
                explanation="Bulunamadı.",
            ),
        ]
    )

    responses = iter([extraction, match_response])
    monkeypatch.setattr(
        "app.services.matching.llm_matcher.generate_structured",
        lambda prompt, response_schema: next(responses),
    )

    result = LLMMatcher().match(job_text="...", cv_text="...", output_language="tr")

    assert result.job_title == "Junior Backend Developer"
    assert result.company_name == "Acme"
    assert len(result.matches) == 2
    assert result.matches[0].requirement_text == "Python"
    assert result.matches[0].status == MatchStatus.MET
    assert result.matches[0].evidence == "Python ile 2 yıl çalıştım"
    assert result.matches[1].requirement_text == "Docker"
    assert result.matches[1].status == MatchStatus.MISSING


def test_llm_matcher_handles_missing_index_gracefully(monkeypatch):
    # LLM, gereksinimlerden biri için hiç sonuç döndürmezse (structured output
    # yine de tam güvenilir değil), o gereksinim "missing" sayılmalı, hata
    # fırlatılmamalı.
    extraction = JobExtraction(
        job_title=None,
        company_name=None,
        requirements=[
            ExtractedRequirement(
                requirement_text="SQL",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=Importance.MUST_HAVE,
            ),
        ],
    )
    match_response = LLMMatchResponse(matches=[])

    responses = iter([extraction, match_response])
    monkeypatch.setattr(
        "app.services.matching.llm_matcher.generate_structured",
        lambda prompt, response_schema: next(responses),
    )

    result = LLMMatcher().match(job_text="...", cv_text="...", output_language="en")

    assert len(result.matches) == 1
    assert result.matches[0].status == MatchStatus.MISSING
    assert "No result" in result.matches[0].explanation


def test_llm_matcher_returns_empty_when_no_requirements_extracted(monkeypatch):
    extraction = JobExtraction(job_title=None, company_name=None, requirements=[])

    monkeypatch.setattr(
        "app.services.matching.llm_matcher.generate_structured",
        lambda prompt, response_schema: extraction,
    )

    result = LLMMatcher().match(job_text="...", cv_text="...", output_language="tr")

    assert result.matches == []
