from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import override_current_user

client = TestClient(app)


def test_user_cannot_see_another_users_analysis(analysis_repository):
    user_a = uuid4()
    user_b = uuid4()

    override_current_user(user_a)
    create_response = client.post(
        "/api/v1/analyses",
        data={
            "job_text": "Python deneyimi olan bir geliştirici arıyoruz.",
            "cv_text": "3 yıldır Python ile çalışıyorum.",
            "output_language": "tr",
        },
    )
    assert create_response.status_code == 201
    analysis_id = create_response.json()["id"]

    override_current_user(user_b)

    assert client.get(f"/api/v1/analyses/{analysis_id}").status_code == 404
    assert client.get("/api/v1/analyses").json() == []
    assert client.delete(f"/api/v1/analyses/{analysis_id}").status_code == 404

    override_current_user(user_a)
    assert client.get(f"/api/v1/analyses/{analysis_id}").status_code == 200
    assert len(client.get("/api/v1/analyses").json()) == 1


def test_missing_token_returns_401(analysis_repository):
    from app.core.auth import get_current_user

    app.dependency_overrides.pop(get_current_user, None)
    try:
        response = client.get("/api/v1/analyses")
        assert response.status_code == 401
    finally:
        override_current_user(uuid4())


def test_daily_quota_returns_429_when_exceeded(analysis_repository, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "daily_analysis_limit", 1)
    override_current_user(uuid4())

    payload = {
        "job_text": "Python deneyimi olan bir geliştirici arıyoruz.",
        "cv_text": "3 yıldır Python ile çalışıyorum.",
        "output_language": "tr",
    }
    first = client.post("/api/v1/analyses", data=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/analyses", data=payload)
    assert second.status_code == 429
