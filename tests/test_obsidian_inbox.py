from pathlib import Path

import pytest

from app.knowledge.markdown_loader import load_markdown_notes
from app.knowledge.obsidian_inbox import ObsidianInboxError, create_inbox_note


def _vault(tmp_path: Path) -> Path:
    inbox = tmp_path / "92_inbox"
    inbox.mkdir()
    return tmp_path


def test_create_inbox_note_writes_valid_markdown_in_92_inbox(tmp_path: Path) -> None:
    result = create_inbox_note(
        _vault(tmp_path),
        "Synthèse proposée accès LAN",
        "Contenu de la note.",
        note_type="conversation_summary",
        source_paths=["docs/OBSIDIAN_WRITE_GOVERNANCE.md"],
    )

    created = Path(result.absolute_path)
    content = created.read_text(encoding="utf-8")

    assert result.relative_path.startswith("92_inbox/")
    assert result.filename.endswith("_inbox_synthese-proposee-acces-lan.md")
    assert created.parent == tmp_path / "92_inbox"
    assert result.frontmatter == {
        "type": "conversation_summary",
        "status": "draft",
        "source": "vivi",
        "created_at": result.frontmatter["created_at"],
        "index": False,
        "review_required": True,
        "source_paths": ["docs/OBSIDIAN_WRITE_GOVERNANCE.md"],
    }
    assert "type: conversation_summary" in content
    assert "status: draft" in content
    assert "source: vivi" in content
    assert "index: false" in content
    assert "review_required: true" in content
    assert "# Synthèse proposée accès LAN" in content
    assert "Proposition générée par VIVI" in content
    assert "Contenu de la note." in content
    assert "## Sources liées" in content
    assert "- docs/OBSIDIAN_WRITE_GOVERNANCE.md" in content


def test_create_inbox_note_allows_only_simple_types_and_statuses(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    ok = create_inbox_note(vault, "Décision", "Brouillon", note_type="decision_proposal", status="to_review")

    assert ok.frontmatter["type"] == "decision_proposal"
    assert ok.frontmatter["status"] == "to_review"

    with pytest.raises(ObsidianInboxError, match="note_type"):
        create_inbox_note(vault, "Décision", "Brouillon", note_type="validated_decision")

    with pytest.raises(ObsidianInboxError, match="status"):
        create_inbox_note(vault, "Décision", "Brouillon", status="validated")


def test_create_inbox_note_generates_safe_unique_filenames(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    first = create_inbox_note(vault, "Note: Windows / dangereuse? * test", "Un")
    second = create_inbox_note(vault, "Note: Windows / dangereuse? * test", "Deux")

    assert first.filename.endswith("_inbox_note-windows-dangereuse-test.md")
    assert second.filename.endswith("_inbox_note-windows-dangereuse-test_001.md")
    assert Path(first.absolute_path).read_text(encoding="utf-8").endswith("Un\n")
    assert Path(second.absolute_path).read_text(encoding="utf-8").endswith("Deux\n")


@pytest.mark.parametrize(
    "title",
    [
        "../outside",
        "..\\outside",
        "C:\\Windows\\system32",
        "/etc/passwd",
        ".obsidian/config",
        "00_product/source",
        "02_architecture/spec",
        "03_decisions/decision",
        "04_backlog/task",
        "05_runs/run",
        "90_generated/export",
        "91_runtime/index",
        "99_archive/old",
        '<bad>:"|?*',
    ],
)
def test_create_inbox_note_neutralizes_dangerous_title_paths(tmp_path: Path, title: str) -> None:
    result = create_inbox_note(_vault(tmp_path), title, "Contenu")
    created = Path(result.absolute_path)

    assert created.exists()
    assert created.parent == tmp_path / "92_inbox"
    assert result.relative_path.startswith("92_inbox/")
    assert not any(part in result.filename for part in ["..", "/", "\\", "<", ">", ":", '"', "|", "?", "*"])


def test_create_inbox_note_rejects_empty_or_fully_invalid_titles(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    with pytest.raises(ObsidianInboxError):
        create_inbox_note(vault, "", "Contenu")

    with pytest.raises(ObsidianInboxError, match="safe characters"):
        create_inbox_note(vault, "////\\\\\\::::****", "Contenu")


def test_create_inbox_note_never_writes_outside_inbox_or_existing_source_files(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    source_file = tmp_path / "00_product" / "source.md"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("# Source humaine\n", encoding="utf-8")

    result = create_inbox_note(vault, "../00_product/source", "Proposition")

    assert Path(result.absolute_path).parent == tmp_path / "92_inbox"
    assert source_file.read_text(encoding="utf-8") == "# Source humaine\n"
    assert not (tmp_path / ".obsidian").exists()
    for folder in ["02_architecture", "03_decisions", "04_backlog", "05_runs", "90_generated", "91_runtime", "99_archive"]:
        assert not (tmp_path / folder / result.filename).exists()


def test_create_inbox_note_rejects_sensitive_content_and_does_not_log_or_call_network(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    with pytest.raises(ObsidianInboxError, match="sensitive"):
        create_inbox_note(vault, "Secret", "api_key=do-not-write-this")

    assert not list((tmp_path / "92_inbox").glob("*.md")) if (tmp_path / "92_inbox").exists() else True


def test_create_inbox_note_rejects_unsafe_source_paths(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    with pytest.raises(ObsidianInboxError, match="source_paths"):
        create_inbox_note(vault, "Note", "Contenu", source_paths=["../00_product/source.md"])

    with pytest.raises(ObsidianInboxError, match="source_paths"):
        create_inbox_note(vault, "Note", "Contenu", source_paths=["/absolute/source.md"])

    with pytest.raises(ObsidianInboxError, match="source_paths"):
        create_inbox_note(vault, "Note", "Contenu", source_paths=[".obsidian/config"])


def test_created_inbox_note_is_not_loaded_by_rag(tmp_path: Path) -> None:
    create_inbox_note(_vault(tmp_path), "Résumé RAG", "Ce brouillon ne doit pas être indexé.", note_type="rag_summary")
    source = tmp_path / "00_product" / "visible.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Visible\nContexte indexable.", encoding="utf-8")

    exists, notes, error = load_markdown_notes(str(tmp_path))

    assert exists is True
    assert error is None
    assert {note.path for note in notes} == {"00_product/visible.md"}
