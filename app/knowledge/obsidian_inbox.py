from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Iterable

ALLOWED_INBOX_NOTE_TYPES = {
    "generated_note",
    "conversation_summary",
    "decision_proposal",
    "documentation_draft",
    "backlog_proposal",
    "rag_summary",
    "clarification_note",
}
ALLOWED_INBOX_STATUSES = {"draft", "to_review"}

_FORBIDDEN_WINDOWS_CHARS_RE = re.compile(r'[<>:"/\\|?*]')
_SLUG_SEPARATOR_RE = re.compile(r"[\s_ -]+")
_SLUG_ALLOWED_RE = re.compile(r"[^a-z0-9-]")
_SENSITIVE_RE = re.compile(
    r"(?i)(sk-[a-z0-9_-]{8,}|(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*\S+)"
)
_PROTECTED_VAULT_PARTS = {
    ".obsidian",
    "00_product",
    "01_user_docs",
    "02_architecture",
    "03_decisions",
    "04_backlog",
    "05_runs",
    "90_generated",
    "91_runtime",
    "99_archive",
}


class ObsidianInboxError(ValueError):
    """Raised when an inbox note request violates the controlled-write rules."""


@dataclass(frozen=True)
class InboxNoteResult:
    relative_path: str
    absolute_path: str
    filename: str
    frontmatter: dict[str, object]


def create_inbox_note(
    vault_path: str | Path,
    title: str,
    body: str,
    note_type: str = "generated_note",
    status: str = "draft",
    source: str = "vivi",
    related: Iterable[str] | None = None,
    source_paths: Iterable[str] | None = None,
    prompt_summary: str | None = None,
    confidence: str | None = None,
) -> InboxNoteResult:
    """Create a reviewed-by-default Markdown proposal in knowledge_vault/92_inbox."""

    vault = Path(vault_path).expanduser().resolve()
    inbox = (vault / "92_inbox").resolve()
    if not vault.exists() or not vault.is_dir():
        raise ObsidianInboxError("vault_path must be an existing directory")
    if not inbox.exists() or not inbox.is_dir():
        raise ObsidianInboxError("92_inbox must exist before creating an inbox note")
    _ensure_inside_vault(vault, inbox)

    clean_title = _clean_text_field(title, "title")
    clean_body = _clean_text_field(body, "body")
    clean_note_type = _validate_choice(note_type, ALLOWED_INBOX_NOTE_TYPES, "note_type")
    clean_status = _validate_choice(status, ALLOWED_INBOX_STATUSES, "status")
    clean_source = _clean_scalar(source, "source")
    if clean_source != "vivi":
        raise ObsidianInboxError("source must be vivi for inbox notes")

    slug = _slugify_title(clean_title)
    today = date.today().isoformat()
    filename = _next_available_filename(inbox, f"{today}_inbox_{slug}.md")
    target = (inbox / filename).resolve()
    _ensure_inbox_target(inbox, target)

    frontmatter: dict[str, object] = {
        "type": clean_note_type,
        "status": clean_status,
        "source": clean_source,
        "created_at": today,
        "index": False,
        "review_required": True,
    }

    clean_related = _clean_optional_list(related, "related")
    if clean_related:
        frontmatter["related"] = clean_related

    clean_prompt_summary = _clean_optional_scalar(prompt_summary, "prompt_summary")
    if clean_prompt_summary:
        frontmatter["prompt_summary"] = clean_prompt_summary

    clean_confidence = _clean_optional_scalar(confidence, "confidence")
    if clean_confidence:
        frontmatter["confidence"] = clean_confidence

    clean_source_paths = _clean_source_paths(source_paths)
    if clean_source_paths:
        frontmatter["source_paths"] = clean_source_paths

    markdown = _render_note(frontmatter, clean_title, clean_body, clean_source_paths)

    target.write_text(markdown, encoding="utf-8")

    return InboxNoteResult(
        relative_path=target.relative_to(vault).as_posix(),
        absolute_path=str(target),
        filename=filename,
        frontmatter=frontmatter,
    )


def _ensure_inside_vault(vault: Path, path: Path) -> None:
    try:
        path.relative_to(vault)
    except ValueError as exc:
        raise ObsidianInboxError("inbox path must stay inside the vault") from exc


