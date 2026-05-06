from __future__ import annotations


def split_into_chunks(text: str, chunk_size: int = 800) -> list[str]:
    value = str(text or "").strip()
    if not value:
        return []
    normalized_size = max(1, int(chunk_size))
    return [value[i : i + normalized_size] for i in range(0, len(value), normalized_size)]
