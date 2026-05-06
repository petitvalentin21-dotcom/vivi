from __future__ import annotations

import json
from pathlib import Path


class SessionStore:
    def __init__(self, store_path: str) -> None:
        self.store_path = Path(store_path)

    def ensure_store(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"sessions": {}}, ensure_ascii=False, indent=2), encoding="utf-8")
