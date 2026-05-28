from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class ListeCourses(SQLModel, table=True):
    __tablename__ = "listes_courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nom: str = Field(min_length=1, max_length=200)
    statut: str = Field(default="en_cours")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None


class ItemCourse(SQLModel, table=True):
    __tablename__ = "items_courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    liste_id: uuid.UUID = Field(foreign_key="listes_courses.id")
    nom: str = Field(min_length=1, max_length=200)
    quantite: Optional[float] = None
    unite: Optional[str] = None
    categorie: Optional[str] = None
    recette_id: Optional[uuid.UUID] = None
    achete: bool = Field(default=False)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
