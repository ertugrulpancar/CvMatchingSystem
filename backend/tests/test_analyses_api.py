from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_analysis_with_cv_text_returns_201():
    response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Python ve Docker deneyimi olan bir geliştirici arıyoruz.",
            "cv_text": "3 yıldır Python ile çalışıyorum, Docker kullanıyorum.",
            "output_language": "tr",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["matcher"] == "keyword"
    assert body["overall_score"] == 100
    assert len(body["matches"]) == 2


def test_create_analysis_requires_exactly_one_cv_source():
    response = client.post(
        "/api/v1/analyses",
        data={"job_text": "Python aranıyor.", "output_language": "tr"},
    )

    assert response.status_code == 400


def test_create_analysis_rejects_both_cv_sources():
    response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Python aranıyor.",
            "cv_text": "Python biliyorum.",
            "output_language": "tr",
        },
        files={"cv_file": ("cv.txt", b"Python biliyorum.", "text/plain")},
    )

    assert response.status_code == 400


def test_create_analysis_with_no_recognizable_requirements_returns_422():
    response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Ofisimiz şehir merkezinde, keyifli bir çalışma ortamımız var.",
            "cv_text": "Herhangi bir CV metni.",
            "output_language": "tr",
        },
    )

    assert response.status_code == 422
