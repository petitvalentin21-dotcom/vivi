from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings
from app.llm.lmstudio import LMStudioCompletionResult, LMStudioError


def _settings(tmp_path: Path, api_key: str = "") -> Settings:
    return Settings(
        api_key=api_key,
        lmstudio_model="local-model",
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        knowledge_vault_path=str(tmp_path / "knowledge_vault"),
    )


def _ok_completion():
    return LMStudioCompletionResult(content="Bonjour", model="local-model", provider="lmstudio")


def test_chat_valid_returns_200_and_contract(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)

    client = TestClient(create_app(_settings(tmp_path)))
    response = client.post("/chat", json={"message": "Salut"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Bonjour"
    assert payload["session_id"]
    assert payload["provider"]["name"] == "lmstudio"
    assert payload["sources"] == []
    assert payload["runtime"]["rag_used"] is False
    assert payload["runtime"]["sources_count"] == 0
    assert payload["runtime"]["external_call_used"] is False


def test_chat_empty_message_returns_safe_error(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_chat_mode_not_supported_returns_safe_error(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    response = client.post("/chat", json={"message": "Salut", "mode": "diagnostic"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_chat_lmstudio_unavailable_returns_safe_error(monkeypatch, tmp_path: Path) -> None:
    err = LMStudioError(
        code="lmstudio_unavailable",
        message="LM Studio is unavailable.",
        recovery_hint="Start LM Studio.",
        status_code=503,
    )

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return None, err

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "Salut"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "lmstudio_unavailable"


def test_chat_model_not_configured_returns_safe_error(monkeypatch, tmp_path: Path) -> None:
    err = LMStudioError(
        code="lmstudio_model_missing",
        message="LM Studio model is not configured.",
        recovery_hint="Set model.",
        status_code=400,
    )

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return None, err

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "Salut"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "lmstudio_model_missing"


def test_chat_does_not_leak_api_key_in_error(monkeypatch, tmp_path: Path) -> None:
    secret = "sk-secret"
    err = LMStudioError(
        code="lmstudio_unavailable",
        message="LM Studio is unavailable.",
        recovery_hint="Retry.",
        status_code=503,
    )

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return None, err

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path, api_key=secret)))

    response = client.post("/chat", json={"message": "Salut"}, headers={"X-VIVI-API-Key": secret})
    assert response.status_code == 503
    assert secret not in response.text


def test_chat_requires_auth_when_api_key_is_set(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path, api_key="top-secret")))

    response = client.post("/chat", json={"message": "Salut"})
    assert response.status_code == 401


def test_chat_without_api_key_is_accessible(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path, api_key="")))

    response = client.post("/chat", json={"message": "Salut"})
    assert response.status_code == 200


def test_chat_session_is_created_when_missing(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)

    store_path = tmp_path / "runtime" / "sessions.json"
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "Salut"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    payload = json.loads(store_path.read_text(encoding="utf-8"))
    assert session_id in payload["sessions"]


def test_chat_session_known_is_reused(monkeypatch, tmp_path: Path) -> None:
    captured = {"calls": 0}

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        captured["calls"] += 1
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    first = client.post("/chat", json={"message": "Salut"}).json()
    session_id = first["session_id"]

    second = client.post("/chat", json={"message": "Encore", "session_id": session_id})
    assert second.status_code == 200
    assert second.json()["session_id"] == session_id
    assert captured["calls"] == 2


def test_chat_unknown_session_returns_session_not_found(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return _ok_completion(), None

    monkeypatch.setattr("app.api.server.LMStudioClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "Salut", "session_id": "unknown"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "session_not_found"
