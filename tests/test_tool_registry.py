"""Tests unitaires — ToolRegistry."""
from __future__ import annotations

import pytest

import app.tools  # noqa: F401 — side-effect: registers all tools
from app.tools.registry import REGISTRY, ToolDefinition, get_tool, list_tools, register_tool

_EXPECTED_TOOLS = {
    "list_recettes",
    "get_recette_by_id",
    "list_stock",
    "list_courses",
    "get_preferences_resume",
}


def test_list_tools_returns_five():
    tools = list_tools()
    assert len(tools) == 5


def test_list_tools_contains_expected_names():
    names = {t.name for t in list_tools()}
    assert names == _EXPECTED_TOOLS


def test_list_tools_sorted_by_name():
    names = [t.name for t in list_tools()]
    assert names == sorted(names)


def test_get_tool_known():
    tool = get_tool("list_recettes")
    assert tool is not None
    assert tool.name == "list_recettes"
    assert tool.read_only is True
    assert callable(tool.callable)
    assert "type" in tool.parameters_schema


def test_get_tool_unknown_returns_none():
    assert get_tool("outil_inexistant") is None


def test_all_tools_have_description():
    for tool in list_tools():
        assert tool.description.strip(), f"{tool.name} has empty description"


def test_all_tools_have_valid_parameters_schema():
    for tool in list_tools():
        schema = tool.parameters_schema
        assert schema.get("type") == "object", f"{tool.name}: schema type must be 'object'"
        assert "properties" in schema, f"{tool.name}: schema must have 'properties'"
        assert "required" in schema, f"{tool.name}: schema must have 'required'"


def test_register_tool_raises_on_duplicate():
    with pytest.raises(ValueError, match="already registered"):
        register_tool(ToolDefinition(
            name="list_recettes",
            description="doublon",
            parameters_schema={"type": "object", "properties": {}, "required": []},
            callable=lambda session: [],
        ))


def test_get_recette_by_id_has_required_param():
    tool = get_tool("get_recette_by_id")
    assert tool is not None
    assert "recette_id" in tool.parameters_schema["properties"]
    assert "recette_id" in tool.parameters_schema["required"]


def test_list_stock_has_optional_categorie():
    tool = get_tool("list_stock")
    assert tool is not None
    assert "categorie" in tool.parameters_schema["properties"]
    assert "categorie" not in tool.parameters_schema["required"]
