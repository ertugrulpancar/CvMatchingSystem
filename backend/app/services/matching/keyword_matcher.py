import re
from typing import Literal

from app.schemas.requirement import Importance, MatchStatus, RequirementMatch
from app.services.matching.base import MatchResult
from app.services.matching.skills_dictionary import SKILLS

# 'i'/'I' Türkçe'de İngilizce'den farklı davranır (İ/ı), bu yüzden düz
# .lower()/.upper() yerine bu iki harfi ayrıca bir karakter sınıfında ele alıyoruz.
_TURKISH_I_VARIANTS = "iİıI"

_EXPLANATIONS: dict[tuple[str, MatchStatus], str] = {
    ("tr", MatchStatus.MET): "CV'de '{quote}' bulundu.",
    ("tr", MatchStatus.MISSING): "'{canonical}' CV'de bulunamadı.",
    ("en", MatchStatus.MET): "Found '{quote}' in the CV.",
    ("en", MatchStatus.MISSING): "Could not find '{canonical}' in the CV.",
}


def _char_pattern(char: str) -> str:
    if char in _TURKISH_I_VARIANTS:
        return f"[{_TURKISH_I_VARIANTS}]"
    if char.isalpha():
        return f"[{char.lower()}{char.upper()}]"
    return re.escape(char)


def _build_pattern(term: str) -> re.Pattern[str]:
    return re.compile("".join(_char_pattern(char) for char in term))


def _find_first(text: str, terms: list[str]) -> re.Match[str] | None:
    for term in terms:
        match = _build_pattern(term).search(text)
        if match:
            return match
    return None


class KeywordMatcher:
    def match(
        self, job_text: str, cv_text: str, output_language: Literal["tr", "en"]
    ) -> MatchResult:
        matches: list[RequirementMatch] = []

        for skill in SKILLS:
            terms = [skill["canonical"], *skill["aliases"]]
            if _find_first(job_text, terms) is None:
                continue

            cv_match = _find_first(cv_text, terms)
            status = MatchStatus.MET if cv_match else MatchStatus.MISSING
            evidence = cv_match.group(0) if cv_match else None
            explanation = _EXPLANATIONS[(output_language, status)].format(
                quote=evidence, canonical=skill["canonical"]
            )

            matches.append(
                RequirementMatch(
                    requirement_text=skill["canonical"],
                    category=skill["category"],
                    importance=Importance.MUST_HAVE,
                    status=status,
                    evidence=evidence,
                    explanation=explanation,
                )
            )

        return MatchResult(job_title=None, company_name=None, matches=matches)
