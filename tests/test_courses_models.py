"""Tests unitaires — repositories et service CoursesService."""
from __future__ import annotations

import uuid

import pytest
from sqlmodel import Session

from app.db.connection import create_db_engine, run_migrations
from app.meals.courses.repository import ItemCourseRepository, ListeCoursesRepository
from app.meals.courses.schemas import (
    ItemCourseBody,
    ItemCourseCreate,
    ItemCourseUpdate,
    ListeCoursesCreate,
    ListeCoursesUpdate,
)
from app.meals.courses.service import CoursesService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def session(tmp_path):
    db_path = str(tmp_path / "courses_models_test.db")
    run_migrations(db_path)
    engine = create_db_engine(db_path)
    with Session(engine) as s:
        yield s
    engine.dispose()


@pytest.fixture()
def liste_repo(session):
    return ListeCoursesRepository(session)


@pytest.fixture()
def item_repo(session):
    return ItemCourseRepository(session)


@pytest.fixture()
def service(liste_repo, item_repo):
    return CoursesService(liste_repo, item_repo)


def _liste_create(**kwargs) -> ListeCoursesCreate:
    defaults = {"nom": "Courses semaine 23"}
    defaults.update(kwargs)
    return ListeCoursesCreate(**defaults)


def _item_create(liste_id: uuid.UUID, **kwargs) -> ItemCourseCreate:
    defaults = {"liste_id": liste_id, "nom": "lait de coco"}
    defaults.update(kwargs)
    return ItemCourseCreate(**defaults)


def _item_body(**kwargs) -> ItemCourseBody:
    defaults = {"nom": "lait de coco"}
    defaults.update(kwargs)
    return ItemCourseBody(**defaults)


# ===========================================================================
# ListeCoursesRepository
# ===========================================================================


def test_create_liste_returns_liste(liste_repo):
    liste = liste_repo.create(_liste_create())
    assert liste.id is not None
    assert liste.nom == "Courses semaine 23"
    assert liste.statut == "en_cours"


def test_get_liste_existing(liste_repo):
    liste = liste_repo.create(_liste_create())
    found = liste_repo.get(liste.id)
    assert found is not None
    assert found.id == liste.id


def test_get_liste_nonexistent(liste_repo):
    assert liste_repo.get(uuid.uuid4()) is None


def test_list_listes_empty(liste_repo):
    assert liste_repo.list() == []


def test_list_listes_returns_created(liste_repo):
    liste_repo.create(_liste_create(nom="A"))
    liste_repo.create(_liste_create(nom="B"))
    noms = [l.nom for l in liste_repo.list()]
    assert set(noms) == {"A", "B"}


def test_list_listes_filter_statut(liste_repo):
    liste_repo.create(_liste_create(nom="En cours", statut="en_cours"))
    liste_repo.create(_liste_create(nom="Terminée", statut="terminée"))
    en_cours = liste_repo.list(statut="en_cours")
    assert len(en_cours) == 1
    assert en_cours[0].nom == "En cours"


def test_list_listes_excludes_deleted(liste_repo):
    liste = liste_repo.create(_liste_create())
    liste_repo.soft_delete(liste.id)
    assert liste_repo.list() == []


def test_update_liste(liste_repo):
    liste = liste_repo.create(_liste_create(nom="Ancien"))
    updated = liste_repo.update(liste.id, ListeCoursesUpdate(nom="Nouveau"))
    assert updated.nom == "Nouveau"


def test_update_liste_nonexistent_raises(liste_repo):
    with pytest.raises(ValueError):
        liste_repo.update(uuid.uuid4(), ListeCoursesUpdate(nom="X"))


def test_soft_delete_liste_hides_from_list(liste_repo):
    liste = liste_repo.create(_liste_create())
    liste_repo.soft_delete(liste.id)
    assert liste_repo.get(liste.id) is None
    assert liste_repo.list() == []


def test_soft_delete_liste_nonexistent_raises(liste_repo):
    with pytest.raises(ValueError):
        liste_repo.soft_delete(uuid.uuid4())


def test_archiver_liste(liste_repo):
    liste = liste_repo.create(_liste_create())
    archived = liste_repo.archiver(liste.id)
    assert archived.statut == "archivée"


def test_archiver_liste_nonexistent_raises(liste_repo):
    with pytest.raises(ValueError):
        liste_repo.archiver(uuid.uuid4())


# ===========================================================================
# ItemCourseRepository
# ===========================================================================


