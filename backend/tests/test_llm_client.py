import pytest
from pydantic import BaseModel

from app.services.llm.client import GeminiError, generate_structured


class _Dummy(BaseModel):
    value: str


class _FakeModels:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def generate_content(self, *, model, contents, config):
        if self._error:
            raise self._error
        return self._response


class _FakeClient:
    def __init__(self, models: _FakeModels):
        self.models = models


class _FakeResponse:
    def __init__(self, parsed):
        self.parsed = parsed


def test_generate_structured_returns_parsed_value(monkeypatch):
    fake_client = _FakeClient(_FakeModels(response=_FakeResponse(parsed=_Dummy(value="ok"))))
    monkeypatch.setattr("app.services.llm.client._get_client", lambda: fake_client)

    result = generate_structured("prompt", _Dummy)

    assert result == _Dummy(value="ok")


def test_generate_structured_wraps_sdk_errors(monkeypatch):
    fake_client = _FakeClient(_FakeModels(error=RuntimeError("boom")))
    monkeypatch.setattr("app.services.llm.client._get_client", lambda: fake_client)

    with pytest.raises(GeminiError):
        generate_structured("prompt", _Dummy)


def test_generate_structured_rejects_unexpected_parsed_type(monkeypatch):
    class _Other(BaseModel):
        other: str

    fake_client = _FakeClient(_FakeModels(response=_FakeResponse(parsed=_Other(other="x"))))
    monkeypatch.setattr("app.services.llm.client._get_client", lambda: fake_client)

    with pytest.raises(GeminiError):
        generate_structured("prompt", _Dummy)
