from app.schemas.requirement import Importance, MatchStatus
from app.services.matching.keyword_matcher import KeywordMatcher

matcher = KeywordMatcher()


def test_skill_present_in_both_job_and_cv_is_met():
    job_text = "Python ve SQL bilgisi aranıyor."
    cv_text = "3 yıl Python ile web servisleri geliştirdim."

    matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="tr")

    by_requirement = {m.requirement_text: m for m in matches}
    assert by_requirement["Python"].status == MatchStatus.MET
    assert by_requirement["Python"].evidence == "Python"
    assert by_requirement["Python"].importance == Importance.MUST_HAVE
    assert by_requirement["SQL"].status == MatchStatus.MISSING
    assert by_requirement["SQL"].evidence is None


def test_skill_not_mentioned_in_job_is_not_a_requirement():
    job_text = "Python bilgisi aranıyor."
    cv_text = "Docker ve Kubernetes deneyimim var."

    matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="tr")

    assert {m.requirement_text for m in matches} == {"Python"}


def test_cross_language_alias_matching():
    # İlan İngilizce, CV Türkçe: "machine learning" ilanda geçiyor,
    # CV'de "makine öğrenmesi" karşılığı olarak geçiyor.
    job_text = "Experience with machine learning is required."
    cv_text = "Makine öğrenmesi projelerinde çalıştım."

    matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="en")

    ml_match = next(m for m in matches if m.requirement_text == "Machine Learning")
    assert ml_match.status == MatchStatus.MET
    assert ml_match.evidence == "Makine öğrenmesi"


def test_turkish_capital_i_alias_matches():
    job_text = "İngilizce bilgisi gerekir."
    cv_text = "İngilizce seviyem ileri düzeydedir."

    matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="tr")

    english_match = next(m for m in matches if m.requirement_text == "English")
    assert english_match.status == MatchStatus.MET


def test_explanation_language_follows_output_language():
    job_text = "Docker deneyimi aranıyor."
    cv_text = "Docker kullandım."

    tr_matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="tr")
    en_matches = matcher.match(job_text=job_text, cv_text=cv_text, output_language="en")

    assert "bulundu" in tr_matches[0].explanation
    assert "Found" in en_matches[0].explanation
