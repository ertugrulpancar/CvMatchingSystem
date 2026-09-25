import unicodedata

from rapidfuzz import fuzz

MIN_PARTIAL_RATIO = 90


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = text.replace("̇", "")
    text = text.replace("ı", "i")
    return " ".join(text.split())


def verify_evidence(evidence: str | None, cv_text: str) -> bool:
    if not evidence:
        return False
    ratio = fuzz.partial_ratio(normalize_for_match(evidence), normalize_for_match(cv_text))
    return ratio >= MIN_PARTIAL_RATIO
