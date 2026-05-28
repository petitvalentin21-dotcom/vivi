from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.meals.stock.models import Batch, IngredientBase
from app.meals.stock.schemas import (
    BatchCreate,
    BatchUpdate,
    IngredientBaseCreate,
    IngredientBaseUpdate,
)


class BatchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: BatchCreate) -> Batch:
        now = datetime.now(timezone.utc)
        batch = Batch(
            recette_id=data.recette_id,
            nom=data.nom,
            portions_total=data.portions_total,
            portions_restantes=data.portions_restantes,
            date_cuisson=data.date_cuisson,
            date_peremption=data.date_peremption,
            stockage=data.stockage,
            notes=data.notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(batch)
        self.session.commit()
        self.session.refresh(batch)
        return batch

    def update(self, id: uuid.UUID, data: BatchUpdate) -> Batch:
        batch = self.get(id)
        if batch is None:
            raise ValueError(f"Batch {id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(batch, key, value)
        batch.updated_at = datetime.now(timezone.utc)
        self.session.add(batch)
        self.session.commit()
        self.session.refresh(batch)
        return batch

    def consommer_portion(self, id: uuid.UUID, nb: int = 1) -> Batch:
        batch = self.get(id)
        if batch is None:
            raise ValueError(f"Batch {id} not found")
        batch.portions_restantes -= nb
        now = datetime.now(timezone.utc)
        batch.updated_at = now
        if batch.portions_restantes <= 0:
            batch.portions_restantes = 0
            batch.deleted_at = now
        self.session.add(batch)
        self.session.commit()
        self.session.refresh(batch)
        return batch

    def soft_delete(self, id: uuid.UUID) -> None:
        batch = self.get(id)
        if batch is None:
            raise ValueError(f"Batch {id} not found")
        now = datetime.now(timezone.utc)
        batch.deleted_at = now
        batch.updated_at = now
        self.session.add(batch)
        self.session.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: uuid.UUID, include_deleted: bool = False) -> Batch | None:
        stmt = select(Batch).where(Batch.id == id)
        if not include_deleted:
            stmt = stmt.where(Batch.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list(self, actifs_seulement: bool = True, stockage: str | None = None) -> list[Batch]:
        stmt = select(Batch).where(Batch.deleted_at.is_(None)).order_by(Batch.date_cuisson.desc())
        if actifs_seulement:
            stmt = stmt.where(Batch.portions_restantes > 0)
        if stockage is not None:
            stmt = stmt.where(Batch.stockage == stockage)
        return list(self.session.exec(stmt).all())

    def count_actifs(self) -> int:
        result = self.session.exec(
            select(func.count(Batch.id))
            .where(Batch.deleted_at.is_(None))
            .where(Batch.portions_restantes > 0)
        ).one()
        return int(result)


class IngredientBaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: IngredientBaseCreate) -> IngredientBase:
        now = datetime.now(timezone.utc)
        ingredient = IngredientBase(
            nom=data.nom,
            categorie=data.categorie,
            quantite=data.quantite,
            unite=data.unite,
            seuil_alerte=data.seuil_alerte,
            notes=data.notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def update(self, id: uuid.UUID, data: IngredientBaseUpdate) -> IngredientBase:
        ingredient = self.get(id)
        if ingredient is None:
            raise ValueError(f"IngredientBase {id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(ingredient, key, value)
        ingredient.updated_at = datetime.now(timezone.utc)
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def soft_delete(self, id: uuid.UUID) -> None:
        ingredient = self.get(id)
        if ingredient is None:
            raise ValueError(f"IngredientBase {id} not found")
        now = datetime.now(timezone.utc)
        ingredient.deleted_at = now
        ingredient.updated_at = now
        self.session.add(ingredient)
        self.session.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: uuid.UUID, include_deleted: bool = False) -> IngredientBase | None:
        stmt = select(IngredientBase).where(IngredientBase.id == id)
        if not include_deleted:
            stmt = stmt.where(IngredientBase.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list(self, categorie: str | None = None) -> list[IngredientBase]:
        stmt = select(IngredientBase).where(IngredientBase.deleted_at.is_(None)).order_by(IngredientBase.nom)
        if categorie is not None:
            stmt = stmt.where(IngredientBase.categorie == categorie)
        return list(self.session.exec(stmt).all())

    def get_alertes(self) -> list[IngredientBase]:
        stmt = (
            select(IngredientBase)
            .where(IngredientBase.deleted_at.is_(None))
            .where(IngredientBase.seuil_alerte.is_not(None))
            .where(IngredientBase.quantite.is_not(None))
            .where(IngredientBase.quantite < IngredientBase.seuil_alerte)
            .order_by(IngredientBase.nom)
        )
        return list(self.session.exec(stmt).all())
