from __future__ import annotations

import uuid

from app.meals.recettes.models import Recette
from app.meals.recettes.repository import RecetteRepository
from app.meals.recettes.schemas import RecetteCreate, RecetteUpdate


class RecetteService:
    """
    Thin service layer for FEAT-18.
    Business logic (valeur sûre automation, batch proposals, …) is FEAT-19+.
    """

    def __init__(self, repo: RecetteRepository) -> None:
        self.repo = repo

    def create(self, data: RecetteCreate) -> Recette:
        return self.repo.create(data)

    def get(self, id: uuid.UUID) -> Recette | None:
        return self.repo.get(id)

    def list(self, limit: int = 50, offset: int = 0, tag: str | None = None) -> list[Recette]:
        return self.repo.list(limit=limit, offset=offset, tag=tag)

    def update(self, id: uuid.UUID, data: RecetteUpdate) -> Recette:
        return self.repo.update(id, data)

    def soft_delete(self, id: uuid.UUID) -> None:
        self.repo.soft_delete(id)

    def search_by_tag(self, tag: str) -> list[Recette]:
        return self.repo.search_by_tag(tag)

    def count(self) -> int:
        return self.repo.count()
