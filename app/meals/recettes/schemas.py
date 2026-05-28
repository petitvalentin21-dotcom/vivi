from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IngredientSchema(BaseModel):
    nom: str
    quantite: Optional[float] = None
    unite: Optional[str] = None


class RecetteCreate(BaseModel):
    titre: str = Field(min_length=1, max_length=200)
    ingredients: list[IngredientSchema] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list)
    portions: int = 2
    temps_prep_min: Optional[int] = None
    temps_cuisson_min: Optional[int] = None
    conservation_jours: Optional[int] = None
    tags: list[str] = Field(default_factory=list)
    notes_perso: Optional[str] = None
    statut_valeur_sure: bool = False


class RecetteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    titre: str
    ingredients: list[IngredientSchema] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list)
    portions: int
    temps_prep_min: Optional[int]
    temps_cuisson_min: Optional[int]
    conservation_jours: Optional[int]
    tags: list[str] = Field(default_factory=list)
    notes_perso: Optional[str]
    statut_valeur_sure: bool
    nb_fois_cuisinee: int
    derniere_fois_cuisinee: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @field_validator("ingredients", mode="before")
    @classmethod
    def _normalize_ingredients(cls, v: Any) -> list:
        return v if v is not None else []

    @field_validator("etapes", "tags", mode="before")
    @classmethod
    def _normalize_list(cls, v: Any) -> list:
        return v if v is not None else []


class RecetteUpdate(BaseModel):
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    ingredients: Optional[list[IngredientSchema]] = None
    etapes: Optional[list[str]] = None
    portions: Optional[int] = None
    temps_prep_min: Optional[int] = None
    temps_cuisson_min: Optional[int] = None
    conservation_jours: Optional[int] = None
    tags: Optional[list[str]] = None
    notes_perso: Optional[str] = None
    statut_valeur_sure: Optional[bool] = None
    nb_fois_cuisinee: Optional[int] = None
    derniere_fois_cuisinee: Optional[datetime] = None
