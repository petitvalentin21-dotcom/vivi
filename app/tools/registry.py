from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters_schema: dict[str, Any]
    callable: Callable[..., Any]
    read_only: bool = True


REGISTRY: dict[str, ToolDefinition] = {}


def register_tool(tool: ToolDefinition) -> None:
    if tool.name in REGISTRY:
        raise ValueError(f"Tool already registered: {tool.name}")
    REGISTRY[tool.name] = tool


def list_tools() -> list[ToolDefinition]:
    return sorted(REGISTRY.values(), key=lambda t: t.name)


def get_tool(name: str) -> ToolDefinition | None:
    return REGISTRY.get(name)
