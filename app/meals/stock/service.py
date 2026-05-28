from __future__ import annotations

import uuid
from datetime import date

from app.meals.stock.models import Batch, IngredientBase
from app.meals.stock.repository import BatchRepository, IngredientBaseRepository
from app.meals.stock.schemas import (
    BatchCreate,
    BatchUpdate,
    IngredientBaseCreate,
    IngredientBaseUpdate,
)


class StockService:
    def __init__(self, batch_repo: BatchRepository, ingredient_repo: IngredientBaseRepository) -> None:
        self.batch_repo = batch_repo
        self.ingredient_repo = ingredient_repo

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    def create_batch(self, data: BatchCreate) -> Batch:
        return self.batch_repo.create(data)

    def get_batch(self, id: uuid.UUID) -> Batch | None:
        return self.batch_repo.get(id)

    def list_batchs(self, actifs_seulement: bool = True, stockage: str | None = None) -> list[Batch]:
        return self.batch_repo.list(actifs_seulement=actifs_seulement, stockage=stockage)

    def update_batch(self, id: uuid.UUID, data: BatchUpdate) -> Batch:
        return self.batch_repo.update(id, data)

    def soft_delete_batch(self, id: uuid.UUID) -> None:
        self.batch_repo.soft_delete(id)

    def consommer_portion(self, id: uuid.UUID, nb: int = 1) -> Batch:
        batch = self.batch_repo.get(id)
        if batch is None:
            raise ValueError(f"Batch {id} not found")
        if batch.portions_restantes <= 0:
            raise ValueError("Aucune portion restante à consommer")
        if nb > batch.portions_restantes:
            raise ValueError(f"Seulement {batch.portions_restantes} portion(s) disponible(s)")
        return self.batch_repo.consommer_portion(id, nb)

    # ------------------------------------------------------------------
    # IngredientBase
    # ------------------------------------------------------------------

    def create_ingredient(self, data: IngredientBaseCreate) -> IngredientBase:
        return self.ingredient_repo.create(data)

    def get_ingredient(self, id: uuid.UUID) -> IngredientBase | None:
        return self.ingredient_repo.get(id)

    def list_ingredients(self, categorie: str | None = None) -> list[IngredientBase]:
        return self.ingredient_repo.list(categorie=categorie)

    def update_ingredient(self, id: uuid.UUID, data: IngredientBaseUpdate) -> IngredientBase:
        return self.ingredient_repo.update(id, data)

    def soft_delete_ingredient(self, id: uuid.UUID) -> None:
        self.ingredient_repo.soft_delete(id)

    def get_alertes(self) -> list[IngredientBase]:
        return self.ingredient_repo.get_alertes()

    # ------------------------------------------------------------------
    # Vue synthétique
    # ------------------------------------------------------------------

    def get_stock_actif(self) -> dict:
        today = date.today()
        batchs = self.batch_repo.list(actifs_seulement=True)
        batchs_valides = [
            b for b in batchs
            if b.date_peremption is None or b.date_peremption >= today
        ]
        return {
            "batchs": batchs_valides,
            "ingredients_alertes": self.ingredient_repo.get_alertes(),
        }
