from datetime import UTC, datetime
from uuid import uuid4

from app.repositories.base import NewAnalysis
from app.repositories.memory_repository import InMemoryAnalysisRepository
from app.schemas.requirement import Importance, MatchStatus, RequirementCategory, RequirementMatch

USER_A = uuid4()
USER_B = uuid4()


def _new_analysis(**overrides) -> NewAnalysis:
    defaults = dict(
        job_title="Junior Developer",
        company_name=None,
        job_text="...",
        cv_source="text",
        overall_score=100,
        output_language="tr",
        matcher="keyword",
        model=None,
        duration_ms=10,
        matches=[
            RequirementMatch(
                requirement_text="Python",
                category=RequirementCategory.TECHNICAL_SKILL,
                importance=Importance.MUST_HAVE,
                status=MatchStatus.MET,
                evidence="Python",
                explanation="Karşılanıyor.",
            )
        ],
    )
    defaults.update(overrides)
    return NewAnalysis(**defaults)


def test_save_returns_result_with_computed_category_scores():
    repo = InMemoryAnalysisRepository()

    result = repo.save(USER_A, _new_analysis())

    assert result.overall_score == 100
    assert len(result.category_scores) == 1
    assert result.category_scores[0].category == RequirementCategory.TECHNICAL_SKILL
    assert result.category_scores[0].score == 100


def test_users_cannot_see_each_others_analyses():
    repo = InMemoryAnalysisRepository()
    saved = repo.save(USER_A, _new_analysis())

    assert repo.get(USER_B, saved.id) is None
    assert repo.list_summaries(USER_B, before=None, limit=20) == []
    assert repo.delete(USER_B, saved.id) is False
    # USER_A hâlâ erişebiliyor olmalı (USER_B'nin silme denemesi etkisiz kaldı)
    assert repo.get(USER_A, saved.id) is not None


def test_list_summaries_orders_newest_first_and_respects_limit():
    repo = InMemoryAnalysisRepository()
    for _ in range(3):
        repo.save(USER_A, _new_analysis())

    summaries = repo.list_summaries(USER_A, before=None, limit=2)

    assert len(summaries) == 2
    assert summaries[0].created_at >= summaries[1].created_at


def test_list_summaries_before_cursor_excludes_newer_items():
    repo = InMemoryAnalysisRepository()
    first = repo.save(USER_A, _new_analysis())

    cutoff = datetime.now(UTC)
    later = repo.save(USER_A, _new_analysis())

    summaries = repo.list_summaries(USER_A, before=cutoff, limit=20)

    ids = {summary.id for summary in summaries}
    assert first.id in ids
    assert later.id not in ids


def test_delete_returns_false_for_unknown_id():
    repo = InMemoryAnalysisRepository()

    assert repo.delete(USER_A, uuid4()) is False


def test_save_sets_created_at_to_now():
    repo = InMemoryAnalysisRepository()
    before = datetime.now(UTC)

    result = repo.save(USER_A, _new_analysis())

    assert before <= result.created_at <= datetime.now(UTC)
