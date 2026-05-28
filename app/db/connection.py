from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine


def create_db_engine(db_path: str, echo: bool = False) -> Engine:
    """
    Build a SQLAlchemy engine for the given SQLite file path.
    Creates the parent directory if missing.
    Enables WAL mode on every new connection for concurrent read safety.
    """
    db_abs = Path(db_path).resolve()
    db_abs.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{db_abs.as_posix()}"
    engine = create_engine(sqlite_url, echo=echo, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_wal_mode(dbapi_conn, _connection_record) -> None:  # pragma: no cover
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    return engine


def get_session(engine: Engine) -> Generator[Session, None, None]:
    """
    Yield a SQLModel Session for use as a FastAPI dependency (via closure).

    Usage in server.py:
        def _make_get_session(engine):
            def dep():
                yield from get_session(engine)
            return dep
    """
    with Session(engine) as session:
        yield session


def run_migrations(db_path: str) -> bool:
    """
    Run Alembic migrations (upgrade head) for the given database path.
    Returns True on success, False on failure — never raises (caller logs degraded state).
    Resolves alembic.ini relative to the project root (parent of app/).
    """
    try:
        from alembic import command
        from alembic.config import Config

        project_root = Path(__file__).resolve().parents[2]  # …/app/db/connection.py → root
        alembic_ini = project_root / "alembic.ini"

        if not alembic_ini.exists():
            print(f"[VIVI:DB] alembic.ini not found at {alembic_ini} — skipping migrations", file=sys.stderr)
            return False

        db_abs = Path(db_path).resolve()
        sqlite_url = f"sqlite:///{db_abs.as_posix()}"

        cfg = Config(str(alembic_ini))
        cfg.set_main_option("sqlalchemy.url", sqlite_url)
        cfg.set_main_option("script_location", str(project_root / "migrations"))

        command.upgrade(cfg, "head")
        print("[VIVI:DB] migrations applied", file=sys.stderr)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[VIVI:DB] migration failed — {exc}", file=sys.stderr)
        return False
