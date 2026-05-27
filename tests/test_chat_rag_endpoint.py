from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings
from app.llm.base import LLMCompletionResult, LLMError


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _settings(tmp_path: Path, api_key: str = "") -> Settings:
    return Settings(
        api_key=api_key,
        llm_model="local-model",
        rag_top_k=3,
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        knowledge_vault_path=str(tmp_path / "knowledge_vault"),
    )


def _seed_vault(vault: Path) -> None:
    _write(vault / "00_product" / "mvp.md", "# MVP\nLe mode document utilise une recherche lexicale.")
    _write(vault / "02_architecture" / "api.md", "# API\nLe endpoint chat retourne des sources visibles.")
    _write(vault / "03_decisions" / "rag.md", "---\ntags: rag\n---\n# RAG\nContexte Obsidian et excerpts.")


def test_chat_mode_chat_without_rag_keeps_sources_empty(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="ok", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "Bonjour"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["sources"] == []
    assert payload["runtime"]["rag_used"] is False
    assert payload["runtime"]["external_call_used"] is False


def test_chat_mode_document_uses_rag_and_returns_sources(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")
    captured = {}

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        captured["messages"] = messages
        return LLMCompletionResult(content="doc", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "sources visibles", "mode": "document"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["mode"] == "document"
    assert payload["runtime"]["rag_used"] is True
    assert payload["runtime"]["sources_count"] >= 1
    assert payload["runtime"]["external_call_used"] is False

    first = payload["sources"][0]
    assert "path" in first and "title" in first and "section" in first and "score" in first and "excerpt" in first
    assert "chunk_text" in first
    assert first["chunk_text"]

    rag_prompt = [m for m in captured["messages"] if m["role"] == "system" and "Contexte documentaire Obsidian" in m["content"]]
    assert rag_prompt
    for src in payload["sources"]:
        assert src["title"] in rag_prompt[0]["content"]
        assert src["path"] in rag_prompt[0]["content"]
        assert src["chunk_text"] in rag_prompt[0]["content"]


def test_chat_use_rag_true_with_chat_mode_activates_rag(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="rag", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "rag", "mode": "chat", "use_rag": True})
    payload = response.json()
    assert response.status_code == 200
    assert payload["mode"] == "chat"
    assert payload["runtime"]["rag_used"] is True


def test_chat_max_sources_limits_results(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="limited", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "rag", "mode": "document", "max_sources": 1})
    payload = response.json()
    assert response.status_code == 200
    assert len(payload["sources"]) <= 1


def test_chat_no_relevant_source_keeps_success_with_empty_sources(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="aucune source", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post("/chat", json={"message": "zzzzzzzzzz", "mode": "document"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["sources"] == []
    assert payload["runtime"]["rag_used"] is True
    assert payload["runtime"]["sources_count"] == 0


def test_chat_document_vault_absent_returns_safe_error(monkeypatch, tmp_path: Path) -> None:
    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="x", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    settings = Settings(
        llm_model="local-model",
        knowledge_vault_path=str(tmp_path / "missing_vault"),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )
    client = TestClient(create_app(settings))

    response = client.post("/chat", json={"message": "doc", "mode": "document"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "vault_not_found"


def test_chat_document_session_behaviors_and_ollama_error(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")

    def fake_ok(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="ok", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_ok)
    store_path = tmp_path / "runtime" / "sessions.json"
    client = TestClient(create_app(_settings(tmp_path)))

    first = client.post("/chat", json={"message": "doc", "mode": "document"})
    assert first.status_code == 200
    session_id = first.json()["session_id"]

    second = client.post("/chat", json={"message": "doc 2", "mode": "document", "session_id": session_id})
    assert second.status_code == 200
    assert second.json()["session_id"] == session_id

    unknown = client.post("/chat", json={"message": "doc", "mode": "document", "session_id": "unknown"})
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "session_not_found"

    payload = json.loads(store_path.read_text(encoding="utf-8"))
    assert session_id in payload["sessions"]

    err = LLMError(
        code="ollama_unavailable",
        message="Ollama is unavailable.",
        recovery_hint="Start Ollama.",
        status_code=503,
    )

    def fake_err(self, messages, model=None, temperature=None, max_tokens=None):
        return None, err

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_err)
    failed = client.post("/chat", json={"message": "doc", "mode": "document"})
    assert failed.status_code == 503
    assert failed.json()["error"]["code"] == "ollama_unavailable"


def test_chat_document_no_secret_leak(monkeypatch, tmp_path: Path) -> None:
    _seed_vault(tmp_path / "knowledge_vault")
    secret = "super-secret-value"

    def fake_chat_completion(self, messages, model=None, temperature=None, max_tokens=None):
        return LLMCompletionResult(content="ok", model="local-model", provider="ollama"), None

    monkeypatch.setattr("app.api.server.OllamaClient.chat_completion", fake_chat_completion)
    client = TestClient(create_app(_settings(tmp_path, api_key=secret)))

    response = client.post(
        "/chat",
        json={"message": "document", "mode": "document"},
        headers={"X-VIVI-API-Key": secret},
    )
    assert response.status_code == 200
    assert secret not in response.text
