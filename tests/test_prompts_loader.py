"""Tests unitaires — loader de prompts versionnés."""
from __future__ import annotations

import pytest

from app.prompts.loader import DEFAULT_VERSION, list_prompts, list_versions, load_prompt


def test_load_system_returns_string():
    content = load_prompt("system")
    assert isinstance(content, str)
    assert len(content) > 0


def test_load_system_contains_keywords():
    content = load_prompt("system")
    assert "Vivi" in content
    assert "Ollama" in content


def test_load_tool_calling_returns_string():
    content = load_prompt("tool_calling")
    assert isinstance(content, str)
    assert len(content) > 0


def test_load_tool_calling_aligned_with_feat22():
    content = load_prompt("tool_calling")
    assert "list_stock" in content or "list_recettes" in content


def test_load_inexistant_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("inexistant")


def test_load_unknown_version_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("system", version="v99")


def test_list_prompts_returns_expected():
    prompts = list_prompts()
    assert prompts == ["system", "tool_calling"]


def test_list_prompts_unknown_version_returns_empty():
    result = list_prompts(version="v99")
    assert result == []


def test_list_versions_contains_v1():
    versions = list_versions()
    assert "v1" in versions
