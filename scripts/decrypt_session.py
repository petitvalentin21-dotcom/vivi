#!/usr/bin/env python3
"""
Decrypt a Vivi session JSONL file for manual inspection.

Usage:
    python scripts/decrypt_session.py data/sessions/raw/session_2026-05-21_14-30-12.jsonl

Reads VIVI_LOG_ENCRYPTION_KEY from .env or the environment.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.sessions.logger import _derive_key  # noqa: E402


def _load_key() -> str:
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("VIVI_LOG_ENCRYPTION_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return os.environ.get("VIVI_LOG_ENCRYPTION_KEY", "")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/decrypt_session.py <path_to_session.jsonl>", file=sys.stderr)
        sys.exit(1)

    session_file = Path(sys.argv[1])
    if not session_file.exists():
        print(f"File not found: {session_file}", file=sys.stderr)
        sys.exit(1)

    raw_key = _load_key()
    if not raw_key:
        print("Error: VIVI_LOG_ENCRYPTION_KEY not found in .env or environment.", file=sys.stderr)
        sys.exit(1)

    fernet = Fernet(_derive_key(raw_key))
    lines = [l for l in session_file.read_bytes().splitlines() if l.strip()]

    if not lines:
        print("(empty file)")
        return

    print(f"Session file : {session_file}")
    print(f"Exchanges    : {len(lines)}")
    print()

    for i, raw_line in enumerate(lines, start=1):
        try:
            decrypted = fernet.decrypt(raw_line).decode("utf-8")
            ex = json.loads(decrypted)
        except InvalidToken:
            print(f"[Exchange {i}] ERROR: wrong key or corrupted data.", file=sys.stderr)
            continue
        except Exception as exc:
            print(f"[Exchange {i}] ERROR: {exc}", file=sys.stderr)
            continue

        print(f"{'='*60}")
        print(f"Exchange {i} — {ex.get('timestamp', '?')}")
        print(f"User      : {ex.get('user', '')}")
        if ex.get("reasoning"):
            reasoning = ex["reasoning"]
            preview = reasoning[:300] + "..." if len(reasoning) > 300 else reasoning
            print(f"Reasoning : {preview}")
        print(f"Response  : {ex.get('response', '')}")
        if ex.get("user_correction"):
            print(f"Correction: {ex['user_correction']}")
        if ex.get("user_feedback"):
            print(f"Feedback  : {ex['user_feedback']}")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
