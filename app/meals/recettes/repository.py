from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.meals.recettes.models import Recette
from app.meals.recettes.schemas import RecetteCreate, RecetteUpdate


class RecetteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: RecetteCreate) -> Recette:
        now = datetime.now(timezone.utc)
        recette = Recette(
            titre=data.titre,
            ingredients=[i.model_dump() for i in data.ingredients],
            etapes=list(data.etapes),
            portions=data.portions,
            temps_prep_min=data.temps_prep_min,
            temps_cuisson_min=data.temps_cuisson_min,
            conservation_jours=data.conservation_jours,
            tags=list(data.tags),
            notes_perso=data.notes_perso,
            statut_valeur_sure=data.statut_valeur_sure,
            created_at=now,
            updated_at=now,
        )
        self.session.add(recette)
        self.session.commit()
        self.session.refresh(recette)
        return recette

    def update(self, id: uuid.UUID, data: RecetteUpdate) -> Recette:
        recette = self.get(id)
        if recette is None:
            raise ValueError(f"Recette {id} not found")

        updates = data.model_dump(exclude_unset=True)

        # Pydantic serialises nested models to dicts; ingredients stays list[dict].
        for key, value in updates.items():
            setattr(recette, key, value)

        recette.updated_at = datetime.now(timezone.utc)
        self.session.add(recette)
        self.session.commit()
        self.session.refresh(recette)
        return recette

    def soft_delete(self, id: uuid.UUID) -> None:
        recette = self.get(id)
        if recette is None:
            raise ValueError(f"Recette {id} not found")
        now = datetime.now(timezone.utc)
        recette.deleted_at = now
        recette.updated_at = now
        self.session.add(recette)
        self.session.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: uuid.UUID, include_deleted: bool = False) -> Recette | None:
        stmt = select(Recette).where(Recette.id == id)
        if not include_deleted:
            stmt = stmt.where(Recette.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list(self, limit: int = 50, offset: int = 0, tag: str | None = None) -> list[Recette]:
        stmt = select(Recette).where(Recette.deleted_at.is_(None)).order_by(Recette.created_at.desc())
        all_rows = list(self.session.exec(stmt).all())
        if tag:
            # Client-side filter on JSON array — correct for SQLite, fine at personal-project scale.
            all_rows = [r for r in all_rows if tag in (r.tags or [])]
        return all_rows[offset : offset + limit]

    def search_by_tag(self, tag: str) -> list[Recette]:
        return self.list(limit=1000, offset=0, tag=tag)

    def count(self) -> int:
        result = self.session.exec(
            select(func.count(Recette.id)).where(Recette.deleted_at.is_(None))
        ).one()
        return int(result)
