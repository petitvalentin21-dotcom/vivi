from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolDescriptor(BaseModel):
    name: str
    description: str
    parameters_schema: dict
    read_only: bool


class ToolListResponse(BaseModel):
    tools: list[ToolDescriptor]
    count: int


class ToolInvocationRequest(BaseModel):
    arguments: dict = Field(default_factory=dict)


class ToolInvocationResponse(BaseModel):
    tool: str
    ok: bool
    result: Any | None = None
    error: str | None = None
