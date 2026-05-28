"""Tests intégration — endpoints REST /stock."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


# ---------------------------------------------------------------------------
# Fixture partagée
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "stock_api_test.db")))
    return TestClient(app)


def _batch_payload(**kwargs) -> dict:
    defaults = {
        "nom": "Dahl lentilles corail",
        "portions_total": 6,
        "portions_restantes": 6,
        "date_cuisson": str(date(2026, 5, 28)),
        "stockage": "frigo",
    }
    defaults.update(kwargs)
    return defaults


def _ingredient_payload(**kwargs) -> dict:
    defaults = {"nom": "Oeufs"}
    defaults.update(kwargs)
    return defaults


# ===========================================================================
# POST /stock/batchs
# ===========================================================================


def test_create_batch_returns_201(client):
    resp = client.post("/stock/batchs", json=_batch_payload())
    assert resp.status_code == 201


def test_create_batch_response_fields(client):
    resp = client.post("/stock/batchs", json=_batch_payload())
    body = resp.json()
    assert "id" in body
    assert body["nom"] == "Dahl lentilles corail"
    assert body["portions_total"] == 6
    assert body["portions_restantes"] == 6
    assert body["stockage"] == "frigo"
    assert body["recette_id"] is None


def test_create_batch_empty_nom_rejected(client):
    resp = client.post("/stock/batchs", json=_batch_payload(nom=""))
    assert resp.status_code == 422


def test_create_batch_invalid_stockage_rejected(client):
    resp = client.post("/stock/batchs", json=_batch_payload(stockage="saladier"))
    assert resp.status_code == 422


# ===========================================================================
# GET /stock/batchs
# ===========================================================================


def test_list_batchs_empty(client):
    resp = client.get("/stock/batchs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_batchs_returns_created(client):
    client.post("/stock/batchs", json=_batch_payload(nom="A"))
    client.post("/stock/batchs", json=_batch_payload(nom="B"))
    resp = client.get("/stock/batchs")
    noms = [b["nom"] for b in resp.json()]
    assert set(noms) == {"A", "B"}


def test_list_batchs_excludes_zero_portions_by_default(client):
    client.post("/stock/batchs", json=_batch_payload(nom="Vide", portions_restantes=0))
    client.post("/stock/batchs", json=_batch_payload(nom="Plein", portions_restantes=3))
    resp = client.get("/stock/batchs")
    noms = [b["nom"] for b in resp.json()]
    assert "Plein" in noms
    assert "Vide" not in noms


def test_list_batchs_all_when_actifs_false(client):
    client.post("/stock/batchs", json=_batch_payload(nom="Vide", portions_restantes=0))
    resp = client.get("/stock/batchs?actifs_seulement=false")
    assert len(resp.json()) == 1


def test_list_batchs_filter_stockage(client):
    client.post("/stock/batchs", json=_batch_payload(nom="Frigo", stockage="frigo"))
    client.post("/stock/batchs", json=_batch_payload(nom="Congel", stockage="congelateur"))
    resp = client.get("/stock/batchs?stockage=frigo")
    noms = [b["nom"] for b in resp.json()]
    assert noms == ["Frigo"]


# ===========================================================================
# GET /stock/batchs/{id}
# ===========================================================================


def test_get_batch_existing(client):
    b = client.post("/stock/batchs", json=_batch_payload()).json()
    resp = client.get(f"/stock/batchs/{b['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == b["id"]


def test_get_batch_nonexistent_404(client):
    resp = client.get(f"/stock/batchs/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_get_batch_after_delete_404(client):
    b = client.post("/stock/batchs", json=_batch_payload()).json()
    client.delete(f"/stock/batchs/{b['id']}")
    resp = client.get(f"/stock/batchs/{b['id']}")
    assert resp.status_code == 404


# ===========================================================================
# PATCH /stock/batchs/{id}
# ===========================================================================


def test_patch_batch_nom(client):
    b = client.post("/stock/batchs", json=_batch_payload(nom="Ancien")).json()
    resp = client.patch(f"/stock/batchs/{b['id']}", json={"nom": "Nouveau"})
    assert resp.status_code == 200
    assert resp.json()["nom"] == "Nouveau"


def test_patch_batch_partial_keeps_other_fields(client):
    b = client.post("/stock/batchs", json=_batch_payload(portions_total=8)).json()
    resp = client.patch(f"/stock/batchs/{b['id']}", json={"notes": "modif"})
    assert resp.json()["portions_total"] == 8


def test_patch_batch_nonexistent_404(client):
    resp = client.patch(f"/stock/batchs/{uuid.uuid4()}", json={"nom": "X"})
    assert resp.status_code == 404


# ===========================================================================
# POST /stock/batchs/{id}/consommer
# ===========================================================================


def test_consommer_decrements_portions(client):
    b = client.post("/stock/batchs", json=_batch_payload(portions_restantes=4)).json()
    resp = client.post(f"/stock/batchs/{b['id']}/consommer", json={"nb": 2})
    assert resp.status_code == 200
    assert resp.json()["portions_restantes"] == 2


def test_consommer_derniere_portion_soft_delete(client):
    b = client.post("/stock/batchs", json=_batch_payload(portions_restantes=1)).json()
    client.post(f"/stock/batchs/{b['id']}/consommer", json={"nb": 1})
    resp = client.get(f"/stock/batchs/{b['id']}")
    assert resp.status_code == 404


def test_consommer_zero_portions_409(client):
    b = client.post("/stock/batchs", json=_batch_payload(portions_restantes=0, actifs_seulement=False)).json()
    resp = client.post(f"/stock/batchs/{b['id']}/consommer", json={"nb": 1})
    assert resp.status_code == 409


def test_consommer_nonexistent_404(client):
    resp = client.post(f"/stock/batchs/{uuid.uuid4()}/consommer", json={"nb": 1})
    assert resp.status_code == 404


def test_consommer_default_nb_1(client):
    b = client.post("/stock/batchs", json=_batch_payload(portions_restantes=3)).json()
    resp = client.post(f"/stock/batchs/{b['id']}/consommer", json={})
    assert resp.status_code == 200
    assert resp.json()["portions_restantes"] == 2


# ===========================================================================
# DELETE /stock/batchs/{id}
# ===========================================================================


def test_delete_batch_204(client):
    b = client.post("/stock/batchs", json=_batch_payload()).json()
    resp = client.delete(f"/stock/batchs/{b['id']}")
    assert resp.status_code == 204


def test_delete_batch_hides_from_list(client):
    b = client.post("/stock/batchs", json=_batch_payload()).json()
    client.delete(f"/stock/batchs/{b['id']}")
    assert client.get("/stock/batchs").json() == []


def test_delete_batch_nonexistent_404(client):
    resp = client.delete(f"/stock/batchs/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# POST /stock/ingredients
# ===========================================================================


def test_create_ingredient_returns_201(client):
    resp = client.post("/stock/ingredients", json=_ingredient_payload())
    assert resp.status_code == 201


def test_create_ingredient_response_fields(client):
    resp = client.post("/stock/ingredients", json=_ingredient_payload(nom="Lait de coco"))
    body = resp.json()
    assert "id" in body
    assert body["nom"] == "Lait de coco"
    assert body["quantite"] is None


def test_create_ingredient_empty_nom_rejected(client):
    resp = client.post("/stock/ingredients", json={"nom": ""})
    assert resp.status_code == 422


# ===========================================================================
# GET /stock/ingredients
# ===========================================================================


def test_list_ingredients_empty(client):
    assert client.get("/stock/ingredients").json() == []


def test_list_ingredients_returns_created(client):
    client.post("/stock/ingredients", json=_ingredient_payload(nom="A"))
    client.post("/stock/ingredients", json=_ingredient_payload(nom="B"))
    noms = [i["nom"] for i in client.get("/stock/ingredients").json()]
    assert set(noms) == {"A", "B"}


def test_list_ingredients_filter_categorie(client):
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Lait", categorie="frigo"))
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Poivre", categorie="épices"))
    resp = client.get("/stock/ingredients?categorie=frigo")
    assert len(resp.json()) == 1
    assert resp.json()[0]["nom"] == "Lait"


# ===========================================================================
# GET /stock/ingredients/{id}
# ===========================================================================


def test_get_ingredient_existing(client):
    i = client.post("/stock/ingredients", json=_ingredient_payload()).json()
    resp = client.get(f"/stock/ingredients/{i['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == i["id"]


def test_get_ingredient_nonexistent_404(client):
    resp = client.get(f"/stock/ingredients/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# PATCH /stock/ingredients/{id}
# ===========================================================================


def test_patch_ingredient_nom(client):
    i = client.post("/stock/ingredients", json=_ingredient_payload(nom="Lait entier")).json()
    resp = client.patch(f"/stock/ingredients/{i['id']}", json={"nom": "Lait écrémé"})
    assert resp.status_code == 200
    assert resp.json()["nom"] == "Lait écrémé"


def test_patch_ingredient_quantite(client):
    i = client.post("/stock/ingredients", json=_ingredient_payload(quantite=12.0)).json()
    resp = client.patch(f"/stock/ingredients/{i['id']}", json={"quantite": 6.0})
    assert resp.json()["quantite"] == 6.0


def test_patch_ingredient_nonexistent_404(client):
    resp = client.patch(f"/stock/ingredients/{uuid.uuid4()}", json={"nom": "X"})
    assert resp.status_code == 404


# ===========================================================================
# DELETE /stock/ingredients/{id}
# ===========================================================================


def test_delete_ingredient_204(client):
    i = client.post("/stock/ingredients", json=_ingredient_payload()).json()
    resp = client.delete(f"/stock/ingredients/{i['id']}")
    assert resp.status_code == 204


def test_delete_ingredient_hides_from_list(client):
    i = client.post("/stock/ingredients", json=_ingredient_payload()).json()
    client.delete(f"/stock/ingredients/{i['id']}")
    assert client.get("/stock/ingredients").json() == []


def test_delete_ingredient_nonexistent_404(client):
    resp = client.delete(f"/stock/ingredients/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# GET /stock/ingredients/alertes
# ===========================================================================


def test_alertes_empty(client):
    resp = client.get("/stock/ingredients/alertes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_alertes_returns_sous_seuil(client):
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Oeufs", quantite=2.0, seuil_alerte=6.0))
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Lait", quantite=500.0, seuil_alerte=200.0))
    alertes = client.get("/stock/ingredients/alertes").json()
    assert len(alertes) == 1
    assert alertes[0]["nom"] == "Oeufs"


def test_alertes_excludes_no_seuil(client):
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Sel", quantite=10.0))
    assert client.get("/stock/ingredients/alertes").json() == []


# ===========================================================================
# GET /stock/resume
# ===========================================================================


def test_resume_structure(client):
    resp = client.get("/stock/resume")
    assert resp.status_code == 200
    body = resp.json()
    assert "batchs" in body
    assert "ingredients_alertes" in body


def test_resume_batchs_actifs(client):
    client.post("/stock/batchs", json=_batch_payload(nom="Actif", portions_restantes=3))
    client.post("/stock/batchs", json=_batch_payload(nom="Vide", portions_restantes=0))
    body = client.get("/stock/resume").json()
    noms = [b["nom"] for b in body["batchs"]]
    assert "Actif" in noms
    assert "Vide" not in noms


def test_resume_ingredients_alertes(client):
    client.post("/stock/ingredients", json=_ingredient_payload(nom="Beurre", quantite=10.0, seuil_alerte=100.0))
    body = client.get("/stock/resume").json()
    assert len(body["ingredients_alertes"]) == 1


# ===========================================================================
# 503 when no DB configured
# ===========================================================================


def test_stock_503_when_no_db():
    app = create_app(Settings())
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/stock/batchs")
    assert resp.status_code == 503
