from __future__ import annotations

from dataclasses import replace
import re

from app.knowledge.sources import NoteChunk, Source

_WORD_RE = re.compile(r"[a-z0-9_]+")
DEFAULT_MAX_CHUNKS_PER_PATH = 2
LOW_CONFIDENCE_MIN_SCORE = 3.0
LOW_CONFIDENCE_RATIO = 0.35
_PRIORITY_RANK: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
_PRIORITY_BOOST: dict[str, float] = {"high": 1.0, "medium": 0.0, "low": -0.5}


def _priority_rank(metadata: dict) -> int:
    return _PRIORITY_RANK.get(str(metadata.get("llm_priority", "")).lower(), 1)


def _priority_boost(metadata: dict) -> float:
    return _PRIORITY_BOOST.get(str(metadata.get("llm_priority", "")).lower(), 0.0)


def retrieve_lexical(
    query: str,
    chunks: list[NoteChunk],
    top_k: int,
    max_chunks_per_path: int = DEFAULT_MAX_CHUNKS_PER_PATH,
) -> list[Source]:
    q = str(query or "").strip().lower()
    if not q:
        return []

    tokens = _tokenize(q)
    if not tokens:
        return []

    scored: list[tuple[float, int, Source]] = []
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
        scored.append((score, _priority_rank(chunk.metadata), source))

    scored.sort(key=lambda item: (-item[0], item[1], item[2].path, item[2].section, item[2].source_id))
    limit = max(1, int(top_k))
    selected = _select_diverse_sources(scored, limit, max_chunks_per_path)
    max_score = scored[0][0] if scored else 0.0
    return [_with_confidence(source, max_score) for source in selected]


def _select_diverse_sources(
    scored: list[tuple[float, int, Source]],
    limit: int,
    max_chunks_per_path: int,
) -> list[Source]:
    if not scored:
        return []

    normalized_limit = max(1, int(limit))
    per_path_limit = max(1, int(max_chunks_per_path))
    selected: list[Source] = []
    selected_ids: set[str] = set()
    counts_by_path: dict[str, int] = {}

    for _, __, source in scored:
        if len(selected) >= normalized_limit:
            return selected
        if counts_by_path.get(source.path, 0) >= per_path_limit:
            continue
        selected.append(source)
        selected_ids.add(source.source_id)
        counts_by_path[source.path] = counts_by_path.get(source.path, 0) + 1

    for _, __, source in scored:
        if len(selected) >= normalized_limit:
            return selected
        if source.source_id in selected_ids:
            continue
        selected.append(source)
        selected_ids.add(source.source_id)

    return selected


def _with_confidence(source: Source, max_score: float) -> Source:
    low = _is_low_confidence(source.score, max_score)
    return replace(
        source,
        confidence_label="low" if low else "normal",
        is_low_confidence=low,
    )


def _is_low_confidence(score: float, max_score: float) -> bool:
    if score <= 0:
        return True
    if score < LOW_CONFIDENCE_MIN_SCORE:
        return True
    if max_score <= 0:
        return False
    return score < (max_score * LOW_CONFIDENCE_RATIO)


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

    score += _priority_boost(chunk.metadata)
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
