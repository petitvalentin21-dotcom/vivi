from __future__ import annotations

import re

from app.knowledge.sources import NoteChunk, Source

_WORD_RE = re.compile(r"[a-z0-9_]+")


def retrieve_lexical(query: str, chunks: list[NoteChunk], top_k: int) -> list[Source]:
    q = str(query or "").strip().lower()
    if not q:
        return []

    tokens = _tokenize(q)
    if not tokens:
        return []

    scored: list[tuple[float, Source]] = []
    for chunk in chunks:
        score = _score_chunk(q, tokens, chunk)
        if score <= 0:
            continue
        excerpt = _build_excerpt(chunk.content, tokens)
        source = Source(
            source_id=chunk.chunk_id,
            path=chunk.path,
            title=chunk.title,
            section=chunk.section,
            score=round(score, 4),
            excerpt=excerpt,
            chunk_text=chunk.content,
        )
        scored.append((score, source))

    scored.sort(key=lambda item: (-item[0], item[1].path, item[1].section, item[1].source_id))
    limit = max(1, int(top_k))
    return [item[1] for item in scored[:limit]]


def _score_chunk(query: str, tokens: list[str], chunk: NoteChunk) -> float:
    title = chunk.title.lower()
    path = chunk.path.lower()
    section = chunk.section.lower()
    content = chunk.content.lower()
    tags = " ".join([str(x).lower() for x in chunk.metadata.get("tags", [])])

    score = 0.0
    if query in content:
        score += 8.0
    if query in title:
        score += 10.0
    if query in path:
        score += 9.0
    if query in tags:
        score += 9.0
    if query in section:
        score += 5.0

    for token in tokens:
        if token in title:
            score += 4.0
        if token in path:
            score += 3.0
        if token in tags:
            score += 4.0
        if token in section:
            score += 2.0
        token_count = content.count(token)
        if token_count:
            score += min(3.0, token_count * 0.5)

    return score


def _build_excerpt(content: str, tokens: list[str], max_len: int = 180) -> str:
    cleaned = " ".join((content or "").split())
    if not cleaned:
        return ""

    lc = cleaned.lower()
    idx = -1
    for token in tokens:
        idx = lc.find(token)
        if idx >= 0:
            break

    if idx < 0:
        return cleaned[:max_len]

    start = max(0, idx - 40)
    end = min(len(cleaned), start + max_len)
    excerpt = cleaned[start:end]
    return excerpt.strip()


def _tokenize(value: str) -> list[str]:
    return [m.group(0) for m in _WORD_RE.finditer(value.lower())]
