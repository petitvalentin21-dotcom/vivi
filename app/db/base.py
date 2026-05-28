from __future__ import annotations

from sqlmodel import SQLModel

# Re-export SQLModel.metadata so Alembic env.py can import it without importing models directly.
# Import all models in this file to ensure they are registered on this metadata before Alembic reads it.
metadata = SQLModel.metadata
