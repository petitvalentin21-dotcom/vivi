from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_knowledge_search_returns_200_and_contract(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    _write(vault / "00_product" / "a.md", "# Search Note\nlexical retrieval works")

    app = create_app(
        Settings(
            knowledge_vault_path=str(vault),
            session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        )
    )
    client = TestClient(app)

    response = client.get("/knowledge/search", params={"q": "lexical"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "lexical"
    assert isinstance(payload["results"], list)
    assert payload["count"] == len(payload["results"])
    assert payload["mode"] == "lexical"


def test_knowledge_search_empty_q_returns_safe_error(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    _write(vault / "00_product" / "a.md", "# A")
    app = create_app(
        Settings(
            knowledge_vault_path=str(vault),
            session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        )
    )
    client = TestClient(app)

    response = client.get("/knowledge/search", params={"q": "   "})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_knowledge_search_vault_not_found_returns_safe_error(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            knowledge_vault_path=str(tmp_path / "missing_vault"),
            session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        )
    )
    client = TestClient(app)

    response = client.get("/knowledge/search", params={"q": "hello"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "vault_not_found"


def test_knowledge_search_does_not_require_lmstudio_and_no_secret_leak(tmp_path: Path) -> None:
    vault = tmp_path / "knowledge_vault"
    _write(vault / "02_architecture" / "b.md", "# B\nsearch content")
    secret = "super-secret-value"

    app = create_app(
        Settings(
            api_key=secret,
            knowledge_vault_path=str(vault),
            session_store_path=str(tmp_path / "runtime" / "sessions.json"),
        )
    )
    client = TestClient(app)

    response = client.get("/knowledge/search", params={"q": "search"})
    assert response.status_code == 200
    assert secret not in response.text
