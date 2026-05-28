"""Integration test — GET /db/health with a real temporary DB."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def test_db_health_no_db_configured() -> None:
    """When db_path is empty, endpoint returns ok=false without crashing."""
    app = create_app(Settings())
    client = TestClient(app)

    response = client.get("/db/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["schema_version"] == "none"
    assert body["app_settings_count"] == 0


def test_db_health_with_migrated_db(tmp_path) -> None:
    """With a real DB + migrations, endpoint returns ok=true and schema_version."""
    db_path = str(tmp_path / "test_vivi.db")
    app = create_app(Settings(db_path=db_path))
    client = TestClient(app)

    response = client.get("/db/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["schema_version"] == "0001"
    assert body["app_settings_count"] == 0


def test_db_health_counts_existing_rows(tmp_path) -> None:
    """app_settings_count reflects actual rows in the table."""
    from sqlmodel import Session, SQLModel

    from app.db.connection import create_db_engine
    from app.db.models import AppSettings

    db_path = str(tmp_path / "count_test.db")

    # Create app — runs migrations
    app = create_app(Settings(db_path=db_path))

    # Insert two rows directly
    engine = create_db_engine(db_path)
    with Session(engine) as session:
        session.add(AppSettings(key="a", value="1"))
        session.add(AppSettings(key="b", value="2"))
        session.commit()
    engine.dispose()

    # New app instance using the same DB (no re-migration since schema is current)
    app2 = create_app(Settings(db_path=db_path))
    client = TestClient(app2)

    response = client.get("/db/health")
    assert response.status_code == 200
    assert response.json()["app_settings_count"] == 2
