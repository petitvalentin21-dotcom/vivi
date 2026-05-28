from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class AppSettings(SQLModel, table=True):
    """
    Key/value store for application-level settings.
    value is stored as a plain string; callers serialize/deserialize JSON if needed.
    """

    __tablename__ = "app_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
