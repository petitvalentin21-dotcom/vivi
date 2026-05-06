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
