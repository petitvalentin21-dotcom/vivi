"""Tests for app/sessions/logger.py — all 9 acceptance criteria."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from app.sessions.logger import SessionLogger, _derive_key, _now

TEST_KEY = "vivi-test-encryption-key-do-not-use-in-prod"
MODEL = "gemma-test"


@pytest.fixture()
def log_dir(tmp_path: Path) -> str:
    return str(tmp_path / "sessions")


@pytest.fixture()
def logger(log_dir: str) -> SessionLogger:
    return SessionLogger(log_dir, TEST_KEY)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _decrypt_lines(raw_dir: Path, session_id: str, key: str) -> list[dict]:
    from cryptography.fernet import Fernet
    fernet = Fernet(_derive_key(key))
    jsonl = raw_dir / f"session_{session_id}.jsonl"
    result = []
    for line in jsonl.read_bytes().splitlines():
        if line.strip():
            result.append(json.loads(fernet.decrypt(line)))
    return result


def _read_meta(raw_dir: Path, session_id: str) -> dict:
    return json.loads((raw_dir / f"session_{session_id}.meta.json").read_text())


def _current(log_dir: str) -> dict:
    return json.loads((Path(log_dir).parent / "current_session.json").read_text())


# ---------------------------------------------------------------------------
# Criterion 1 — N exchanges produce a valid JSONL and coherent meta.json
# ---------------------------------------------------------------------------

def test_n_exchanges_produce_valid_jsonl_and_meta(logger: SessionLogger, log_dir: str) -> None:
    logger.log_exchange("hello", "hi there", MODEL)
    logger.log_exchange("how are you?", "I am fine", MODEL)
    logger.log_exchange("bye", "goodbye", MODEL)

    current = _current(log_dir)
    sid = current["session_id"]
    raw_dir = Path(log_dir) / "raw"

    exchanges = _decrypt_lines(raw_dir, sid, TEST_KEY)
    assert len(exchanges) == 3

    for ex in exchanges:
        assert set(ex.keys()) == {"timestamp", "user", "reasoning", "response", "user_correction", "user_feedback"}
        assert ex["user_correction"] is None
        assert ex["user_feedback"] is None

    assert exchanges[0]["user"] == "hello"
    assert exchanges[0]["response"] == "hi there"

    meta = _read_meta(raw_dir, sid)
    assert meta["status"] == "active"
    assert meta["exchange_count"] == 3
    assert meta["model"] == MODEL


# ---------------------------------------------------------------------------
# Criterion 2 — JSONL is encrypted (unreadable without key), decryptable with key
# ---------------------------------------------------------------------------

def test_jsonl_is_encrypted_and_decryptable(logger: SessionLogger, log_dir: str) -> None:
    logger.log_exchange("secret message", "secret response", MODEL)

    sid = _current(log_dir)["session_id"]
    raw_dir = Path(log_dir) / "raw"
    raw_bytes = (raw_dir / f"session_{sid}.jsonl").read_bytes()

    # Raw content must not contain the plaintext
    assert b"secret message" not in raw_bytes
    assert b"secret response" not in raw_bytes

    # Decryptable with the correct key
    exchanges = _decrypt_lines(raw_dir, sid, TEST_KEY)
    assert exchanges[0]["user"] == "secret message"
    assert exchanges[0]["response"] == "secret response"


# ---------------------------------------------------------------------------
# Criterion 3 & 4 — After 15 min inactivity, next message creates a new session
#                   and old session transitions to pending_triage
# ---------------------------------------------------------------------------

def test_timeout_creates_new_session_and_closes_old(logger: SessionLogger, log_dir: str) -> None:
    t0 = datetime(2026, 5, 21, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=16)

    raw_dir = Path(log_dir) / "raw"

    with patch("app.sessions.logger._now", return_value=t0):
        logger.log_exchange("first message", "first response", MODEL)

    first_sid = _current(log_dir)["session_id"]

    with patch("app.sessions.logger._now", return_value=t1):
        logger.log_exchange("after timeout", "new session response", MODEL)

    second_sid = _current(log_dir)["session_id"]

    assert first_sid != second_sid, "A new session file must be created after timeout"

    first_meta = _read_meta(raw_dir, first_sid)
    assert first_meta["status"] == "pending_triage"

    second_meta = _read_meta(raw_dir, second_sid)
    assert second_meta["status"] == "active"
    assert second_meta["exchange_count"] == 1


def test_no_new_session_within_timeout(logger: SessionLogger, log_dir: str) -> None:
    t0 = datetime(2026, 5, 21, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=14)

    with patch("app.sessions.logger._now", return_value=t0):
        logger.log_exchange("msg1", "resp1", MODEL)
    first_sid = _current(log_dir)["session_id"]

    with patch("app.sessions.logger._now", return_value=t1):
        logger.log_exchange("msg2", "resp2", MODEL)
    second_sid = _current(log_dir)["session_id"]

    assert first_sid == second_sid


# ---------------------------------------------------------------------------
# Criterion 5 — Reasoning captured when available, null otherwise
# ---------------------------------------------------------------------------

def test_reasoning_extracted_when_present(logger: SessionLogger, log_dir: str) -> None:
    raw = "<|channel|>thought\nI should think about this carefully.\n<channel|>The answer is 42."
    logger.log_exchange("what is the answer?", raw, MODEL)

    sid = _current(log_dir)["session_id"]
    ex = _decrypt_lines(Path(log_dir) / "raw", sid, TEST_KEY)[0]

    assert ex["reasoning"] == "I should think about this carefully."
    assert "42" in ex["response"]
    assert "<|channel|>" not in ex["response"]


def test_reasoning_is_null_when_absent(logger: SessionLogger, log_dir: str) -> None:
    logger.log_exchange("hello", "plain response without thinking", MODEL)

    sid = _current(log_dir)["session_id"]
    ex = _decrypt_lines(Path(log_dir) / "raw", sid, TEST_KEY)[0]

    assert ex["reasoning"] is None
    assert ex["response"] == "plain response without thinking"


# ---------------------------------------------------------------------------
# Criterion 6 & 7 — Logger error does not interrupt response; error is traced
# ---------------------------------------------------------------------------

def test_logger_error_does_not_propagate(logger: SessionLogger) -> None:
    with patch.object(logger, "_log_exchange", side_effect=OSError("disk full")):
        # Must not raise
        logger.log_exchange("msg", "resp", MODEL)


def test_logger_error_written_to_error_log(logger: SessionLogger, log_dir: str) -> None:
    error_log = Path(log_dir).parent / "logger_errors.log"

    with patch.object(logger, "_log_exchange", side_effect=RuntimeError("boom")):
        logger.log_exchange("msg", "resp", MODEL)

    assert error_log.exists()
    content = error_log.read_text()
    assert "RuntimeError" in content
    assert "boom" in content


# ---------------------------------------------------------------------------
# Criterion 8 — Backend refuses to start without VIVI_LOG_ENCRYPTION_KEY
# ---------------------------------------------------------------------------

def test_logger_raises_on_missing_key() -> None:
    with pytest.raises(ValueError, match="VIVI_LOG_ENCRYPTION_KEY"):
        SessionLogger("/tmp/vivi-test-sessions", "")


def test_create_app_exits_on_missing_key(tmp_path: Path) -> None:
    from app.api.server import create_app
    from app.config import Settings

    cfg = Settings(
        session_log_path=str(tmp_path / "sessions"),
        log_encryption_key="",
    )
    with pytest.raises(SystemExit) as exc_info:
        create_app(cfg)
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# Criterion 9 — current_session.json survives backend restart (session continues)
# ---------------------------------------------------------------------------

def test_current_session_survives_restart(log_dir: str) -> None:
    logger1 = SessionLogger(log_dir, TEST_KEY)
    logger1.log_exchange("before restart", "response before", MODEL)
    sid_before = _current(log_dir)["session_id"]

    # Simulate restart: new SessionLogger instance, same log_dir and key
    logger2 = SessionLogger(log_dir, TEST_KEY)
    logger2.log_exchange("after restart", "response after", MODEL)
    sid_after = _current(log_dir)["session_id"]

    assert sid_before == sid_after, "Session must continue after restart within timeout"

    raw_dir = Path(log_dir) / "raw"
    exchanges = _decrypt_lines(raw_dir, sid_before, TEST_KEY)
    assert len(exchanges) == 2
