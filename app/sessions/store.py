from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class SessionStore:
    def __init__(self, store_path: str) -> None:
        self.store_path = Path(store_path)

    def ensure_store(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_payload({"sessions": {}})

    def create_session(self) -> str:
        payload = self._read_payload()
        session_id = uuid4().hex
        now = _now_iso()
        payload["sessions"][session_id] = {
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        self._write_payload(payload)
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        payload = self._read_payload()
        session = payload.get("sessions", {}).get(session_id)
        if not isinstance(session, dict):
            return None
        return session

    def append_messages(self, session_id: str, messages: list[dict[str, str]]) -> bool:
        payload = self._read_payload()
        sessions = payload.get("sessions", {})
        session = sessions.get(session_id)
        if not isinstance(session, dict):
            return False

        session_messages = session.setdefault("messages", [])
        if not isinstance(session_messages, list):
            session_messages = []
            session["messages"] = session_messages

        now = _now_iso()
        for item in messages:
            role = str(item.get("role", "")).strip()
            content = str(item.get("content", "")).strip()
            if not role or not content:
                continue
            session_messages.append({"role": role, "content": content, "created_at": now})

        session["updated_at"] = now
        self._write_payload(payload)
        return True

    def last_messages_for_prompt(self, session_id: str, limit: int = 4) -> list[dict[str, str]]:
        session = self.get_session(session_id)
        if not session:
            return []
        messages = session.get("messages", [])
        if not isinstance(messages, list):
            return []

        prompt_messages: list[dict[str, str]] = []
        for item in messages[-limit:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "")).strip().lower()
            content = str(item.get("content", "")).strip()
            if role in {"user", "assistant"} and content:
                prompt_messages.append({"role": role, "content": content})
        return prompt_messages

    def _read_payload(self) -> dict[str, Any]:
        self.ensure_store()
        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {"sessions": {}}
        if not isinstance(data, dict):
            data = {"sessions": {}}
        if not isinstance(data.get("sessions"), dict):
            data["sessions"] = {}
        return data

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
