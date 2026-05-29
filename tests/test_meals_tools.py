"""Tests unitaires — callables des 5 outils Repas (session in-memory)."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from sqlmodel import Session

import app.tools  # noqa: F401 — side-effect: registers all tools
from app.db.connection import create_db_engine, run_migrations
from app.meals.courses.repository import ItemCourseRepository, ListeCoursesRepository
from app.meals.courses.schemas import ItemCourseCreate, ListeCoursesCreate
from app.meals.preferences.repository import PreferenceRepository
from app.meals.recettes.repository import RecetteRepository
from app.meals.recettes.schemas import RecetteCreate
from app.meals.stock.repository import BatchRepository, IngredientBaseRepository
from app.meals.stock.schemas import BatchCreate, IngredientBaseCreate
from app.tools.registry import get_tool


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def session(tmp_path):
    db_path = str(tmp_path / "meals_tools_test.db")
    run_migrations(db_path)
    engine = create_db_engine(db_path)
    with Session(engine) as s:
        yield s
    engine.dispose()


# ---------------------------------------------------------------------------
# list_recettes
# ---------------------------------------------------------------------------


def test_list_recettes_empty(session):
    tool = get_tool("list_recettes")
    result = tool.callable(session)
    assert result == []


def test_list_recettes_returns_items(session):
    repo = RecetteRepository(session)
    repo.create(RecetteCreate(titre="Dahl de lentilles", tags=["végétarien", "batch"]))
    repo.create(RecetteCreate(titre="Poulet rôti"))
    tool = get_tool("list_recettes")
    result = tool.callable(session)
    assert len(result) == 2
    assert all("id" in r for r in result)
    assert any(r["titre"] == "Dahl de lentilles" for r in result)


def test_list_recettes_result_is_json_serializable(session):
    import json
    repo = RecetteRepository(session)
    repo.create(RecetteCreate(titre="Wok de légumes"))
    result = get_tool("list_recettes").callable(session)
    json.dumps(result)  # must not raise


# ---------------------------------------------------------------------------
# get_recette_by_id
# ---------------------------------------------------------------------------


def test_get_recette_by_id_returns_correct(session):
    repo = RecetteRepository(session)
    r = repo.create(RecetteCreate(titre="Soupe potiron", etapes=["Cuire"], tags=["soupe"]))
    tool = get_tool("get_recette_by_id")
    result = tool.callable(session, recette_id=str(r.id))
    assert result["id"] == str(r.id)
    assert result["titre"] == "Soupe potiron"
    assert result["tags"] == ["soupe"]


def test_get_recette_by_id_unknown_raises(session):
    tool = get_tool("get_recette_by_id")
    with pytest.raises(ValueError, match="introuvable"):
        tool.callable(session, recette_id=str(uuid.uuid4()))


def test_get_recette_by_id_invalid_uuid_raises(session):
    tool = get_tool("get_recette_by_id")
    with pytest.raises(ValueError):
        tool.callable(session, recette_id="pas-un-uuid")


# ---------------------------------------------------------------------------
# list_stock
# ---------------------------------------------------------------------------


def test_list_stock_empty(session):
    tool = get_tool("list_stock")
    result = tool.callable(session)
    assert result == {"batchs": [], "ingredients": []}


def test_list_stock_returns_batchs_and_ingredients(session):
    batch_repo = BatchRepository(session)
    ingredient_repo = IngredientBaseRepository(session)
    batch_repo.create(BatchCreate(
        nom="Dahl batch",
        portions_total=4,
        portions_restantes=4,
        date_cuisson=date.today(),
    ))
    ingredient_repo.create(IngredientBaseCreate(nom="Riz", categorie="féculents"))
    ingredient_repo.create(IngredientBaseCreate(nom="Courgette", categorie="légumes"))
    tool = get_tool("list_stock")
    result = tool.callable(session)
    assert len(result["batchs"]) == 1
    assert result["batchs"][0]["nom"] == "Dahl batch"
    assert len(result["ingredients"]) == 2


def test_list_stock_categorie_filter(session):
    ingredient_repo = IngredientBaseRepository(session)
    ingredient_repo.create(IngredientBaseCreate(nom="Riz", categorie="féculents"))
    ingredient_repo.create(IngredientBaseCreate(nom="Courgette", categorie="légumes"))
    tool = get_tool("list_stock")
    result = tool.callable(session, categorie="légumes")
    assert len(result["ingredients"]) == 1
    assert result["ingredients"][0]["nom"] == "Courgette"
    assert result["batchs"] == []


# ---------------------------------------------------------------------------
# list_courses
# ---------------------------------------------------------------------------


def test_list_courses_empty(session):
    tool = get_tool("list_courses")
    result = tool.callable(session)
    assert result == []


def test_list_courses_returns_active_lists_with_items(session):
    liste_repo = ListeCoursesRepository(session)
    item_repo = ItemCourseRepository(session)
    liste = liste_repo.create(ListeCoursesCreate(nom="Courses semaine", statut="en_cours"))
    item_repo.create(ItemCourseCreate(liste_id=liste.id, nom="Lentilles corail"))
    item_repo.create(ItemCourseCreate(liste_id=liste.id, nom="Crème de coco"))
    tool = get_tool("list_courses")
    result = tool.callable(session)
    assert len(result) == 1
    assert result[0]["nom"] == "Courses semaine"
    assert len(result[0]["items"]) == 2


def test_list_courses_excludes_terminated_lists(session):
    liste_repo = ListeCoursesRepository(session)
    liste_repo.create(ListeCoursesCreate(nom="Terminée", statut="terminée"))
    liste_repo.create(ListeCoursesCreate(nom="En cours", statut="en_cours"))
    tool = get_tool("list_courses")
    result = tool.callable(session)
    assert len(result) == 1
    assert result[0]["nom"] == "En cours"


# ---------------------------------------------------------------------------
# get_preferences_resume
# ---------------------------------------------------------------------------


def test_get_preferences_resume_empty(session):
    tool = get_tool("get_preferences_resume")
    result = tool.callable(session)
    assert result == {}


def test_get_preferences_resume_returns_decoded_dict(session):
    repo = PreferenceRepository(session)
    repo.upsert_by_cle(cle="regime", valeur="végétarien")
    repo.upsert_by_cle(cle="taille_foyer", valeur="2", type_valeur="int")
    repo.upsert_by_cle(cle="aime_epice", valeur="true", type_valeur="bool")
    tool = get_tool("get_preferences_resume")
    result = tool.callable(session)
    assert result["regime"] == "végétarien"
    assert result["taille_foyer"] == 2
    assert result["aime_epice"] is True


def test_get_preferences_resume_is_json_serializable(session):
    import json
    repo = PreferenceRepository(session)
    repo.upsert_by_cle(cle="allergies", valeur='["gluten", "lactose"]', type_valeur="list")
    result = get_tool("get_preferences_resume").callable(session)
    json.dumps(result)  # must not raise
