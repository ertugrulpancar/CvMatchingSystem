from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_analysis_with_cv_text_returns_201(analysis_repository):
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
    assert body["id"]
    assert body["created_at"]


def test_create_analysis_requires_exactly_one_cv_source(analysis_repository):
    response = client.post(
        "/api/v1/analyses",
        data={"job_text": "Python aranıyor.", "output_language": "tr"},
    )

    assert response.status_code == 400


def test_create_analysis_rejects_both_cv_sources(analysis_repository):
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


def test_create_analysis_with_no_recognizable_requirements_returns_422(analysis_repository):
    response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Ofisimiz şehir merkezinde, keyifli bir çalışma ortamımız var.",
            "cv_text": "Herhangi bir CV metni.",
            "output_language": "tr",
        },
    )

    assert response.status_code == 422


def test_created_analysis_appears_in_list_and_detail(analysis_repository):
    create_response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Python deneyimi olan bir geliştirici arıyoruz.",
            "cv_text": "3 yıldır Python ile çalışıyorum.",
            "output_language": "tr",
        },
    )
    analysis_id = create_response.json()["id"]

    list_response = client.get("/api/v1/analyses")
    assert list_response.status_code == 200
    summaries = list_response.json()
    assert len(summaries) == 1
    assert summaries[0]["id"] == analysis_id
    assert "matches" not in summaries[0]

    detail_response = client.get(f"/api/v1/analyses/{analysis_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == analysis_id
    assert len(detail_response.json()["matches"]) == 1


def test_get_unknown_analysis_returns_404(analysis_repository):
    response = client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000099")

    assert response.status_code == 404


def test_delete_analysis_removes_it(analysis_repository):
    create_response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Python deneyimi olan bir geliştirici arıyoruz.",
            "cv_text": "3 yıldır Python ile çalışıyorum.",
            "output_language": "tr",
        },
    )
    analysis_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/analyses/{analysis_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_response.status_code == 404


def test_delete_unknown_analysis_returns_404(analysis_repository):
    response = client.delete("/api/v1/analyses/00000000-0000-0000-0000-000000000099")

    assert response.status_code == 404
