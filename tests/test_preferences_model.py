"""Tests unitaires — PreferenceRepository et PreferenceService."""
from __future__ import annotations

import uuid

import pytest
from sqlmodel import Session

from app.db.connection import create_db_engine, run_migrations
from app.meals.preferences.repository import PreferenceRepository
from app.meals.preferences.schemas import PreferenceUpdate
from app.meals.preferences.service import PreferenceService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def session(tmp_path):
    db_path = str(tmp_path / "preferences_model_test.db")
    run_migrations(db_path)
    engine = create_db_engine(db_path)
    with Session(engine) as s:
        yield s
    engine.dispose()


@pytest.fixture()
def repo(session):
    return PreferenceRepository(session)


@pytest.fixture()
def service(repo):
    return PreferenceService(repo)


# ===========================================================================
# PreferenceRepository
# ===========================================================================


def test_create_default_type_valeur(repo):
    pref = repo.create(cle="regime", valeur="végétarien")
    assert pref.type_valeur == "string"
    assert pref.deleted_at is None


def test_create_custom_fields(repo):
    pref = repo.create(cle="taille_foyer", valeur="2", type_valeur="int", categorie="planning", notes="deux personnes")
    assert pref.categorie == "planning"
    assert pref.notes == "deux personnes"


def test_get_by_cle_existing(repo):
    repo.create(cle="regime", valeur="omnivore")
    pref = repo.get_by_cle("regime")
    assert pref is not None
    assert pref.cle == "regime"


def test_get_by_cle_unknown_returns_none(repo):
    assert repo.get_by_cle("inexistant") is None


def test_create_duplicate_raises(repo):
    repo.create(cle="regime", valeur="omnivore")
    with pytest.raises(ValueError):
        repo.create(cle="regime", valeur="végétarien")


def test_list_all(repo):
    repo.create(cle="a", valeur="1")
    repo.create(cle="b", valeur="2")
    items = repo.list()
    assert len(items) == 2


def test_list_filtered_by_categorie(repo):
    repo.create(cle="regime", valeur="omnivore", categorie="alimentaire")
    repo.create(cle="temps_max", valeur="45", categorie="planning")
    alimentaire = repo.list(categorie="alimentaire")
    assert len(alimentaire) == 1
    assert alimentaire[0].cle == "regime"


def test_list_ordered_by_cle(repo):
    repo.create(cle="z_pref", valeur="1")
    repo.create(cle="a_pref", valeur="2")
    cles = [p.cle for p in repo.list()]
    assert cles == sorted(cles)


def test_upsert_by_cle_creates_when_absent(repo):
    pref = repo.upsert_by_cle(cle="nouveau", valeur="test")
    assert pref.id is not None
    assert pref.cle == "nouveau"


def test_upsert_by_cle_updates_same_id(repo):
    created = repo.upsert_by_cle(cle="regime", valeur="omnivore")
    updated = repo.upsert_by_cle(cle="regime", valeur="végétarien")
    assert created.id == updated.id
    assert updated.valeur == "végétarien"


def test_soft_delete_hides_from_get(repo):
    pref = repo.create(cle="a_supprimer", valeur="x")
    repo.soft_delete(pref.id)
    assert repo.get(pref.id) is None


def test_soft_delete_hides_from_get_by_cle(repo):
    pref = repo.create(cle="a_supprimer", valeur="x")
    repo.soft_delete(pref.id)
    assert repo.get_by_cle("a_supprimer") is None


def test_soft_delete_hides_from_list(repo):
    pref = repo.create(cle="a_supprimer", valeur="x")
    repo.soft_delete(pref.id)
    assert repo.list() == []


def test_soft_delete_unknown_returns_false(repo):
    result = repo.soft_delete(uuid.uuid4())
    assert result is False


def test_soft_delete_known_returns_true(repo):
    pref = repo.create(cle="ok", valeur="v")
    assert repo.soft_delete(pref.id) is True


def test_update_sets_fields(repo):
    pref = repo.create(cle="regime", valeur="omnivore")
    updated = repo.update(pref.id, PreferenceUpdate(valeur="végétarien", categorie="alimentaire"))
    assert updated is not None
    assert updated.valeur == "végétarien"
    assert updated.categorie == "alimentaire"


def test_update_unknown_returns_none(repo):
    result = repo.update(uuid.uuid4(), PreferenceUpdate(valeur="x"))
    assert result is None


# ===========================================================================
# PreferenceService — encode / decode + API typée
# ===========================================================================


def test_service_get_value_default_when_absent(service):
    assert service.get_value("inexistant", default="fallback") == "fallback"


def test_service_set_get_string(service):
    service.set_value("regime", "végétarien")
    assert service.get_value("regime") == "végétarien"


def test_service_set_get_int(service):
    service.set_value("taille_foyer", 2, type_valeur="int")
    val = service.get_value("taille_foyer")
    assert val == 2
    assert isinstance(val, int)


def test_service_set_get_float(service):
    service.set_value("note", 4.5, type_valeur="float")
    val = service.get_value("note")
    assert val == pytest.approx(4.5)
    assert isinstance(val, float)


def test_service_set_get_bool_true(service):
    service.set_value("aime_epice", True, type_valeur="bool")
    assert service.get_value("aime_epice") is True


def test_service_set_get_bool_false(service):
    service.set_value("batch_cooking_actif", False, type_valeur="bool")
    assert service.get_value("batch_cooking_actif") is False


def test_service_set_get_list(service):
    service.set_value("allergies", ["gluten", "lactose"], type_valeur="list")
    val = service.get_value("allergies")
    assert val == ["gluten", "lactose"]
    assert isinstance(val, list)


def test_service_set_get_dict(service):
    data = {"wok": True, "cocotte": False}
    service.set_value("materiel", data, type_valeur="dict")
    val = service.get_value("materiel")
    assert val == data
    assert isinstance(val, dict)


def test_service_get_all_as_dict_mix_types(service):
    service.set_value("regime", "végétarien")
    service.set_value("taille_foyer", 2, type_valeur="int")
    service.set_value("aime_epice", True, type_valeur="bool")
    d = service.get_all_as_dict()
    assert d["regime"] == "végétarien"
    assert d["taille_foyer"] == 2
    assert d["aime_epice"] is True


def test_service_get_value_default_if_decode_fails(service):
    """Si la valeur stockée ne correspond pas au type_valeur, get_value retourne default."""
    service.repository.upsert_by_cle(cle="broken", valeur="abc", type_valeur="int")
    assert service.get_value("broken", default=-1) == -1


def test_service_get_all_as_dict_silently_ignores_decode_errors(service):
    service.repository.upsert_by_cle(cle="ok", valeur="hello", type_valeur="string")
    service.repository.upsert_by_cle(cle="broken", valeur="abc", type_valeur="int")
    d = service.get_all_as_dict()
    assert "ok" in d
    assert "broken" not in d
