"""Tests intégration — endpoints REST /courses."""
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
    app = create_app(Settings(db_path=str(tmp_path / "courses_api_test.db")))
    return TestClient(app)


def _liste_payload(**kwargs) -> dict:
    defaults = {"nom": "Courses semaine 23"}
    defaults.update(kwargs)
    return defaults


def _item_payload(**kwargs) -> dict:
    defaults = {"nom": "lait de coco"}
    defaults.update(kwargs)
    return defaults


def _create_liste(client, **kwargs) -> dict:
    return client.post("/courses/listes", json=_liste_payload(**kwargs)).json()


def _add_item(client, liste_id: str, **kwargs) -> dict:
    return client.post(f"/courses/listes/{liste_id}/items", json=_item_payload(**kwargs)).json()


# ===========================================================================
# POST /courses/listes
# ===========================================================================


def test_create_liste_returns_201(client):
    resp = client.post("/courses/listes", json=_liste_payload())
    assert resp.status_code == 201


def test_create_liste_response_fields(client):
    resp = client.post("/courses/listes", json=_liste_payload())
    body = resp.json()
    assert "id" in body
    assert body["nom"] == "Courses semaine 23"
    assert body["statut"] == "en_cours"
    assert body["notes"] is None


def test_create_liste_empty_nom_rejected(client):
    resp = client.post("/courses/listes", json=_liste_payload(nom=""))
    assert resp.status_code == 422


def test_create_liste_invalid_statut_rejected(client):
    resp = client.post("/courses/listes", json=_liste_payload(statut="inconnu"))
    assert resp.status_code == 422


def test_create_liste_with_notes(client):
    resp = client.post("/courses/listes", json=_liste_payload(notes="Pour la semaine"))
    assert resp.status_code == 201
    assert resp.json()["notes"] == "Pour la semaine"


# ===========================================================================
# GET /courses/listes
# ===========================================================================


