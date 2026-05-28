from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Recette(SQLModel, table=True):
    __tablename__ = "recettes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    titre: str = Field(min_length=1, max_length=200)

    # JSON — stored as nullable to satisfy SQLModel + SQLite Column(JSON) constraints.
    # Repository always writes non-None values; RecetteRead normalises None → [].
    ingredients: Optional[list[Any]] = Field(default=None, sa_column=Column(JSON))
    etapes: Optional[list[Any]] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[list[Any]] = Field(default=None, sa_column=Column(JSON))

    portions: int = Field(default=2)
    temps_prep_min: Optional[int] = None
    temps_cuisson_min: Optional[int] = None
    conservation_jours: Optional[int] = None
    notes_perso: Optional[str] = None
    statut_valeur_sure: bool = False
    nb_fois_cuisinee: int = 0
    derniere_fois_cuisinee: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