def _ensure_inbox_target(inbox: Path, target: Path) -> None:
    try:
        rel = target.relative_to(inbox)
    except ValueError as exc:
        raise ObsidianInboxError("inbox note target must stay inside 92_inbox") from exc

    if len(rel.parts) != 1 or rel.suffix.lower() != ".md":
        raise ObsidianInboxError("inbox note target must be a single Markdown file")
    if set(target.parts).intersection(_PROTECTED_VAULT_PARTS - {"92_inbox"}):
        raise ObsidianInboxError("inbox note target cannot use protected vault folders")


def _validate_choice(value: str, allowed: set[str], field_name: str) -> str:
    clean = _clean_scalar(value, field_name)
    if clean not in allowed:
        raise ObsidianInboxError(f"{field_name} is not allowed: {clean}")
    return clean


def _clean_text_field(value: str, field_name: str) -> str:
    clean = _clean_scalar(value, field_name)
    if _SENSITIVE_RE.search(clean):
        raise ObsidianInboxError(f"{field_name} appears to contain sensitive content")
    return clean


def _clean_scalar(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ObsidianInboxError(f"{field_name} must be a string")
    clean = value.strip()
    if not clean:
        raise ObsidianInboxError(f"{field_name} cannot be empty")
    return clean


def _clean_optional_scalar(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _clean_text_field(value, field_name)


def _clean_optional_list(values: Iterable[str] | None, field_name: str) -> list[str]:
    if values is None:
        return []
    return [_clean_text_field(str(value), field_name) for value in values if str(value).strip()]


def _clean_source_paths(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []

    clean_paths: list[str] = []
    for raw in values:
        value = _clean_text_field(str(raw), "source_paths").replace("\\", "/")
        candidate = PurePosixPath(value)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ObsidianInboxError("source_paths cannot be absolute or use traversal")
        if candidate.parts and candidate.parts[0] in {".obsidian", "92_inbox"}:
            raise ObsidianInboxError("source_paths cannot point to protected Obsidian internals or inbox drafts")
        clean_paths.append(value)
    return clean_paths


def _slugify_title(title: str) -> str:
    lowered = unicodedata.normalize("NFKD", title.lower()).encode("ascii", "ignore").decode("ascii")
    without_forbidden = _FORBIDDEN_WINDOWS_CHARS_RE.sub(" ", lowered)
    separated = _SLUG_SEPARATOR_RE.sub("-", without_forbidden)
    slug = _SLUG_ALLOWED_RE.sub("", separated).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)[:80].strip("-")
    if not slug:
        raise ObsidianInboxError("title does not contain enough safe characters for a filename")
    return slug


def _next_available_filename(inbox: Path, preferred: str) -> str:
    stem = Path(preferred).stem
    suffix = Path(preferred).suffix
    candidate = preferred
    index = 1
    while (inbox / candidate).exists():
        candidate = f"{stem}_{index:03d}{suffix}"
        index += 1
    return candidate


def _render_note(
    frontmatter: dict[str, object],
    title: str,
    body: str,
    source_paths: list[str],
) -> str:
    lines = ["---", *_render_frontmatter_lines(frontmatter), "---", "", f"# {title}", ""]
    lines.extend(
        [
            "> Proposition générée par VIVI. À relire avant toute intégration dans les notes sources.",
            "",
            body.rstrip(),
            "",
        ]
    )

    if source_paths:
        lines.extend(["## Sources liées", ""])
        lines.extend(f"- {path}" for path in source_paths)
        lines.append("")

    return "\n".join(lines)


def _render_frontmatter_lines(frontmatter: dict[str, object]) -> list[str]:
    lines: list[str] = []
    for key, value in frontmatter.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
            lines.append(f"{key}: {rendered}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {_escape_frontmatter_scalar(item)}" for item in value)
        else:
            lines.append(f"{key}: {_escape_frontmatter_scalar(value)}")
    return lines


def _escape_frontmatter_scalar(value: object) -> str:
    text = str(value)
    if not text or text[0] in {"[", "{", "&", "*", "!", "|", ">", "@", "`"} or ": " in text:
        return '"' + text.replace('"', '\\"') + '"'
    return text
