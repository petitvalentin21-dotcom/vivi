from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Batch(SQLModel, table=True):
    __tablename__ = "batchs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    recette_id: Optional[uuid.UUID] = None
    nom: str = Field(min_length=1, max_length=200)
    portions_total: int
    portions_restantes: int
    date_cuisson: date
    date_peremption: Optional[date] = None
    stockage: str = Field(default="frigo")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None


class IngredientBase(SQLModel, table=True):
    __tablename__ = "ingredients_base"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nom: str = Field(min_length=1, max_length=200)
    categorie: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
