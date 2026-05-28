"""Unit tests — BatchRepository + IngredientBaseRepository avec BDD SQLite temporaire."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest
from sqlmodel import Session, SQLModel

from app.db.connection import create_db_engine
from app.meals.stock.models import Batch, IngredientBase
from app.meals.stock.repository import BatchRepository, IngredientBaseRepository
from app.meals.stock.schemas import (
    BatchCreate,
    BatchUpdate,
    IngredientBaseCreate,
    IngredientBaseUpdate,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def batch_repo(tmp_path):
    engine = create_db_engine(str(tmp_path / "stock_test.db"))
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield BatchRepository(session)
    engine.dispose()


@pytest.fixture()
def ingredient_repo(tmp_path):
    engine = create_db_engine(str(tmp_path / "stock_test.db"))
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield IngredientBaseRepository(session)
    engine.dispose()


def _batch(**kwargs) -> BatchCreate:
    defaults = dict(
        nom="Dahl lentilles corail",
        portions_total=6,
        portions_restantes=6,
        date_cuisson=date(2026, 5, 28),
    )
    defaults.update(kwargs)
    return BatchCreate(**defaults)


def _ingredient(**kwargs) -> IngredientBaseCreate:
    defaults = dict(nom="Oeufs")
    defaults.update(kwargs)
    return IngredientBaseCreate(**defaults)


# ===========================================================================
# BatchRepository
# ===========================================================================


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_batch_create_returns_id(batch_repo):
    b = batch_repo.create(_batch())
    assert b.id is not None
    assert isinstance(b.id, uuid.UUID)
    assert b.nom == "Dahl lentilles corail"


def test_batch_create_defaults(batch_repo):
    b = batch_repo.create(_batch())
    assert b.stockage == "frigo"
    assert b.recette_id is None
    assert b.deleted_at is None


def test_batch_create_timestamps(batch_repo):
    before = datetime.now(timezone.utc)
    b = batch_repo.create(_batch())
    after = datetime.now(timezone.utc)

    def _utc(dt):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    assert before <= _utc(b.created_at) <= after
    assert before <= _utc(b.updated_at) <= after


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


def test_batch_get_existing(batch_repo):
    b = batch_repo.create(_batch())
    found = batch_repo.get(b.id)
    assert found is not None
    assert found.id == b.id


def test_batch_get_nonexistent(batch_repo):
    assert batch_repo.get(uuid.uuid4()) is None


def test_batch_get_excludes_soft_deleted(batch_repo):
    b = batch_repo.create(_batch())
    batch_repo.soft_delete(b.id)
    assert batch_repo.get(b.id) is None


def test_batch_get_include_deleted(batch_repo):
    b = batch_repo.create(_batch())
    batch_repo.soft_delete(b.id)
    found = batch_repo.get(b.id, include_deleted=True)
    assert found is not None
    assert found.deleted_at is not None


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_batch_list_actifs(batch_repo):
    batch_repo.create(_batch(nom="A"))
    batch_repo.create(_batch(nom="B"))
    results = batch_repo.list(actifs_seulement=True)
    assert len(results) == 2


def test_batch_list_excludes_deleted(batch_repo):
    b1 = batch_repo.create(_batch(nom="Keep"))
    b2 = batch_repo.create(_batch(nom="Delete"))
    batch_repo.soft_delete(b2.id)
    results = batch_repo.list(actifs_seulement=False)
    ids = [r.id for r in results]
    assert b1.id in ids
    assert b2.id not in ids


def test_batch_list_actifs_excludes_zero_portions(batch_repo):
    batch_repo.create(_batch(nom="Vide", portions_restantes=0))
    batch_repo.create(_batch(nom="Plein", portions_restantes=3))
    results = batch_repo.list(actifs_seulement=True)
    assert len(results) == 1
    assert results[0].nom == "Plein"


def test_batch_list_filter_stockage(batch_repo):
    batch_repo.create(_batch(nom="Frigo", stockage="frigo"))
    batch_repo.create(_batch(nom="Congel", stockage="congelateur"))
    results = batch_repo.list(stockage="frigo")
    assert len(results) == 1
    assert results[0].nom == "Frigo"


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_batch_update_nom(batch_repo):
    b = batch_repo.create(_batch(nom="Ancien"))
    updated = batch_repo.update(b.id, BatchUpdate(nom="Nouveau"))
    assert updated.nom == "Nouveau"


def test_batch_update_bumps_updated_at(batch_repo):
    b = batch_repo.create(_batch())
    before = datetime.now(timezone.utc)
    updated = batch_repo.update(b.id, BatchUpdate(notes="modif"))

    def _utc(dt):
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    assert _utc(updated.updated_at) >= before


def test_batch_update_nonexistent_raises(batch_repo):
    with pytest.raises(ValueError, match="not found"):
        batch_repo.update(uuid.uuid4(), BatchUpdate(nom="X"))


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


def test_batch_soft_delete_sets_deleted_at(batch_repo):
    b = batch_repo.create(_batch())
    batch_repo.soft_delete(b.id)
    found = batch_repo.get(b.id, include_deleted=True)
    assert found.deleted_at is not None


def test_batch_soft_delete_nonexistent_raises(batch_repo):
    with pytest.raises(ValueError, match="not found"):
        batch_repo.soft_delete(uuid.uuid4())


# ---------------------------------------------------------------------------
# consommer_portion
# ---------------------------------------------------------------------------


def test_consommer_portion_decrements(batch_repo):
    b = batch_repo.create(_batch(portions_restantes=3))
    updated = batch_repo.consommer_portion(b.id, 1)
    assert updated.portions_restantes == 2


def test_consommer_portion_derniere_soft_delete(batch_repo):
    b = batch_repo.create(_batch(portions_restantes=1))
    updated = batch_repo.consommer_portion(b.id, 1)
    assert updated.portions_restantes == 0
    assert updated.deleted_at is not None


def test_consommer_portion_nonexistent_raises(batch_repo):
    with pytest.raises(ValueError, match="not found"):
        batch_repo.consommer_portion(uuid.uuid4())


# ---------------------------------------------------------------------------
# count_actifs
# ---------------------------------------------------------------------------


def test_count_actifs(batch_repo):
    batch_repo.create(_batch(nom="A", portions_restantes=3))
    batch_repo.create(_batch(nom="B", portions_restantes=0))
    b3 = batch_repo.create(_batch(nom="C", portions_restantes=2))
    batch_repo.soft_delete(b3.id)
    assert batch_repo.count_actifs() == 1


def test_count_actifs_empty(batch_repo):
    assert batch_repo.count_actifs() == 0


# ===========================================================================
# IngredientBaseRepository
# ===========================================================================


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_ingredient_create_returns_id(ingredient_repo):
    i = ingredient_repo.create(_ingredient())
    assert i.id is not None
    assert i.nom == "Oeufs"


def test_ingredient_create_defaults(ingredient_repo):
    i = ingredient_repo.create(_ingredient())
    assert i.categorie is None
    assert i.quantite is None
    assert i.seuil_alerte is None
    assert i.deleted_at is None


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------


def test_ingredient_get_existing(ingredient_repo):
    i = ingredient_repo.create(_ingredient())
    found = ingredient_repo.get(i.id)
    assert found is not None
    assert found.id == i.id


def test_ingredient_get_nonexistent(ingredient_repo):
    assert ingredient_repo.get(uuid.uuid4()) is None


def test_ingredient_get_excludes_deleted(ingredient_repo):
    i = ingredient_repo.create(_ingredient())
    ingredient_repo.soft_delete(i.id)
    assert ingredient_repo.get(i.id) is None


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_ingredient_list_all(ingredient_repo):
    ingredient_repo.create(_ingredient(nom="A"))
    ingredient_repo.create(_ingredient(nom="B"))
    assert len(ingredient_repo.list()) == 2


def test_ingredient_list_excludes_deleted(ingredient_repo):
    i1 = ingredient_repo.create(_ingredient(nom="Keep"))
    i2 = ingredient_repo.create(_ingredient(nom="Delete"))
    ingredient_repo.soft_delete(i2.id)
    ids = [r.id for r in ingredient_repo.list()]
    assert i1.id in ids
    assert i2.id not in ids


def test_ingredient_list_filter_categorie(ingredient_repo):
    ingredient_repo.create(_ingredient(nom="Lait", categorie="frigo"))
    ingredient_repo.create(_ingredient(nom="Poivre", categorie="épices"))
    results = ingredient_repo.list(categorie="frigo")
    assert len(results) == 1
    assert results[0].nom == "Lait"


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_ingredient_update_nom(ingredient_repo):
    i = ingredient_repo.create(_ingredient(nom="Lait entier"))
    updated = ingredient_repo.update(i.id, IngredientBaseUpdate(nom="Lait demi-écrémé"))
    assert updated.nom == "Lait demi-écrémé"


def test_ingredient_update_quantite(ingredient_repo):
    i = ingredient_repo.create(_ingredient(nom="Oeufs", quantite=12.0))
    updated = ingredient_repo.update(i.id, IngredientBaseUpdate(quantite=6.0))
    assert updated.quantite == 6.0


def test_ingredient_update_nonexistent_raises(ingredient_repo):
    with pytest.raises(ValueError, match="not found"):
        ingredient_repo.update(uuid.uuid4(), IngredientBaseUpdate(nom="X"))


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------


def test_ingredient_soft_delete_sets_deleted_at(ingredient_repo):
    i = ingredient_repo.create(_ingredient())
    ingredient_repo.soft_delete(i.id)
    found = ingredient_repo.get(i.id, include_deleted=True)
    assert found.deleted_at is not None


def test_ingredient_soft_delete_nonexistent_raises(ingredient_repo):
    with pytest.raises(ValueError, match="not found"):
        ingredient_repo.soft_delete(uuid.uuid4())


# ---------------------------------------------------------------------------
# get_alertes
# ---------------------------------------------------------------------------


def test_get_alertes_returns_sous_seuil(ingredient_repo):
    ingredient_repo.create(_ingredient(nom="Oeufs", quantite=2.0, seuil_alerte=6.0))
    ingredient_repo.create(_ingredient(nom="Lait", quantite=500.0, seuil_alerte=200.0))
    alertes = ingredient_repo.get_alertes()
    assert len(alertes) == 1
    assert alertes[0].nom == "Oeufs"


def test_get_alertes_excludes_no_seuil(ingredient_repo):
    ingredient_repo.create(_ingredient(nom="Sel", quantite=10.0, seuil_alerte=None))
    assert ingredient_repo.get_alertes() == []


def test_get_alertes_excludes_no_quantite(ingredient_repo):
    ingredient_repo.create(_ingredient(nom="Poivre", quantite=None, seuil_alerte=5.0))
    assert ingredient_repo.get_alertes() == []


def test_get_alertes_excludes_deleted(ingredient_repo):
    i = ingredient_repo.create(_ingredient(nom="Beurre", quantite=50.0, seuil_alerte=100.0))
    ingredient_repo.soft_delete(i.id)
    assert ingredient_repo.get_alertes() == []
