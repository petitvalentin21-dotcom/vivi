"""Tests Alembic — upgrade head + downgrade base sur BDD temporaire."""
from __future__ import annotations

import pytest

from app.db.connection import run_migrations


def test_run_migrations_upgrade_head(tmp_path) -> None:
    db_path = str(tmp_path / "alembic_test.db")
    ok = run_migrations(db_path)
    assert ok is True

    # Verify the table and alembic_version exist
    import sqlite3

    con = sqlite3.connect(db_path)
    tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "app_settings" in tables
    assert "alembic_version" in tables

    version = con.execute("SELECT version_num FROM alembic_version").fetchone()
    assert version is not None
    assert version[0] == "0002"  # current head — update when new migrations are added
    con.close()


def test_run_migrations_downgrade_base(tmp_path) -> None:
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    db_path = str(tmp_path / "alembic_down.db")
    ok = run_migrations(db_path)
    assert ok is True

    # Programmatic downgrade to base
    project_root = Path(__file__).resolve().parents[1]
    alembic_ini = project_root / "alembic.ini"
    db_abs = Path(db_path).resolve()

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_abs.as_posix()}")
    cfg.set_main_option("script_location", str(project_root / "migrations"))
    command.downgrade(cfg, "base")

    import sqlite3

    con = sqlite3.connect(db_path)
    tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "app_settings" not in tables
    con.close()


def test_run_migrations_idempotent(tmp_path) -> None:
    """Running upgrade head twice must not raise."""
    db_path = str(tmp_path / "idempotent.db")
    assert run_migrations(db_path) is True
    assert run_migrations(db_path) is True


def test_run_migrations_missing_ini(tmp_path, monkeypatch) -> None:
    """If alembic.ini is absent, run_migrations returns False without raising."""
    import app.db.connection as conn_module

    # Point __file__ somewhere with no alembic.ini
    fake_file = tmp_path / "app" / "db" / "connection.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.touch()
    monkeypatch.setattr(conn_module, "__file__", str(fake_file))

    db_path = str(tmp_path / "no_ini.db")
    result = run_migrations(db_path)
    assert result is False
