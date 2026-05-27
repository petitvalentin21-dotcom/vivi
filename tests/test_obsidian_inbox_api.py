from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings
from app.knowledge.markdown_loader import load_markdown_notes


def _settings(tmp_path: Path, api_key: str = "") -> Settings:
    vault = tmp_path / "knowledge_vault"
    (vault / "92_inbox").mkdir(parents=True)
    return Settings(
        api_key=api_key,
        llm_model="local-model",
        knowledge_vault_path=str(vault),
        session_store_path=str(tmp_path / "runtime" / "sessions.json"),
    )


def test_obsidian_inbox_endpoint_creates_note_with_structured_response(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    client = TestClient(create_app(settings))

    response = client.post(
        "/obsidian/inbox",
        json={
            "title": "Synthèse accès LAN",
            "body": "Contenu proposé à relire.",
            "note_type": "conversation_summary",
            "status": "draft",
            "source_paths": ["docs/LAN_LOCAL_ACCESS.md"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["created"] is True
    assert payload["relative_path"].startswith("92_inbox/")
    assert payload["filename"].endswith("_inbox_synthese-acces-lan.md")
    assert payload["note_type"] == "conversation_summary"
    assert payload["status"] == "draft"
    assert payload["index"] is False
    assert payload["review_required"] is True
    assert "Contenu proposé à relire." not in response.text

    created = Path(settings.knowledge_vault_path) / payload["relative_path"]
    content = created.read_text(encoding="utf-8")
    assert created.parent == Path(settings.knowledge_vault_path) / "92_inbox"
    assert "type: conversation_summary" in content
    assert "status: draft" in content
    assert "source: vivi" in content
    assert "index: false" in content
    assert "review_required: true" in content
    assert "# Synthèse accès LAN" in content
    assert "Contenu proposé à relire." in content
    assert "- docs/LAN_LOCAL_ACCESS.md" in content


def test_obsidian_inbox_endpoint_accepts_allowed_type_and_rejects_unknown_type(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    ok = client.post(
        "/obsidian/inbox",
        json={"title": "Backlog", "body": "Proposition.", "note_type": "backlog_proposal"},
    )
    assert ok.status_code == 200
    assert ok.json()["note_type"] == "backlog_proposal"

    rejected = client.post(
        "/obsidian/inbox",
        json={"title": "Backlog", "body": "Proposition.", "note_type": "validated_decision"},
    )
    assert rejected.status_code == 400
    assert rejected.json()["error"]["code"] == "invalid_request"


def test_obsidian_inbox_endpoint_rejects_non_creatable_status(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post(
        "/obsidian/inbox",
        json={"title": "Décision", "body": "Proposition.", "status": "validated"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_obsidian_inbox_endpoint_rejects_missing_title_or_body(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    missing_title = client.post("/obsidian/inbox", json={"body": "Contenu."})
    missing_body = client.post("/obsidian/inbox", json={"title": "Titre"})
    empty_title = client.post("/obsidian/inbox", json={"title": "   ", "body": "Contenu."})
    empty_body = client.post("/obsidian/inbox", json={"title": "Titre", "body": "   "})

    assert missing_title.status_code == 422
    assert missing_body.status_code == 422
    assert empty_title.status_code == 400
    assert empty_body.status_code == 400


def test_obsidian_inbox_endpoint_rejects_sensitive_content(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))

    response = client.post(
        "/obsidian/inbox",
        json={"title": "Secret", "body": "api_key=do-not-store-this"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"
    assert list((Path(tmp_path) / "knowledge_vault" / "92_inbox").glob("*.md")) == []


def test_obsidian_inbox_endpoint_auth_when_api_key_is_configured(tmp_path: Path) -> None:
    client = TestClient(create_app(_settings(tmp_path, api_key="vivi-secret")))
    payload = {"title": "Auth", "body": "Contenu."}

    no_key = client.post("/obsidian/inbox", json=payload)
    wrong_key = client.post("/obsidian/inbox", json=payload, headers={"X-VIVI-API-Key": "wrong"})
    good_key = client.post("/obsidian/inbox", json=payload, headers={"X-VIVI-API-Key": "vivi-secret"})

    assert no_key.status_code == 401
    assert wrong_key.status_code == 401
    assert good_key.status_code == 200
    assert "vivi-secret" not in good_key.text


def test_obsidian_inbox_endpoint_never_writes_outside_inbox_or_modifies_sources(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    vault = Path(settings.knowledge_vault_path)
    source = vault / "00_product" / "source.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Source humaine\n", encoding="utf-8")
    client = TestClient(create_app(settings))

    response = client.post(
        "/obsidian/inbox",
        json={"title": "../00_product/source", "body": "Proposition."},
    )

    assert response.status_code == 200
    created = vault / response.json()["relative_path"]
    assert created.parent == vault / "92_inbox"
    assert source.read_text(encoding="utf-8") == "# Source humaine\n"
    assert not (vault / ".obsidian").exists()
    for folder in ["02_architecture", "03_decisions", "04_backlog", "05_runs", "90_generated", "91_runtime", "99_archive"]:
        assert not (vault / folder / response.json()["filename"]).exists()


def test_obsidian_inbox_endpoint_does_not_call_lmstudio_or_change_rag(monkeypatch, tmp_path: Path) -> None:
    def fail_post(*args, **kwargs):
        raise AssertionError("LM Studio must not be called by /obsidian/inbox")

    monkeypatch.setattr(httpx, "post", fail_post)
    settings = _settings(tmp_path)
    vault = Path(settings.knowledge_vault_path)
    source = vault / "00_product" / "visible.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Visible\nContexte indexable.", encoding="utf-8")
    client = TestClient(create_app(settings))

    response = client.post(
        "/obsidian/inbox",
        json={"title": "Résumé RAG", "body": "Ce brouillon ne doit pas être indexé.", "note_type": "rag_summary"},
    )

    assert response.status_code == 200
    exists, notes, error = load_markdown_notes(str(vault))
    assert exists is True
    assert error is None
    assert {note.path for note in notes} == {"00_product/visible.md"}
