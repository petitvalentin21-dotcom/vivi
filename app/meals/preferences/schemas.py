from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.meals.preferences.models import PreferenceValueType


class PreferenceCreate(BaseModel):
    cle: str = Field(min_length=1, max_length=200)
    valeur: str
    type_valeur: PreferenceValueType = "string"
    categorie: Optional[str] = None
    notes: Optional[str] = None


class PreferenceUpdate(BaseModel):
    valeur: Optional[str] = None
    type_valeur: Optional[PreferenceValueType] = None
    categorie: Optional[str] = None
    notes: Optional[str] = None


class PreferenceUpsert(BaseModel):
    """Corps de PUT /{cle} — la clé est dans l'URL, pas dans le body."""

    valeur: str
    type_valeur: PreferenceValueType = "string"
    categorie: Optional[str] = None
    notes: Optional[str] = None


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cle: str
    valeur: str
    type_valeur: str
    categorie: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class PreferenceListResponse(BaseModel):
    items: list[PreferenceRead]
    count: int


class PreferenceResumeResponse(BaseModel):
    preferences: dict[str, Any]
    count: int
