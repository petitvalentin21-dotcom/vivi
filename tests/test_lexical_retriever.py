from app.knowledge.chunker import split_into_chunks
from app.knowledge.lexical_retriever import retrieve_lexical
from app.knowledge.sources import MarkdownNote


def _notes() -> list[MarkdownNote]:
    return [
        MarkdownNote(
            path="00_product/alpha.md",
            title="Alpha System",
            content="# Intro\nThe lexical engine helps source search.\n## API\nSearch endpoint details.",
            headings=["Intro", "API"],
            tags=["rag", "api"],
            metadata={"tags": ["rag", "api"]},
        ),
        MarkdownNote(
            path="02_architecture/beta.md",
            title="Beta Design",
            content="# Plan\nContains architecture notes and retrieval flow.",
            headings=["Plan"],
            tags=["architecture"],
            metadata={"tags": ["architecture"]},
        ),
    ]


def test_chunker_creates_chunks_with_fields() -> None:
    chunks = split_into_chunks(_notes())
    assert chunks
    first = chunks[0]
    assert first.path
    assert first.title
    assert first.section
    assert first.chunk_id


def test_retriever_matches_title_tags_content_section_and_is_deterministic() -> None:
    chunks = split_into_chunks(_notes())

    by_title = retrieve_lexical("Alpha", chunks, 5)
    by_tags = retrieve_lexical("rag", chunks, 5)
    by_content = retrieve_lexical("retrieval", chunks, 5)
    by_section = retrieve_lexical("api", chunks, 5)
    repeated = retrieve_lexical("api", chunks, 5)

    assert by_title and by_title[0].title == "Alpha System"
    assert by_tags and any(item.path == "00_product/alpha.md" for item in by_tags)
    assert by_content and any(item.path == "02_architecture/beta.md" for item in by_content)
    assert by_section and any(item.section.lower() == "api" for item in by_section)
    assert [x.source_id for x in by_section] == [x.source_id for x in repeated]


def test_retriever_respects_top_k_excludes_zero_and_excerpt_is_short() -> None:
    chunks = split_into_chunks(_notes())
    results = retrieve_lexical("search", chunks, 1)

    assert len(results) == 1
    assert all(item.score > 0 for item in results)
    assert len(results[0].excerpt) <= 180


def test_retriever_keeps_full_chunk_text_next_to_short_excerpt() -> None:
    long_note = MarkdownNote(
        path="00_product/long.md",
        title="Long Source",
        content=" ".join(["Contexte avant search"] + [f"detail-{idx}" for idx in range(80)]),
        headings=["Long Source"],
        tags=[],
        metadata={},
    )
    chunks = split_into_chunks([long_note])
    results = retrieve_lexical("search", chunks, 1)

    assert results[0].chunk_text
    assert results[0].excerpt
    assert results[0].chunk_text != results[0].excerpt
    assert "detail-79" in results[0].chunk_text


def test_retriever_diversifies_documents_in_top_k_when_possible() -> None:
    notes = [
        MarkdownNote(
            path="00_product/a.md",
            title="Alpha MVP",
            content="# One\nmvp mvp mvp mvp\n## Two\nmvp mvp mvp\n## Three\nmvp mvp",
            headings=["One", "Two", "Three"],
            tags=[],
            metadata={},
        ),
        MarkdownNote(
            path="02_architecture/b.md",
            title="Beta MVP",
            content="# One\nmvp architecture",
            headings=["One"],
            tags=[],
            metadata={},
        ),
        MarkdownNote(
            path="04_backlog/c.md",
            title="Gamma MVP",
            content="# One\nmvp backlog",
            headings=["One"],
            tags=[],
            metadata={},
        ),
    ]
    chunks = split_into_chunks(notes)

    results = retrieve_lexical("mvp", chunks, 5)

    assert results[0].path == "00_product/a.md"
    assert len({item.path for item in results}) >= 3
    assert sum(1 for item in results[:3] if item.path == "00_product/a.md") <= 2


def test_retriever_fills_from_same_document_when_no_other_document_matches() -> None:
    note = MarkdownNote(
        path="00_product/only.md",
        title="Only Source",
        content="# One\nunique\n## Two\nunique\n## Three\nunique",
        headings=["One", "Two", "Three"],
        tags=[],
        metadata={},
    )
    chunks = split_into_chunks([note])

    results = retrieve_lexical("unique", chunks, 5)

    assert len(results) == 3
    assert {item.path for item in results} == {"00_product/only.md"}


def test_retriever_diversification_keeps_out_of_context_empty() -> None:
    chunks = split_into_chunks(_notes())

    assert retrieve_lexical("zzzzzzzzzz", chunks, 5) == []


def test_retriever_marks_strong_and_weak_confidence_sources() -> None:
    notes = [
        MarkdownNote(
            path="00_product/strong.md",
            title="MVP Strong",
            content="# One\nmvp mvp mvp mvp mvp",
            headings=["One"],
            tags=[],
            metadata={},
        ),
        MarkdownNote(
            path="04_backlog/weak.md",
            title="Weak",
            content="# One\nrelated mvp backlog note",
            headings=["One"],
            tags=[],
            metadata={},
        ),
    ]
    chunks = split_into_chunks(notes)

    results = retrieve_lexical("mvp", chunks, 5)
    by_path = {item.path: item for item in results}

    assert by_path["00_product/strong.md"].confidence_label == "normal"
    assert by_path["00_product/strong.md"].is_low_confidence is False
    assert by_path["04_backlog/weak.md"].confidence_label == "low"
    assert by_path["04_backlog/weak.md"].is_low_confidence is True


def test_retriever_confidence_marking_is_deterministic() -> None:
    chunks = split_into_chunks(_notes())

    first = retrieve_lexical("api", chunks, 5)
    second = retrieve_lexical("api", chunks, 5)

    assert [(item.source_id, item.confidence_label, item.is_low_confidence) for item in first] == [
        (item.source_id, item.confidence_label, item.is_low_confidence) for item in second
    ]
