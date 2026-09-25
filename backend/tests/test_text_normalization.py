from app.services.text_normalization import normalize_for_match, verify_evidence


def test_normalize_handles_turkish_dotted_capital_i():
    # Python'da "İSTANBUL".lower() -> "i̇stanbul" (i + görünmez U+0307) üretir.
    # normalize_for_match bunu "istanbul" haline getirmeli.
    assert normalize_for_match("İSTANBUL") == normalize_for_match("istanbul")


def test_normalize_handles_turkish_dotless_i():
    # "kapıyı" (dotless ı) ile büyük harfli "KAPIYI" (ASCII I) aynı kelimenin
    # farklı yazımları; ikisi de "kapiyi" biçimine normalize edilmeli.
    assert normalize_for_match("kapıyı") == normalize_for_match("KAPIYI") == "kapiyi"


def test_normalize_collapses_whitespace_and_line_breaks():
    assert normalize_for_match("Makine   Öğrenmesi") == normalize_for_match("makine öğrenmesi")


def test_normalize_english_capital_i_unaffected():
    assert normalize_for_match("Istanbul") == "istanbul"


def test_verify_evidence_true_for_verbatim_quote():
    cv_text = "Deneyim: Python ve FastAPI ile bir raporlama servisi geliştirdim."
    assert verify_evidence("Python ve FastAPI ile bir raporlama servisi", cv_text) is True


def test_verify_evidence_true_across_line_break():
    # PDF'lerde satır kırılmaları olabilir; fuzzy eşik bunu tolere etmeli.
    cv_text = "Python ve FastAPI\nile bir raporlama servisi geliştirdim."
    assert verify_evidence("Python ve FastAPI ile bir raporlama servisi", cv_text) is True


def test_verify_evidence_true_for_turkish_case_mismatch():
    cv_text = "İSTANBUL'da yaşıyorum ve makine öğrenmesi ile ilgileniyorum."
    assert verify_evidence("istanbul'da yaşıyorum", cv_text) is True


def test_verify_evidence_false_for_fabricated_quote():
    cv_text = "Python ve SQL biliyorum."
    assert verify_evidence("10 yıl Java deneyimim var", cv_text) is False


def test_verify_evidence_false_for_none():
    assert verify_evidence(None, "herhangi bir cv metni") is False
