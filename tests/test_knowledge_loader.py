from pathlib import Path

from app.knowledge.markdown_loader import load_markdown_notes


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_loader_loads_included_markdown_files(tmp_path: Path) -> None:
    _write(tmp_path / "00_product" / "a.md", "# A\ncontent")
    _write(tmp_path / "01_user_docs" / "b.md", "# B\ncontent")
    _write(tmp_path / "91_runtime" / "ignored.md", "# Ignored")

    exists, notes, err = load_markdown_notes(str(tmp_path))

    assert exists is True
    assert err is None
    paths = {n.path for n in notes}
    assert "00_product/a.md" in paths
    assert "01_user_docs/b.md" in paths
    assert "91_runtime/ignored.md" not in paths


def test_loader_ignores_excluded_folders(tmp_path: Path) -> None:
    for folder in [".obsidian", "90_generated", "91_runtime", "92_inbox", "99_archive"]:
        _write(tmp_path / folder / "x.md", "# X")
    _write(tmp_path / "02_architecture" / "ok.md", "# OK")

    _, notes, _ = load_markdown_notes(str(tmp_path))
    paths = {n.path for n in notes}
    assert paths == {"02_architecture/ok.md"}


def test_loader_ignores_index_false(tmp_path: Path) -> None:
    _write(
        tmp_path / "03_decisions" / "off.md",
        "---\nindex: false\ntitle: Hidden\n---\n# Hidden\nsecret",
    )
    _write(tmp_path / "03_decisions" / "on.md", "---\nindex: true\n---\n# Visible")

    _, notes, _ = load_markdown_notes(str(tmp_path))
    titles = {n.title for n in notes}
    assert "Hidden" not in titles
    assert "Visible" in titles


def test_loader_extracts_title_from_frontmatter_then_h1_then_filename(tmp_path: Path) -> None:
    _write(tmp_path / "04_backlog" / "front.md", "---\ntitle: Front Title\n---\n# H1")
    _write(tmp_path / "04_backlog" / "h1.md", "# H1 Title\ntext")
    _write(tmp_path / "04_backlog" / "name.md", "text only")

    _, notes, _ = load_markdown_notes(str(tmp_path))
    by_path = {n.path: n for n in notes}
    assert by_path["04_backlog/front.md"].title == "Front Title"
    assert by_path["04_backlog/h1.md"].title == "H1 Title"
    assert by_path["04_backlog/name.md"].title == "name"


def test_loader_extracts_tags_from_frontmatter_list_and_string(tmp_path: Path) -> None:
    _write(tmp_path / "05_runs" / "list.md", "---\ntags:\n- rag\n- mvp\n---\n# T")
    _write(tmp_path / "05_runs" / "str.md", "---\ntags: backend\n---\n# T")

    _, notes, _ = load_markdown_notes(str(tmp_path))
    by_path = {n.path: n for n in notes}
    assert by_path["05_runs/list.md"].tags == ["rag", "mvp"]
    assert by_path["05_runs/str.md"].tags == ["backend"]
