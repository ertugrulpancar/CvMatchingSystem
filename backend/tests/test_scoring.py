import pytest

from app.schemas.requirement import Importance, MatchStatus, RequirementCategory, RequirementMatch
from app.services.scoring import EmptyRequirementsError, calculate_category_scores, calculate_score


def _match(
    category: RequirementCategory,
    importance: Importance,
    status: MatchStatus,
) -> RequirementMatch:
    return RequirementMatch(
        requirement_text="test gereksinimi",
        category=category,
        importance=importance,
        status=status,
        evidence=None,
        explanation="test",
    )


def test_all_must_have_met_scores_100():
    matches = [
        _match(RequirementCategory.TECHNICAL_SKILL, Importance.MUST_HAVE, MatchStatus.MET),
        _match(RequirementCategory.TOOL, Importance.MUST_HAVE, MatchStatus.MET),
    ]
    assert calculate_score(matches) == 100


def test_all_missing_scores_0():
    matches = [
        _match(RequirementCategory.TECHNICAL_SKILL, Importance.MUST_HAVE, MatchStatus.MISSING),
    ]
    assert calculate_score(matches) == 0


def test_weighted_mix_matches_expected_formula():
    # must_have(w=2) met(1.0) + nice_to_have(w=1) missing(0) + must_have(w=2) partial(0.5)
    # = (2*1.0 + 1*0 + 2*0.5) / (2+1+2) * 100 = 3/5*100 = 60
    matches = [
        _match(RequirementCategory.TECHNICAL_SKILL, Importance.MUST_HAVE, MatchStatus.MET),
        _match(RequirementCategory.TOOL, Importance.NICE_TO_HAVE, MatchStatus.MISSING),
        _match(RequirementCategory.TECHNICAL_SKILL, Importance.MUST_HAVE, MatchStatus.PARTIAL),
    ]
    assert calculate_score(matches) == 60


def test_empty_matches_raises():
    with pytest.raises(EmptyRequirementsError):
        calculate_score([])


def test_category_scores_only_include_present_categories():
    matches = [
        _match(RequirementCategory.TECHNICAL_SKILL, Importance.MUST_HAVE, MatchStatus.MET),
        _match(RequirementCategory.TOOL, Importance.MUST_HAVE, MatchStatus.MISSING),
    ]
    scores = calculate_category_scores(matches)

    scores_by_category = {score.category: score.score for score in scores}
    assert scores_by_category == {
        RequirementCategory.TECHNICAL_SKILL: 100,
        RequirementCategory.TOOL: 0,
    }
    assert RequirementCategory.LANGUAGE not in scores_by_category
