"""Unit tests — RecetteRepository avec BDD SQLite temporaire."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import Session, SQLModel

from app.db.connection import create_db_engine
from app.meals.recettes.models import Recette
from app.meals.recettes.repository import RecetteRepository
from app.meals.recettes.schemas import RecetteCreate, RecetteUpdate


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path):
    engine = create_db_engine(str(tmp_path / "recettes_test.db"))
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield RecetteRepository(session)
    engine.dispose()


def _simple_create(**kwargs) -> RecetteCreate:
    defaults = dict(
        titre="Pasta carbonara",
        ingredients=[],
        etapes=["Cuire", "Mélanger"],
        portions=2,
        tags=["rapide"],
    )
    defaults.update(kwargs)
    return RecetteCreate(**defaults)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_create_returns_recette_with_id(repo):
    r = repo.create(_simple_create())
    assert r.id is not None
    assert isinstance(r.id, uuid.UUID)
    assert r.titre == "Pasta carbonara"


def test_create_sets_json_defaults(repo):
    r = repo.create(_simple_create())
    assert r.etapes == ["Cuire", "Mélanger"]
    assert r.tags == ["rapide"]
    assert r.ingredients == []


def test_create_with_ingredients(repo):
    data = _simple_create(
        ingredients=[
            {"nom": "pâtes", "quantite": 200, "unite": "g"},
            {"nom": "lardons", "quantite": None, "unite": None},
        ]
    )
    # Accept both dict and IngredientSchema for convenience in tests
    from app.meals.recettes.schemas import IngredientSchema

    data_typed = RecetteCreate(
        titre=data.titre,
        ingredients=[IngredientSchema(nom="pâtes", quantite=200, unite="g")],
        etapes=data.etapes,
        tags=data.tags,
    )
    r = repo.create(data_typed)
    assert len(r.ingredients) == 1
    assert r.ingredients[0]["nom"] == "pâtes"
    assert r.ingredients[0]["quantite"] == 200.0


def test_create_sets_timestamps(repo):
    before = datetime.now(timezone.utc)
    r = repo.create(_simple_create())
    after = datetime.now(timezone.utc)

    def to_utc(dt):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    assert before <= to_utc(r.created_at) <= after
    assert before <= to_utc(r.updated_at) <= after


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


def test_get_existing(repo):
    r = repo.create(_simple_create())
    found = repo.get(r.id)
    assert found is not None
    assert found.id == r.id


def test_get_nonexistent_returns_none(repo):
    assert repo.get(uuid.uuid4()) is None


def test_get_excludes_soft_deleted(repo):
    r = repo.create(_simple_create())
    repo.soft_delete(r.id)
    assert repo.get(r.id) is None


def test_get_include_deleted(repo):
    r = repo.create(_simple_create())
    repo.soft_delete(r.id)
    found = repo.get(r.id, include_deleted=True)
    assert found is not None
    assert found.deleted_at is not None


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_list_returns_all_active(repo):
    repo.create(_simple_create(titre="A"))
    repo.create(_simple_create(titre="B"))
    results = repo.list()
    assert len(results) == 2


def test_list_excludes_deleted(repo):
    r1 = repo.create(_simple_create(titre="Keep"))
    r2 = repo.create(_simple_create(titre="Delete"))
    repo.soft_delete(r2.id)
    results = repo.list()
    ids = [r.id for r in results]
    assert r1.id in ids
    assert r2.id not in ids


def test_list_pagination(repo):
    for i in range(5):
        repo.create(_simple_create(titre=f"R{i}"))
    page1 = repo.list(limit=2, offset=0)
    page2 = repo.list(limit=2, offset=2)
    assert len(page1) == 2
    assert len(page2) == 2
    assert {r.id for r in page1}.isdisjoint({r.id for r in page2})


def test_list_filter_by_tag(repo):
    repo.create(_simple_create(titre="Rapide", tags=["rapide", "végétarien"]))
    repo.create(_simple_create(titre="Longue", tags=["batch"]))
    results = repo.list(tag="rapide")
    assert len(results) == 1
    assert results[0].titre == "Rapide"


def test_list_tag_no_partial_match(repo):
    repo.create(_simple_create(titre="Test", tags=["rapide"]))
    # "rapid" is NOT a tag — must not match "rapide"
    assert repo.list(tag="rapid") == []


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_update_titre(repo):
    r = repo.create(_simple_create(titre="Old"))
    updated = repo.update(r.id, RecetteUpdate(titre="New"))
    assert updated.titre == "New"


def test_update_bumps_updated_at(repo):
    r = repo.create(_simple_create())
    before = datetime.now(timezone.utc)
    updated = repo.update(r.id, RecetteUpdate(titre="X"))

    def to_utc(dt):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    assert to_utc(updated.updated_at) >= before


def test_update_partial_leaves_other_fields(repo):
    r = repo.create(_simple_create(portions=4, tags=["batch"]))
    updated = repo.update(r.id, RecetteUpdate(titre="Changed"))
    assert updated.portions == 4
    assert "batch" in updated.tags


def test_update_nonexistent_raises(repo):
    with pytest.raises(ValueError, match="not found"):
        repo.update(uuid.uuid4(), RecetteUpdate(titre="X"))


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


def test_soft_delete_sets_deleted_at(repo):
    r = repo.create(_simple_create())
    repo.soft_delete(r.id)
    found = repo.get(r.id, include_deleted=True)
    assert found is not None
    assert found.deleted_at is not None


def test_soft_delete_nonexistent_raises(repo):
    with pytest.raises(ValueError, match="not found"):
        repo.soft_delete(uuid.uuid4())


# ---------------------------------------------------------------------------
# Search by tag + count
# ---------------------------------------------------------------------------


def test_search_by_tag(repo):
    repo.create(_simple_create(titre="A", tags=["végétarien"]))
    repo.create(_simple_create(titre="B", tags=["rapide"]))
    results = repo.search_by_tag("végétarien")
    assert len(results) == 1
    assert results[0].titre == "A"


def test_count_excludes_deleted(repo):
    repo.create(_simple_create())
    r2 = repo.create(_simple_create())
    repo.soft_delete(r2.id)
    assert repo.count() == 1


def test_count_empty(repo):
    assert repo.count() == 0
