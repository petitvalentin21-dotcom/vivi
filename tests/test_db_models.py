"""Unit tests — AppSettings CRUD with in-memory SQLite."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlmodel import Session, select

from app.db.connection import create_db_engine
from app.db.models import AppSettings


@pytest.fixture()
def db_session(tmp_path):
    """Temporary file-based DB with schema created via SQLModel metadata."""
    from sqlmodel import SQLModel

    engine = create_db_engine(str(tmp_path / "test.db"))
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_create_and_read(db_session: Session) -> None:
    entry = AppSettings(key="theme", value="dark")
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    assert entry.id is not None
    result = db_session.exec(select(AppSettings).where(AppSettings.key == "theme")).first()
    assert result is not None
    assert result.value == "dark"


def test_key_is_unique(db_session: Session) -> None:
    import sqlalchemy.exc

    db_session.add(AppSettings(key="unique_key", value="v1"))
    db_session.commit()

    db_session.add(AppSettings(key="unique_key", value="v2"))
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()


def test_update(db_session: Session) -> None:
    entry = AppSettings(key="lang", value="fr")
    db_session.add(entry)
    db_session.commit()

    entry.value = "en"
    entry.updated_at = datetime.now(timezone.utc)
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    assert entry.value == "en"


def test_delete(db_session: Session) -> None:
    entry = AppSettings(key="to_delete", value="bye")
    db_session.add(entry)
    db_session.commit()

    db_session.delete(entry)
    db_session.commit()

    result = db_session.exec(select(AppSettings).where(AppSettings.key == "to_delete")).first()
    assert result is None


def test_updated_at_defaults_to_now(db_session: Session) -> None:
    before = datetime.now(timezone.utc)
    entry = AppSettings(key="ts_test", value="x")
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    # updated_at stored without tz info (SQLite limitation) — compare naive
    after = datetime.now(timezone.utc)
    stored = entry.updated_at.replace(tzinfo=timezone.utc) if entry.updated_at.tzinfo is None else entry.updated_at
    assert before <= stored <= after
