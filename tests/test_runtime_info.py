from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def test_runtime_info_returns_200_when_ollama_unavailable(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    vault.mkdir(parents=True)
    (vault / "a.md").write_text("# note", encoding="utf-8")

    settings = Settings(
        ollama_base_url="http://127.0.0.1:9",
        knowledge_vault_path=str(vault),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )
    app = create_app(settings)
    client = TestClient(app)

    response = client.get("/runtime/info")
    assert response.status_code == 200


def test_runtime_info_does_not_expose_api_key(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    vault.mkdir(parents=True)

    secret = "super-secret-value"
    settings = Settings(
        api_key=secret,
        knowledge_vault_path=str(vault),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )
    app = create_app(settings)
    client = TestClient(app)

    payload = client.get("/runtime/info").json()
    assert secret not in str(payload)


def test_runtime_info_counts_vault_notes(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    vault.mkdir(parents=True)
    (vault / "one.md").write_text("# one", encoding="utf-8")
    (vault / "two.md").write_text("# two", encoding="utf-8")

    settings = Settings(
        knowledge_vault_path=str(vault),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )
    app = create_app(settings)
    client = TestClient(app)

    payload = client.get("/runtime/info").json()
    assert payload["vault"]["exists"] is True
    assert payload["vault"]["notes_count"] == 2


def test_runtime_info_exposes_ollama_provider(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    vault.mkdir(parents=True)

    settings = Settings(
        ollama_base_url="http://127.0.0.1:9",
        llm_model="test-model",
        knowledge_vault_path=str(vault),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )
    app = create_app(settings)
    client = TestClient(app)

    payload = client.get("/runtime/info").json()
    assert payload["provider"]["name"] == "ollama"
    assert payload["provider"]["model"] == "test-model"
