from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def _client(tmp_path):
    vault = tmp_path / "vault"
    (vault / "92_inbox").mkdir(parents=True)
    s = Settings(knowledge_vault_path=str(vault))  # api_key="" → auth_enabled=False
    return TestClient(create_app(s)), vault


def test_conversation_export_creates_inbox_note(tmp_path):
    client, vault = _client(tmp_path)
    payload = {
        "session_id": "abc12345",
        "messages": [
            {"role": "user", "content": "Bonjour VIVI"},
            {"role": "assistant", "content": "Bonjour !"},
        ],
    }
    res = client.post("/conversation/export", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["exported"] is True
    assert data["filename"].endswith(".md")
    assert "92_inbox" in data["relative_path"]

    note_path = vault / data["relative_path"]
    note = note_path.read_text(encoding="utf-8")
    assert "Conversation VIVI" in note
    assert "abc12345" in note
    assert "Bonjour VIVI" in note
    assert "Bonjour !" in note
    assert "conversation_summary" in note


def test_conversation_export_requires_user_message(tmp_path):
    client, _ = _client(tmp_path)
    payload = {
        "messages": [
            {"role": "assistant", "content": "Réponse sans question"},
        ]
    }
    res = client.post("/conversation/export", json=payload)
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "invalid_request"


def test_conversation_export_empty_messages_rejected(tmp_path):
    client, _ = _client(tmp_path)
    res = client.post("/conversation/export", json={"messages": []})
    assert res.status_code == 400


def test_conversation_export_no_session_id(tmp_path):
    client, vault = _client(tmp_path)
    payload = {
        "messages": [
            {"role": "user", "content": "Test sans session"},
            {"role": "assistant", "content": "OK"},
        ]
    }
    res = client.post("/conversation/export", json=payload)
    assert res.status_code == 200
    data = res.json()
    note = (vault / data["relative_path"]).read_text(encoding="utf-8")
    assert "anonyme" in note


def test_conversation_export_formats_exchanges_correctly(tmp_path):
    client, vault = _client(tmp_path)
    payload = {
        "session_id": "sess9999",
        "messages": [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Réponse 1"},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Réponse 2"},
        ],
    }
    res = client.post("/conversation/export", json=payload)
    assert res.status_code == 200
    note = (vault / res.json()["relative_path"]).read_text(encoding="utf-8")
    assert "Échanges : 2" in note
    assert "**[vous]** Question 1" in note
    assert "**[VIVI]** Réponse 1" in note
    assert "**[vous]** Question 2" in note
    assert "**[VIVI]** Réponse 2" in note


def test_web_js_has_conversation_log(tmp_path):
    client, _ = _client(tmp_path)
    js = client.get("/web/app.js")
    assert "conversationLog" in js.text
    assert "exportConversation" in js.text
    assert "sendBeacon" in js.text
    assert "/conversation/export" in js.text
