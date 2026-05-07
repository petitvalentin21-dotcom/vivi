from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    source_id: str
    path: str
    title: str
    section: str
    score: float
    excerpt: str
    chunk_text: str
    confidence_label: str = "unknown"
    is_low_confidence: bool = False


@dataclass(frozen=True)
class MarkdownNote:
    path: str
    title: str
    content: str
    headings: list[str]
    tags: list[str]
    metadata: dict
    modified_at: str | None = None


@dataclass(frozen=True)
class NoteChunk:
    chunk_id: str
    path: str
    title: str
    section: str
    content: str
    metadata: dict
