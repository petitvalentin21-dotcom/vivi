"""
Session Logger — captures user <-> Vivi exchanges in encrypted JSONL files.

TERMINOLOGY NOTE — two distinct "session" concepts coexist in this codebase:

    Logger session (this module)
        A contiguous window of activity bounded by 15 minutes of inactivity.
        Produces one encrypted .jsonl file + one .meta.json file.
        Identified by a timestamp string: YYYY-MM-DD_HH-MM-SS.
        One SessionStore session can span several logger sessions if the user
        pauses long enough between messages.

    SessionStore session (app/sessions/store.py)
        A UUID-keyed conversational thread used to feed message history to the
        LLM. Orthogonal to logger sessions — do not conflate the two.
"""
from __future__ import annotations

import base64
import json
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_SESSION_TIMEOUT_SECONDS = 15 * 60

# Gemma thinking tokens: <|channel|>thought ... </s> or similar LM Studio variants.
# Kept permissive so minor format changes don't break logging.
_REASONING_RE = re.compile(
    r"<\|channel\|>thought(.*?)(?:<channel\|>|</s>|$)", re.DOTALL | re.IGNORECASE
)

# Fixed salt — key secrecy comes entirely from VIVI_LOG_ENCRYPTION_KEY.
_KDF_SALT = b"vivi-session-logger-v1"


def _derive_key(raw_key: str) -> bytes:
    """Derive a Fernet-compatible key from an arbitrary string via PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_KDF_SALT,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(raw_key.encode("utf-8")))


def _now() -> datetime:
    """Thin wrapper around datetime.now so tests can patch it."""
    return datetime.now(timezone.utc)


class SessionLogger:
    """Appends one encrypted JSONL line per exchange, managing 15-min logger sessions."""

    def __init__(self, session_log_path: str, encryption_key: str) -> None:
        if not encryption_key or not encryption_key.strip():
            raise ValueError(
                "VIVI_LOG_ENCRYPTION_KEY is required but not set. "
                "Generate a key and add it to your .env file."
            )

        base = Path(session_log_path)
        self._raw_dir = base / "raw"
        self._processed_dir = base / "processed"
        self._current_session_file = base.parent / "current_session.json"
        self._error_log = base.parent / "logger_errors.log"
        self._fernet = Fernet(_derive_key(encryption_key))

        self._raw_dir.mkdir(parents=True, exist_ok=True)
        self._processed_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_exchange(self, user_msg: str, raw_response: str, model: str) -> None:
        """Log one exchange. Silently absorbs all errors to protect the chat flow."""
        try:
            self._log_exchange(user_msg, raw_response, model)
        except Exception:
            self._write_error(traceback.format_exc())

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _log_exchange(self, user_msg: str, raw_response: str, model: str) -> None:
        now = _now()
        reasoning, response = self._extract_reasoning(raw_response)
        current = self._load_current_session()

        if current is not None:
            last_exchange_at = datetime.fromisoformat(current["last_exchange_at"])
            elapsed = (now - last_exchange_at).total_seconds()

            if elapsed > _SESSION_TIMEOUT_SECONDS:
                # Lazy timeout detection: the transition is triggered by the next
                # incoming message, not by a timer.
                # TODO: implement a background worker that proactively closes sessions
                #       and transitions them to pending_triage without waiting for a
                #       new message. Useful for triage pipelines that poll on schedule.
                #       Not in scope for v1.
                self._close_session(current["session_id"], last_exchange_at)
                current = None

        if current is None:
            session_id = now.strftime("%Y-%m-%d_%H-%M-%S")
            self._open_session(session_id, now, model)
            current = {"session_id": session_id, "last_exchange_at": now.isoformat()}

        exchange = {
            "timestamp": now.isoformat(),
            "user": user_msg,
            "reasoning": reasoning,
            "response": response,
            "user_correction": None,
            "user_feedback": None,
        }

        self._append_exchange(current["session_id"], exchange)
        self._increment_meta(current["session_id"], now)
        current["last_exchange_at"] = now.isoformat()
        self._save_current_session(current)

    def _open_session(self, session_id: str, started_at: datetime, model: str) -> None:
        meta = {
            "session_id": session_id,
            "timestamp_start": started_at.isoformat(),
            "timestamp_end": started_at.isoformat(),
            "model": model,
            "domain": None,
            "tags": [],
            "session_feedback": None,
            "status": "active",
            "exchange_count": 0,
        }
        self._meta_path(session_id).write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )

    def _close_session(self, session_id: str, last_exchange_at: datetime) -> None:
        meta_path = self._meta_path(session_id)
        if not meta_path.exists():
            return
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["status"] = "pending_triage"
        meta["timestamp_end"] = last_exchange_at.isoformat()
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    def _append_exchange(self, session_id: str, exchange: dict) -> None:
        line = json.dumps(exchange, ensure_ascii=False)
        token = self._fernet.encrypt(line.encode("utf-8"))
        with self._jsonl_path(session_id).open("ab") as f:
            f.write(token + b"\n")

    def _increment_meta(self, session_id: str, now: datetime) -> None:
        meta_path = self._meta_path(session_id)
        if not meta_path.exists():
            return
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["exchange_count"] = meta.get("exchange_count", 0) + 1
        meta["timestamp_end"] = now.isoformat()
        meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # current_session.json helpers
    # ------------------------------------------------------------------

    def _load_current_session(self) -> Optional[dict]:
        if not self._current_session_file.exists():
            return None
        try:
            return json.loads(self._current_session_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _save_current_session(self, data: dict) -> None:
        self._current_session_file.write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    def _jsonl_path(self, session_id: str) -> Path:
        return self._raw_dir / f"session_{session_id}.jsonl"

    def _meta_path(self, session_id: str) -> Path:
        return self._raw_dir / f"session_{session_id}.meta.json"

    # ------------------------------------------------------------------
    # Reasoning extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_reasoning(content: str) -> tuple[Optional[str], str]:
        """Return (reasoning_or_None, cleaned_response).

        Extracts Gemma thinking tokens when present. Never raises.
        """
        try:
            match = _REASONING_RE.search(content)
            if not match:
                return None, content
            reasoning = match.group(1).strip() or None
            response = _REASONING_RE.sub("", content).strip()
            return reasoning, response
        except Exception:
            return None, content

    # ------------------------------------------------------------------
    # Error logging
    # ------------------------------------------------------------------

    def _write_error(self, tb: str) -> None:
        try:
            ts = _now().isoformat()
            with self._error_log.open("a", encoding="utf-8") as f:
                f.write(f"\n[{ts}]\n{tb}\n")
        except Exception:
            pass
