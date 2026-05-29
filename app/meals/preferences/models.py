from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from sqlmodel import Field, SQLModel

PreferenceValueType = Literal["string", "int", "float", "bool", "list", "dict"]


class Preference(SQLModel, table=True):
    __tablename__ = "preferences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cle: str = Field(index=True, unique=True)
    valeur: str
    type_valeur: str = Field(default="string")
    categorie: Optional[str] = Field(default=None, index=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
