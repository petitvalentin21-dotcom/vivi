from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StatutListe = Literal["en_cours", "terminée", "archivée"]


class ListeCoursesCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    statut: StatutListe = "en_cours"
    notes: Optional[str] = None


class ListeCoursesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nom: str
    statut: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ListeCoursesUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    statut: Optional[StatutListe] = None
    notes: Optional[str] = None


class ItemCourseBody(BaseModel):
    """Item sans liste_id — utilisé pour POST /listes/{id}/items et creer_liste_avec_items."""

    nom: str = Field(min_length=1, max_length=200)
    quantite: Optional[float] = None
    unite: Optional[str] = None
    categorie: Optional[str] = None
    recette_id: Optional[uuid.UUID] = None
    achete: bool = False
    notes: Optional[str] = None


class ItemCourseCreate(ItemCourseBody):
    liste_id: uuid.UUID


class ItemCourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    liste_id: uuid.UUID
    nom: str
    quantite: Optional[float]
    unite: Optional[str]
    categorie: Optional[str]
    recette_id: Optional[uuid.UUID]
    achete: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ItemCourseUpdate(BaseModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    quantite: Optional[float] = None
    unite: Optional[str] = None
    categorie: Optional[str] = None
    recette_id: Optional[uuid.UUID] = None
    achete: Optional[bool] = None
    notes: Optional[str] = None
