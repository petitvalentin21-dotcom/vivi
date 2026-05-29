"""Tests intégration — endpoints REST /tools."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings

_EXPECTED_TOOL_NAMES = {
    "list_recettes",
    "get_recette_by_id",
    "list_stock",
    "list_courses",
    "get_preferences_resume",
}


@pytest.fixture()
def client(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "tools_api_test.db")))
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /tools
# ---------------------------------------------------------------------------


def test_list_tools_200(client):
    resp = client.get("/tools")
    assert resp.status_code == 200


def test_list_tools_count_five(client):
    body = client.get("/tools").json()
    assert body["count"] == 5
    assert len(body["tools"]) == 5


def test_list_tools_contains_expected_names(client):
    body = client.get("/tools").json()
    names = {t["name"] for t in body["tools"]}
    assert names == _EXPECTED_TOOL_NAMES


def test_list_tools_each_has_required_fields(client):
    body = client.get("/tools").json()
    for tool in body["tools"]:
        assert "name" in tool
        assert "description" in tool
        assert "parameters_schema" in tool
        assert "read_only" in tool
        assert tool["read_only"] is True


# ---------------------------------------------------------------------------
# POST /tools/list_recettes/invoke
# ---------------------------------------------------------------------------


def test_invoke_list_recettes_200(client):
    resp = client.post("/tools/list_recettes/invoke", json={"arguments": {}})
    assert resp.status_code == 200


def test_invoke_list_recettes_ok_and_result_is_list(client):
    body = client.post("/tools/list_recettes/invoke", json={"arguments": {}}).json()
    assert body["ok"] is True
    assert isinstance(body["result"], list)
    assert body["error"] is None


def test_invoke_get_recette_by_id_invalid_uuid_400(client):
    resp = client.post(
        "/tools/get_recette_by_id/invoke",
        json={"arguments": {"recette_id": "pas-un-uuid"}},
    )
    assert resp.status_code == 400


def test_invoke_get_recette_by_id_unknown_uuid_400(client):
    import uuid
    resp = client.post(
        "/tools/get_recette_by_id/invoke",
        json={"arguments": {"recette_id": str(uuid.uuid4())}},
    )
    assert resp.status_code == 400


def test_invoke_get_recette_by_id_missing_arg_422(client):
    resp = client.post("/tools/get_recette_by_id/invoke", json={"arguments": {}})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /tools/list_stock/invoke
# ---------------------------------------------------------------------------


def test_invoke_list_stock_200(client):
    resp = client.post("/tools/list_stock/invoke", json={"arguments": {}})
    assert resp.status_code == 200


def test_invoke_list_stock_result_has_batchs_and_ingredients(client):
    body = client.post("/tools/list_stock/invoke", json={"arguments": {}}).json()
    assert body["ok"] is True
    assert "batchs" in body["result"]
    assert "ingredients" in body["result"]


def test_invoke_list_stock_with_categorie_200(client):
    resp = client.post(
        "/tools/list_stock/invoke",
        json={"arguments": {"categorie": "légumes"}},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /tools/list_courses/invoke
# ---------------------------------------------------------------------------


def test_invoke_list_courses_200(client):
    resp = client.post("/tools/list_courses/invoke", json={"arguments": {}})
    assert resp.status_code == 200


def test_invoke_list_courses_result_is_list(client):
    body = client.post("/tools/list_courses/invoke", json={"arguments": {}}).json()
    assert body["ok"] is True
    assert isinstance(body["result"], list)


# ---------------------------------------------------------------------------
# POST /tools/get_preferences_resume/invoke
# ---------------------------------------------------------------------------


def test_invoke_get_preferences_resume_200(client):
    resp = client.post("/tools/get_preferences_resume/invoke", json={"arguments": {}})
    assert resp.status_code == 200


def test_invoke_get_preferences_resume_result_is_dict(client):
    body = client.post("/tools/get_preferences_resume/invoke", json={"arguments": {}}).json()
    assert body["ok"] is True
    assert isinstance(body["result"], dict)


# ---------------------------------------------------------------------------
# Outil inconnu
# ---------------------------------------------------------------------------


def test_invoke_unknown_tool_404(client):
    resp = client.post("/tools/outil_inconnu/invoke", json={"arguments": {}})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 503 when no DB configured
# ---------------------------------------------------------------------------


def test_invoke_503_when_no_db():
    app = create_app(Settings())
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.post("/tools/list_recettes/invoke", json={"arguments": {}})
    assert resp.status_code == 503
