from app.core.config import IMPORTANCE_WEIGHTS, STATUS_POINTS
from app.schemas.analysis import CategoryScore
from app.schemas.requirement import RequirementCategory, RequirementMatch


class EmptyRequirementsError(Exception):
    pass


def calculate_score(matches: list[RequirementMatch]) -> int:
    if not matches:
        raise EmptyRequirementsError("Skor hesaplamak için en az bir gereksinim gerekir")

    total_weight = sum(IMPORTANCE_WEIGHTS[match.importance] for match in matches)
    total_points = sum(
        IMPORTANCE_WEIGHTS[match.importance] * STATUS_POINTS[match.status] for match in matches
    )
    return round(total_points / total_weight * 100)


def calculate_category_scores(matches: list[RequirementMatch]) -> list[CategoryScore]:
    scores = []
    for category in RequirementCategory:
        category_matches = [match for match in matches if match.category == category]
        if not category_matches:
            continue
        scores.append(CategoryScore(category=category, score=calculate_score(category_matches)))
    return scores
