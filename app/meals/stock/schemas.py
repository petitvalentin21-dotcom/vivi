from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StockageType = Literal["frigo", "congelateur", "temperature_ambiante"]


class BatchCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    recette_id: Optional[uuid.UUID] = None
    portions_total: int = Field(gt=0)
    portions_restantes: int = Field(ge=0)
    date_cuisson: date
    date_peremption: Optional[date] = None
    stockage: StockageType = "frigo"
    notes: Optional[str] = None


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recette_id: Optional[uuid.UUID]
    nom: str
    portions_total: int
    portions_restantes: int
    date_cuisson: date
    date_peremption: Optional[date]
    stockage: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class BatchUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    recette_id: Optional[uuid.UUID] = None
    portions_total: Optional[int] = Field(default=None, gt=0)
    portions_restantes: Optional[int] = Field(default=None, ge=0)
    date_cuisson: Optional[date] = None
    date_peremption: Optional[date] = None
    stockage: Optional[StockageType] = None
    notes: Optional[str] = None


class IngredientBaseCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    categorie: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    notes: Optional[str] = None


class IngredientBaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nom: str
    categorie: Optional[str]
    quantite: Optional[float]
    unite: Optional[str]
    seuil_alerte: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class IngredientBaseUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    categorie: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    notes: Optional[str] = None
