from __future__ import annotations

import hashlib
import re

from app.knowledge.sources import MarkdownNote, NoteChunk

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def split_into_chunks(notes: list[MarkdownNote], max_chars: int = 1200) -> list[NoteChunk]:
    chunks: list[NoteChunk] = []
    normalized_max = max(200, int(max_chars))

    for note in notes:
        lines = note.content.splitlines()
        sections: list[tuple[str, list[str]]] = []
        current_section = note.title
        current_lines: list[str] = []

        for line in lines:
            match = _HEADING_RE.match(line.strip())
            if match:
                if current_lines:
                    sections.append((current_section, current_lines))
                current_section = match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_section, current_lines))

        if not sections:
            sections = [(note.title, [note.content])]

        for section, section_lines in sections:
            content = "\n".join(section_lines).strip()
            if not content:
                continue

            if len(content) <= normalized_max:
                chunks.append(_build_chunk(note, section, content, 0))
                continue

            part_index = 0
            pos = 0
            while pos < len(content):
                end = pos + normalized_max
                if end < len(content):
                    ws = content.rfind(" ", pos, end)
                    if ws > pos:
                        end = ws
                piece = content[pos:end].strip()
                if piece:
                    chunks.append(_build_chunk(note, section, piece, part_index))
                    part_index += 1
                pos = end
                while pos < len(content) and content[pos] in " \n":
                    pos += 1

    return chunks


def _build_chunk(note: MarkdownNote, section: str, content: str, part_index: int) -> NoteChunk:
    base = f"{note.path}|{section}|{part_index}|{content}"
    chunk_id = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]
    return NoteChunk(
        chunk_id=chunk_id,
        path=note.path,
        title=note.title,
        section=section,
        content=content,
        metadata=dict(note.metadata),
    )
