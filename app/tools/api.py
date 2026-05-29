from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.tools.registry import get_tool, list_tools
from app.tools.schemas import (
    ToolDescriptor,
    ToolInvocationRequest,
    ToolInvocationResponse,
    ToolListResponse,
)

router = APIRouter(prefix="/tools", tags=["tools"])


def _get_session(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Base de données non configurée")
    with Session(engine) as session:
        yield session


@router.get("", response_model=ToolListResponse, summary="Liste les outils disponibles pour le LLM")
def list_tools_endpoint() -> ToolListResponse:
    tools = list_tools()
    return ToolListResponse(
        tools=[
            ToolDescriptor(
                name=t.name,
                description=t.description,
                parameters_schema=t.parameters_schema,
                read_only=t.read_only,
            )
            for t in tools
        ],
        count=len(tools),
    )


@router.post(
    "/{name}/invoke",
    response_model=ToolInvocationResponse,
    summary="Invoque un outil par son nom (endpoint de debug)",
)
def invoke_tool_endpoint(
    name: str,
    payload: ToolInvocationRequest,
    session: Session = Depends(_get_session),
) -> ToolInvocationResponse:
    tool = get_tool(name)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"tool '{name}' not found")
    try:
        result = tool.callable(session, **payload.arguments)
        return ToolInvocationResponse(tool=name, ok=True, result=result)
    except TypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
