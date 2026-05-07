from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings
from app.knowledge import load_markdown_notes, retrieve_lexical, split_into_chunks

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "rag_validation_cases.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _write_validation_vault(tmp_path: Path) -> Path:
    fixture = _load_fixture()
    vault = tmp_path / "knowledge_vault"
    for document in fixture["documents"]:
        target = vault / document["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document["content"], encoding="utf-8")
    return vault


def _search(vault: Path, question: str, top_k: int):
    exists, notes, error = load_markdown_notes(str(vault))
    assert exists, error
    chunks = split_into_chunks(notes)
    return retrieve_lexical(question, chunks, top_k)


def test_rag_validation_fixture_covers_required_case_types() -> None:
    fixture = _load_fixture()
    case_ids = {case["id"] for case in fixture["cases"]}

    assert "product_mvp_goal" in case_ids
    assert "backend_api_contract" in case_ids
    assert "rag_obsidian_role" in case_ids
    assert "out_of_context" in case_ids
    assert "ambiguous_short_question" in case_ids


def test_rag_validation_reference_questions_return_expected_sources(tmp_path: Path) -> None:
    fixture = _load_fixture()
    vault = _write_validation_vault(tmp_path)

    for case in fixture["cases"]:
        results = _search(vault, case["question"], case["max_sources"])
        result_paths = {source.path for source in results}
        combined_excerpt = "\n".join(source.excerpt for source in results)

        assert len(results) >= case["min_sources"], case["id"]
        assert len(results) <= case["max_sources"], case["id"]
        for expected_path in case["expected_paths"]:
            assert expected_path in result_paths, case["id"]
        for keyword in case["expected_excerpt_keywords"]:
            assert keyword.lower() in combined_excerpt.lower(), case["id"]
        for forbidden in case["forbidden_keywords"]:
            assert forbidden.lower() not in combined_excerpt.lower(), case["id"]


def test_rag_validation_out_of_context_does_not_invent_sources(tmp_path: Path) -> None:
    fixture = _load_fixture()
    vault = _write_validation_vault(tmp_path)
    case = next(item for item in fixture["cases"] if item["id"] == "out_of_context")

    results = _search(vault, case["question"], 3)

    assert results == []


def test_rag_validation_is_deterministic_for_ambiguous_question(tmp_path: Path) -> None:
    fixture = _load_fixture()
    vault = _write_validation_vault(tmp_path)
    case = next(item for item in fixture["cases"] if item["id"] == "ambiguous_short_question")

    first = _search(vault, case["question"], case["max_sources"])
    second = _search(vault, case["question"], case["max_sources"])

    assert [source.source_id for source in first] == [source.source_id for source in second]
    assert len(first) <= case["max_sources"]


def test_rag_validation_endpoint_uses_fixture_without_lmstudio_or_secret_leak(tmp_path: Path) -> None:
    fixture = _load_fixture()
    vault = _write_validation_vault(tmp_path)
    secret = "test-only-secret-value"
    app = create_app(
        Settings(
            api_key=secret,
            knowledge_vault_path=str(vault),
            session_store_path=str(tmp_path / "runtime" / "sessions.json"),
            rag_top_k=3,
        )
    )
    client = TestClient(app)

    for case in fixture["cases"]:
        response = client.get("/knowledge/search", params={"q": case["question"], "top_k": case["max_sources"]})

        assert response.status_code == 200, case["id"]
        assert secret not in response.text
        payload = response.json()
        assert payload["mode"] == "lexical"
        assert payload["count"] == len(payload["results"])
        assert payload["count"] <= case["max_sources"]