def test_list_listes_empty(client):
    resp = client.get("/courses/listes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_listes_returns_created(client):
    _create_liste(client, nom="A")
    _create_liste(client, nom="B")
    resp = client.get("/courses/listes")
    noms = [l["nom"] for l in resp.json()]
    assert set(noms) == {"A", "B"}


def test_list_listes_filter_statut(client):
    _create_liste(client, nom="En cours", statut="en_cours")
    _create_liste(client, nom="Terminée", statut="terminée")
    resp = client.get("/courses/listes?statut=en_cours")
    assert len(resp.json()) == 1
    assert resp.json()[0]["nom"] == "En cours"


def test_list_listes_excludes_deleted(client):
    liste = _create_liste(client)
    client.delete(f"/courses/listes/{liste['id']}")
    assert client.get("/courses/listes").json() == []


# ===========================================================================
# GET /courses/listes/{id}
# ===========================================================================


def test_get_liste_existing(client):
    liste = _create_liste(client)
    resp = client.get(f"/courses/listes/{liste['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == liste["id"]


def test_get_liste_nonexistent_404(client):
    resp = client.get(f"/courses/listes/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_get_liste_after_delete_404(client):
    liste = _create_liste(client)
    client.delete(f"/courses/listes/{liste['id']}")
    resp = client.get(f"/courses/listes/{liste['id']}")
    assert resp.status_code == 404


# ===========================================================================
# PATCH /courses/listes/{id}
# ===========================================================================


def test_patch_liste_nom(client):
    liste = _create_liste(client, nom="Ancien")
    resp = client.patch(f"/courses/listes/{liste['id']}", json={"nom": "Nouveau"})
    assert resp.status_code == 200
    assert resp.json()["nom"] == "Nouveau"


def test_patch_liste_statut(client):
    liste = _create_liste(client)
    resp = client.patch(f"/courses/listes/{liste['id']}", json={"statut": "terminée"})
    assert resp.json()["statut"] == "terminée"


def test_patch_liste_partial_keeps_other_fields(client):
    liste = _create_liste(client, nom="Original", notes="A conserver")
    resp = client.patch(f"/courses/listes/{liste['id']}", json={"statut": "terminée"})
    assert resp.json()["nom"] == "Original"
    assert resp.json()["notes"] == "A conserver"


def test_patch_liste_nonexistent_404(client):
    resp = client.patch(f"/courses/listes/{uuid.uuid4()}", json={"nom": "X"})
    assert resp.status_code == 404


# ===========================================================================
# POST /courses/listes/{id}/archiver
# ===========================================================================


def test_archiver_liste(client):
    liste = _create_liste(client)
    resp = client.post(f"/courses/listes/{liste['id']}/archiver")
    assert resp.status_code == 200
    assert resp.json()["statut"] == "archivée"


def test_archiver_liste_nonexistent_404(client):
    resp = client.post(f"/courses/listes/{uuid.uuid4()}/archiver")
    assert resp.status_code == 404


# ===========================================================================
# DELETE /courses/listes/{id}
# ===========================================================================


def test_delete_liste_204(client):
    liste = _create_liste(client)
    resp = client.delete(f"/courses/listes/{liste['id']}")
    assert resp.status_code == 204


def test_delete_liste_hides_from_list(client):
    liste = _create_liste(client)
    client.delete(f"/courses/listes/{liste['id']}")
    assert client.get("/courses/listes").json() == []


def test_delete_liste_nonexistent_404(client):
    resp = client.delete(f"/courses/listes/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# GET /courses/listes/{id}/resume
# ===========================================================================


def test_resume_structure(client):
    liste = _create_liste(client)
    resp = client.get(f"/courses/listes/{liste['id']}/resume")
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "nb_achetes" in body
    assert "nb_restants" in body
    assert "pct_avancement" in body


def test_resume_counts(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], nom="A")
    _add_item(client, liste["id"], nom="B")
    client.post(f"/courses/items/{item['id']}/acheter", json={"valeur": True})
    body = client.get(f"/courses/listes/{liste['id']}/resume").json()
    assert body["total"] == 2
    assert body["nb_achetes"] == 1
    assert body["nb_restants"] == 1
    assert body["pct_avancement"] == 50


def test_resume_nonexistent_liste_404(client):
    resp = client.get(f"/courses/listes/{uuid.uuid4()}/resume")
    assert resp.status_code == 404


# ===========================================================================
# POST /courses/listes/{id}/items
# ===========================================================================


def test_add_item_returns_201(client):
    liste = _create_liste(client)
    resp = client.post(f"/courses/listes/{liste['id']}/items", json=_item_payload())
    assert resp.status_code == 201


def test_add_item_response_fields(client):
    liste = _create_liste(client)
    resp = client.post(f"/courses/listes/{liste['id']}/items", json=_item_payload(nom="farine", quantite=500.0, unite="g"))
    body = resp.json()
    assert "id" in body
    assert body["nom"] == "farine"
    assert body["quantite"] == 500.0
    assert body["unite"] == "g"
    assert body["achete"] is False
    assert body["liste_id"] == liste["id"]


def test_add_item_empty_nom_rejected(client):
    liste = _create_liste(client)
    resp = client.post(f"/courses/listes/{liste['id']}/items", json={"nom": ""})
    assert resp.status_code == 422


def test_add_item_to_nonexistent_liste_404(client):
    resp = client.post(f"/courses/listes/{uuid.uuid4()}/items", json=_item_payload())
    assert resp.status_code == 404


# ===========================================================================
# GET /courses/listes/{id}/items
# ===========================================================================


def test_list_items_empty(client):
    liste = _create_liste(client)
    resp = client.get(f"/courses/listes/{liste['id']}/items")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_items_returns_created(client):
    liste = _create_liste(client)
    _add_item(client, liste["id"], nom="A")
    _add_item(client, liste["id"], nom="B")
    items = client.get(f"/courses/listes/{liste['id']}/items").json()
    noms = [i["nom"] for i in items]
    assert set(noms) == {"A", "B"}


def test_list_items_achetes_seulement(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], nom="A")
    _add_item(client, liste["id"], nom="B")
    client.post(f"/courses/items/{item['id']}/acheter", json={"valeur": True})
    resp = client.get(f"/courses/listes/{liste['id']}/items?achetes_seulement=true")
    assert len(resp.json()) == 1
    assert resp.json()[0]["nom"] == "A"


def test_list_items_nonexistent_liste_404(client):
    resp = client.get(f"/courses/listes/{uuid.uuid4()}/items")
    assert resp.status_code == 404


# ===========================================================================
# PATCH /courses/items/{id}
# ===========================================================================


def test_patch_item_nom(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], nom="Ancien")
    resp = client.patch(f"/courses/items/{item['id']}", json={"nom": "Nouveau"})
    assert resp.status_code == 200
    assert resp.json()["nom"] == "Nouveau"


def test_patch_item_quantite_et_unite(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"])
    resp = client.patch(f"/courses/items/{item['id']}", json={"quantite": 2.0, "unite": "boîtes"})
    assert resp.json()["quantite"] == 2.0
    assert resp.json()["unite"] == "boîtes"


def test_patch_item_partial_keeps_other_fields(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], nom="Original", categorie="frais")
    resp = client.patch(f"/courses/items/{item['id']}", json={"quantite": 3.0})
    assert resp.json()["nom"] == "Original"
    assert resp.json()["categorie"] == "frais"


def test_patch_item_nonexistent_404(client):
    resp = client.patch(f"/courses/items/{uuid.uuid4()}", json={"nom": "X"})
    assert resp.status_code == 404


# ===========================================================================
# POST /courses/items/{id}/acheter
# ===========================================================================


def test_acheter_item_true(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"])
    resp = client.post(f"/courses/items/{item['id']}/acheter", json={"valeur": True})
    assert resp.status_code == 200
    assert resp.json()["achete"] is True


def test_acheter_item_false_unmarks(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], achete=True)
    resp = client.post(f"/courses/items/{item['id']}/acheter", json={"valeur": False})
    assert resp.json()["achete"] is False


def test_acheter_item_default_true(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"])
    resp = client.post(f"/courses/items/{item['id']}/acheter", json={})
    assert resp.json()["achete"] is True


def test_acheter_item_nonexistent_404(client):
    resp = client.post(f"/courses/items/{uuid.uuid4()}/acheter", json={"valeur": True})
    assert resp.status_code == 404


# ===========================================================================
# DELETE /courses/items/{id}
# ===========================================================================


def test_delete_item_204(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"])
    resp = client.delete(f"/courses/items/{item['id']}")
    assert resp.status_code == 204


def test_delete_item_hides_from_list(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"])
    client.delete(f"/courses/items/{item['id']}")
    assert client.get(f"/courses/listes/{liste['id']}/items").json() == []


def test_delete_item_nonexistent_404(client):
    resp = client.delete(f"/courses/items/{uuid.uuid4()}")
    assert resp.status_code == 404


# ===========================================================================
# POST /courses/listes/{id}/tout-acheter
# ===========================================================================


def test_tout_acheter_marks_all(client):
    liste = _create_liste(client)
    _add_item(client, liste["id"], nom="A")
    _add_item(client, liste["id"], nom="B")
    resp = client.post(f"/courses/listes/{liste['id']}/tout-acheter")
    assert resp.status_code == 200
    assert resp.json()["nb_mis_a_jour"] == 2
    items = client.get(f"/courses/listes/{liste['id']}/items").json()
    assert all(i["achete"] for i in items)


def test_tout_acheter_returns_count_of_updated(client):
    liste = _create_liste(client)
    item = _add_item(client, liste["id"], nom="A", achete=True)
    _add_item(client, liste["id"], nom="B")
    resp = client.post(f"/courses/listes/{liste['id']}/tout-acheter")
    assert resp.json()["nb_mis_a_jour"] == 1


def test_tout_acheter_nonexistent_liste_404(client):
    resp = client.post(f"/courses/listes/{uuid.uuid4()}/tout-acheter")
    assert resp.status_code == 404


# ===========================================================================
# 503 when no DB configured
# ===========================================================================


def test_courses_503_when_no_db():
    app = create_app(Settings())
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/courses/listes")
    assert resp.status_code == 503