def test_create_item_returns_item(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    assert item.id is not None
    assert item.nom == "lait de coco"
    assert item.achete is False
    assert item.liste_id == liste.id


def test_get_item_existing(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    found = item_repo.get(item.id)
    assert found is not None
    assert found.id == item.id


def test_get_item_nonexistent(item_repo):
    assert item_repo.get(uuid.uuid4()) is None


def test_list_by_liste_returns_items(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item_repo.create(_item_create(liste.id, nom="A"))
    item_repo.create(_item_create(liste.id, nom="B"))
    items = item_repo.list_by_liste(liste.id)
    assert len(items) == 2


def test_list_by_liste_excludes_deleted(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    item_repo.soft_delete(item.id)
    assert item_repo.list_by_liste(liste.id) == []


def test_list_by_liste_achetes_seulement(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item_a = item_repo.create(_item_create(liste.id, nom="A"))
    item_repo.create(_item_create(liste.id, nom="B"))
    item_repo.marquer_achete(item_a.id, True)
    achetes = item_repo.list_by_liste(liste.id, achetes_seulement=True)
    assert len(achetes) == 1
    assert achetes[0].nom == "A"


def test_marquer_achete_true(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    updated = item_repo.marquer_achete(item.id, True)
    assert updated.achete is True


def test_marquer_achete_false(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id, achete=True))
    updated = item_repo.marquer_achete(item.id, False)
    assert updated.achete is False


def test_marquer_achete_nonexistent_raises(item_repo):
    with pytest.raises(ValueError):
        item_repo.marquer_achete(uuid.uuid4())


def test_update_item(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    updated = item_repo.update(item.id, ItemCourseUpdate(nom="farine T65", quantite=500.0, unite="g"))
    assert updated.nom == "farine T65"
    assert updated.quantite == 500.0
    assert updated.unite == "g"


def test_update_item_nonexistent_raises(item_repo):
    with pytest.raises(ValueError):
        item_repo.update(uuid.uuid4(), ItemCourseUpdate(nom="X"))


def test_soft_delete_item(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item = item_repo.create(_item_create(liste.id))
    item_repo.soft_delete(item.id)
    assert item_repo.get(item.id) is None


def test_soft_delete_item_nonexistent_raises(item_repo):
    with pytest.raises(ValueError):
        item_repo.soft_delete(uuid.uuid4())


def test_tout_marquer_achete_returns_count(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item_repo.create(_item_create(liste.id, nom="A"))
    item_repo.create(_item_create(liste.id, nom="B"))
    item_repo.create(_item_create(liste.id, nom="C"))
    count = item_repo.tout_marquer_achete(liste.id)
    assert count == 3


def test_tout_marquer_achete_skips_already_bought(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item_a = item_repo.create(_item_create(liste.id, nom="A", achete=True))
    item_repo.create(_item_create(liste.id, nom="B"))
    count = item_repo.tout_marquer_achete(liste.id)
    assert count == 1


def test_tout_marquer_achete_all_items_bought_after(liste_repo, item_repo):
    liste = liste_repo.create(_liste_create())
    item_repo.create(_item_create(liste.id, nom="A"))
    item_repo.create(_item_create(liste.id, nom="B"))
    item_repo.tout_marquer_achete(liste.id)
    items = item_repo.list_by_liste(liste.id, achetes_seulement=True)
    assert len(items) == 2


# ===========================================================================
# CoursesService — opérations complexes
# ===========================================================================


def test_creer_liste_avec_items_creates_all(service, item_repo):
    liste_data = _liste_create(nom="Liste atomique")
    items = [_item_body(nom="A"), _item_body(nom="B"), _item_body(nom="C")]
    liste = service.creer_liste_avec_items(liste_data, items)
    assert liste.id is not None
    assert liste.nom == "Liste atomique"
    created_items = item_repo.list_by_liste(liste.id)
    assert len(created_items) == 3


def test_creer_liste_avec_items_empty_items(service, item_repo):
    liste = service.creer_liste_avec_items(_liste_create(), [])
    assert item_repo.list_by_liste(liste.id) == []


def test_get_resume_counts(service, item_repo):
    liste = service.creer_liste(ListeCoursesCreate(nom="Résumé"))
    item_a = service.create_item(ItemCourseCreate(liste_id=liste.id, nom="A"))
    service.create_item(ItemCourseCreate(liste_id=liste.id, nom="B"))
    service.marquer_achete(item_a.id, True)
    resume = service.get_resume(liste.id)
    assert resume["total"] == 2
    assert resume["nb_achetes"] == 1
    assert resume["nb_restants"] == 1
    assert resume["pct_avancement"] == 50


def test_get_resume_empty_liste(service):
    liste = service.creer_liste(ListeCoursesCreate(nom="Vide"))
    resume = service.get_resume(liste.id)
    assert resume["total"] == 0
    assert resume["pct_avancement"] == 0


def test_archiver_si_terminee_true_when_all_bought(service):
    liste = service.creer_liste(ListeCoursesCreate(nom="Terminée"))
    item = service.create_item(ItemCourseCreate(liste_id=liste.id, nom="A"))
    service.marquer_achete(item.id, True)
    result = service.archiver_si_terminee(liste.id)
    assert result is True
    updated = service.get_liste(liste.id)
    assert updated.statut == "archivée"


def test_archiver_si_terminee_false_when_remaining(service):
    liste = service.creer_liste(ListeCoursesCreate(nom="Partielle"))
    item_a = service.create_item(ItemCourseCreate(liste_id=liste.id, nom="A"))
    service.create_item(ItemCourseCreate(liste_id=liste.id, nom="B"))
    service.marquer_achete(item_a.id, True)
    result = service.archiver_si_terminee(liste.id)
    assert result is False
    updated = service.get_liste(liste.id)
    assert updated.statut == "en_cours"


def test_archiver_si_terminee_false_when_no_items(service):
    liste = service.creer_liste(ListeCoursesCreate(nom="Sans items"))
    result = service.archiver_si_terminee(liste.id)
    assert result is False
