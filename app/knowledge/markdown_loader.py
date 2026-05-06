from __future__ import annotations

from pathlib import Path


def count_markdown_notes(vault_path: str) -> tuple[bool, int, str | None]:
    path = Path(vault_path)
    if not path.exists() or not path.is_dir():
        return False, 0, f"Vault not found: {path}"

    count = 0
    for file_path in path.rglob("*.md"):
        if ".obsidian" in file_path.parts:
            continue
        count += 1
    return True, count, None
