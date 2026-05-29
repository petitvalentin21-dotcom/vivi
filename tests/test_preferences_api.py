"""Tests intégration — endpoints REST /preferences."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


# ---------------------------------------------------------------------------
# Fixture partagée
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "preferences_api_test.db")))
    return TestClient(app)


def _pref_payload(**kwargs) -> dict:
    defaults = {"cle": "regime", "valeur": "végétarien"}
    defaults.update(kwargs)
    return defaults


# ===========================================================================
# POST /preferences
# ===========================================================================


def test_create_returns_201(client):
    resp = client.post("/preferences", json=_pref_payload())
    assert resp.status_code == 201


def test_create_response_fields(client):
    resp = client.post("/preferences", json=_pref_payload(cle="regime", valeur="végétarien", type_valeur="string"))
    body = resp.json()
    assert "id" in body
    assert body["cle"] == "regime"
    assert body["valeur"] == "végétarien"
    assert body["type_valeur"] == "string"


def test_create_empty_cle_rejected(client):
    resp = client.post("/preferences", json=_pref_payload(cle=""))
    assert resp.status_code == 422


def test_create_duplicate_409(client):
    client.post("/preferences", json=_pref_payload())
    resp = client.post("/preferences", json=_pref_payload())
    assert resp.status_code == 409


# ===========================================================================
# GET /preferences
# ===========================================================================


def test_list_empty(client):
    resp = client.get("/preferences")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["count"] == 0


def test_list_returns_created(client):
    client.post("/preferences", json=_pref_payload(cle="a", valeur="1"))
    client.post("/preferences", json=_pref_payload(cle="b", valeur="2"))
    body = client.get("/preferences").json()
    assert body["count"] == 2


def test_list_filter_categorie(client):
    client.post("/preferences", json=_pref_payload(cle="regime", categorie="alimentaire"))
    client.post("/preferences", json=_pref_payload(cle="temps_max", valeur="45", categorie="planning"))
    body = client.get("/preferences?categorie=alimentaire").json()
    assert body["count"] == 1
    assert body["items"][0]["cle"] == "regime"


# ===========================================================================
# GET /preferences/resume
# ===========================================================================


def test_resume_empty(client):
    resp = client.get("/preferences/resume")
    assert resp.status_code == 200
    body = resp.json()
    assert body["preferences"] == {}
    assert body["count"] == 0


def test_resume_returns_typed_values(client):
    client.post("/preferences", json=_pref_payload(cle="regime", valeur="végétarien", type_valeur="string"))
    client.post("/preferences", json=_pref_payload(cle="taille_foyer", valeur="2", type_valeur="int"))
    client.post("/preferences", json=_pref_payload(cle="allergies", valeur='["gluten"]', type_valeur="list"))
    body = client.get("/preferences/resume").json()
    assert body["preferences"]["regime"] == "végétarien"
    assert body["preferences"]["taille_foyer"] == 2
    assert body["preferences"]["allergies"] == ["gluten"]
    assert body["count"] == 3


# ===========================================================================
# GET /preferences/{cle}
# ===========================================================================


def test_get_by_cle_existing(client):
    client.post("/preferences", json=_pref_payload(cle="regime"))
    resp = client.get("/preferences/regime")
    assert resp.status_code == 200
    assert resp.json()["cle"] == "regime"


def test_get_by_cle_unknown_404(client):
    resp = client.get("/preferences/inexistant")
    assert resp.status_code == 404


# ===========================================================================
# PATCH /preferences/{preference_id}
# ===========================================================================


def test_patch_updates_fields(client):
    pref = client.post("/preferences", json=_pref_payload(cle="regime", valeur="omnivore")).json()
    resp = client.patch(f"/preferences/{pref['id']}", json={"valeur": "végétarien"})
    assert resp.status_code == 200
    assert resp.json()["valeur"] == "végétarien"


def test_patch_partial_keeps_other_fields(client):
    pref = client.post("/preferences", json=_pref_payload(cle="regime", valeur="omnivore", categorie="alimentaire")).json()
    resp = client.patch(f"/preferences/{pref['id']}", json={"valeur": "végétarien"})
    assert resp.json()["categorie"] == "alimentaire"


def test_patch_unknown_404(client):
    resp = client.patch(f"/preferences/{uuid.uuid4()}", json={"valeur": "x"})
    assert resp.status_code == 404


# ===========================================================================
# PUT /preferences/{cle}
# ===========================================================================


def test_put_creates_when_absent(client):
    resp = client.put("/preferences/nouveau", json={"valeur": "test"})
    assert resp.status_code == 200
    assert resp.json()["cle"] == "nouveau"


def test_put_upserts_same_id(client):
    first = client.put("/preferences/regime", json={"valeur": "omnivore"}).json()
    second = client.put("/preferences/regime", json={"valeur": "végétarien"}).json()
    assert first["id"] == second["id"]
    assert second["valeur"] == "végétarien"


# ===========================================================================
# DELETE /preferences/{preference_id}
# ===========================================================================


def test_delete_204(client):
    pref = client.post("/preferences", json=_pref_payload()).json()
    resp = client.delete(f"/preferences/{pref['id']}")
    assert resp.status_code == 204


def test_delete_then_get_by_cle_404(client):
    pref = client.post("/preferences", json=_pref_payload(cle="regime")).json()
    client.delete(f"/preferences/{pref['id']}")
    assert client.get("/preferences/regime").status_code == 404


def test_delete_unknown_404(client):
    resp = client.delete(f"/preferences/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# 503 when no DB configured
# ===========================================================================


def test_preferences_503_when_no_db():
    app = create_app(Settings())
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/preferences")
    assert resp.status_code == 503
