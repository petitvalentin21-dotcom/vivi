"""Tests intégration — endpoints REST /recettes."""
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
    app = create_app(Settings(db_path=str(tmp_path / "api_test.db")))
    return TestClient(app)


def _create_payload(**kwargs) -> dict:
    defaults = {
        "titre": "Soupe de tomates",
        "ingredients": [{"nom": "tomates", "quantite": 500, "unite": "g"}],
        "etapes": ["Éplucher", "Mixer"],
        "portions": 4,
        "tags": ["végétarien", "rapide"],
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# POST /recettes
# ---------------------------------------------------------------------------


def test_create_returns_201(client):
    resp = client.post("/recettes", json=_create_payload())
    assert resp.status_code == 201


def test_create_response_fields(client):
    resp = client.post("/recettes", json=_create_payload())
    body = resp.json()
    assert "id" in body
    assert body["titre"] == "Soupe de tomates"
    assert body["portions"] == 4
    assert body["nb_fois_cuisinee"] == 0
    assert body["statut_valeur_sure"] is False
    assert body["ingredients"] == [{"nom": "tomates", "quantite": 500.0, "unite": "g"}]
    assert body["tags"] == ["végétarien", "rapide"]


def test_create_minimal_payload(client):
    resp = client.post("/recettes", json={"titre": "Pain"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["ingredients"] == []
    assert body["etapes"] == []
    assert body["tags"] == []


def test_create_empty_titre_rejected(client):
    resp = client.post("/recettes", json={"titre": ""})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /recettes
# ---------------------------------------------------------------------------


def test_list_empty(client):
    resp = client.get("/recettes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_returns_created(client):
    client.post("/recettes", json=_create_payload(titre="A"))
    client.post("/recettes", json=_create_payload(titre="B"))
    resp = client.get("/recettes")
    assert resp.status_code == 200
    titles = [r["titre"] for r in resp.json()]
    assert set(titles) == {"A", "B"}


def test_list_filter_by_tag(client):
    client.post("/recettes", json=_create_payload(titre="Vég", tags=["végétarien"]))
    client.post("/recettes", json=_create_payload(titre="Batch", tags=["batch"]))
    resp = client.get("/recettes?tag=végétarien")
    assert resp.status_code == 200
    titles = [r["titre"] for r in resp.json()]
    assert titles == ["Vég"]


def test_list_pagination(client):
    for i in range(5):
        client.post("/recettes", json=_create_payload(titre=f"R{i}"))
    page = client.get("/recettes?limit=2&offset=0").json()
    assert len(page) == 2


# ---------------------------------------------------------------------------
# GET /recettes/{id}
# ---------------------------------------------------------------------------


def test_get_existing(client):
    r = client.post("/recettes", json=_create_payload()).json()
    resp = client.get(f"/recettes/{r['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == r["id"]


def test_get_nonexistent_returns_404(client):
    resp = client.get(f"/recettes/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_get_after_delete_returns_404(client):
    r = client.post("/recettes", json=_create_payload()).json()
    client.delete(f"/recettes/{r['id']}")
    resp = client.get(f"/recettes/{r['id']}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /recettes/{id}
# ---------------------------------------------------------------------------


def test_patch_titre(client):
    r = client.post("/recettes", json=_create_payload(titre="Old")).json()
    resp = client.patch(f"/recettes/{r['id']}", json={"titre": "New"})
    assert resp.status_code == 200
    assert resp.json()["titre"] == "New"


def test_patch_partial_keeps_other_fields(client):
    r = client.post("/recettes", json=_create_payload(portions=6)).json()
    resp = client.patch(f"/recettes/{r['id']}", json={"titre": "Updated"})
    assert resp.json()["portions"] == 6


def test_patch_statut_valeur_sure(client):
    r = client.post("/recettes", json=_create_payload()).json()
    resp = client.patch(f"/recettes/{r['id']}", json={"statut_valeur_sure": True})
    assert resp.json()["statut_valeur_sure"] is True


def test_patch_nonexistent_returns_404(client):
    resp = client.patch(f"/recettes/{uuid.uuid4()}", json={"titre": "X"})
    assert resp.status_code == 404


def test_patch_empty_titre_rejected(client):
    r = client.post("/recettes", json=_create_payload()).json()
    resp = client.patch(f"/recettes/{r['id']}", json={"titre": ""})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /recettes/{id}
# ---------------------------------------------------------------------------


def test_delete_returns_204(client):
    r = client.post("/recettes", json=_create_payload()).json()
    resp = client.delete(f"/recettes/{r['id']}")
    assert resp.status_code == 204


def test_delete_hides_from_list(client):
    r = client.post("/recettes", json=_create_payload()).json()
    client.delete(f"/recettes/{r['id']}")
    assert client.get("/recettes").json() == []


def test_delete_nonexistent_returns_404(client):
    resp = client.delete(f"/recettes/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /recettes/count
# ---------------------------------------------------------------------------


def test_count_empty(client):
    resp = client.get("/recettes/count")
    assert resp.status_code == 200
    assert resp.json() == {"count": 0}


def test_count_increments(client):
    client.post("/recettes", json=_create_payload())
    client.post("/recettes", json=_create_payload())
    assert client.get("/recettes/count").json()["count"] == 2


def test_count_excludes_deleted(client):
    r = client.post("/recettes", json=_create_payload()).json()
    client.delete(f"/recettes/{r['id']}")
    assert client.get("/recettes/count").json()["count"] == 0


# ---------------------------------------------------------------------------
# 503 when no DB configured
# ---------------------------------------------------------------------------


def test_recettes_503_when_no_db():
    app = create_app(Settings())  # db_path = "" → no DB
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/recettes")
    assert resp.status_code == 503
