"""Tests intégration — endpoints REST /prompts."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


@pytest.fixture()
def client():
    app = create_app(Settings(db_path=""))
    return TestClient(app)


def test_list_prompts_ok(client):
    resp = client.get("/prompts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["current_version"] == "v1"
    assert "system" in body["prompts"]
    assert "tool_calling" in body["prompts"]


def test_get_system_ok(client):
    resp = client.get("/prompts/system")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["content"]) > 0
    assert body["char_count"] > 0
    assert body["char_count"] == len(body["content"])


def test_get_system_with_explicit_version(client):
    resp = client.get("/prompts/system?version=v1")
    assert resp.status_code == 200


def test_get_inexistant_returns_404(client):
    resp = client.get("/prompts/inexistant")
    assert resp.status_code == 404


def test_get_system_unknown_version_returns_404(client):
    resp = client.get("/prompts/system?version=v99")
    assert resp.status_code == 404


def test_get_system_invalid_version_returns_422(client):
    resp = client.get("/prompts/system?version=invalid")
    assert resp.status_code == 422


def test_get_tool_calling_ok(client):
    resp = client.get("/prompts/tool_calling")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["content"]) > 0
