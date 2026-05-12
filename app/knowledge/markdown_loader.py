from __future__ import annotations

import re
from pathlib import Path

from app.knowledge.sources import MarkdownNote

_INCLUDED_PREFIXES = {"00_product", "01_user_docs", "02_architecture", "03_decisions", "04_backlog", "05_runs"}
_EXCLUDED_PARTS = {".obsidian", "90_generated", "91_runtime", "92_inbox", "99_archive", "tmp", "data"}
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def load_markdown_notes(vault_path: str) -> tuple[bool, list[MarkdownNote], str | None]:
    vault = Path(vault_path)
    if not vault.exists() or not vault.is_dir():
        return False, [], f"Vault not found: {vault}"

    notes: list[MarkdownNote] = []
    for file_path in sorted(vault.rglob("*.md")):
        rel = file_path.relative_to(vault)
        rel_parts = set(rel.parts)
        if len(rel.parts) > 1 and rel.parts[0] not in _INCLUDED_PREFIXES:
            continue
        if rel_parts.intersection(_EXCLUDED_PARTS):
            continue

        raw = file_path.read_text(encoding="utf-8")
        metadata, content = _parse_frontmatter(raw)
        if _metadata_index_false(metadata):
            continue

        title = _extract_title(metadata, content, file_path)
        tags = _extract_tags(metadata)
        headings = [m.group(1).strip() for m in _HEADING_RE.finditer(content)]
        modified_at = None
        try:
            modified_at = file_path.stat().st_mtime_ns
            modified_at = str(modified_at)
        except OSError:
            modified_at = None

        notes.append(
            MarkdownNote(
                path=rel.as_posix(),
                title=title,
                content=content.strip(),
                headings=headings,
                tags=tags,
                metadata=metadata,
                modified_at=modified_at,
            )
        )

    return True, notes, None


def count_markdown_notes(vault_path: str) -> tuple[bool, int, str | None]:
    exists, notes, error = load_markdown_notes(vault_path)
    return exists, len(notes), error


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    text = raw or ""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    block = text[4:end]
    content = text[end + 5 :]
    metadata: dict[str, object] = {}
    last_key = ""

    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") and last_key:
            current = metadata.get(last_key)
            if not isinstance(current, list):
                current = []
            current.append(stripped[2:].strip().strip("\"'"))
            metadata[last_key] = current
            continue
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        k = key.strip().lower()
        v = value.strip()
        last_key = k
        metadata[k] = _parse_scalar(v)

    return metadata, content


def _parse_scalar(value: str):
    v = value.strip()
    if not v:
        return ""
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
    return v.strip("\"'")


def _metadata_index_false(metadata: dict) -> bool:
    for key in ("index", "llm_index"):
        value = metadata.get(key)
        if isinstance(value, bool):
            if value is False:
                return True
        if isinstance(value, str):
            if value.strip().lower() == "false":
                return True
    return False


def _extract_title(metadata: dict, content: str, file_path: Path) -> str:
    front_title = str(metadata.get("title", "")).strip()
    if front_title:
        return front_title

    match = _H1_RE.search(content or "")
    if match:
        return match.group(1).strip()

    return file_path.stem


def _extract_tags(metadata: dict) -> list[str]:
    raw = metadata.get("tags")
    if raw is None:
        return []
    if isinstance(raw, str):
        candidate = raw.strip()
        if not candidate:
            return []
        if "," in candidate:
            return [x.strip() for x in candidate.split(",") if x.strip()]
        return [candidate]
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return []


