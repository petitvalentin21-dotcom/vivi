from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str, recovery_hint: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.recovery_hint = recovery_hint


def to_error_payload(*, code: str, message: str, recovery_hint: str, status_code: int, request_id: str = "") -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "recovery_hint": recovery_hint,
        },
        "status_code": status_code,
    }
    if request_id:
        payload["request_id"] = request_id
    return payload


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    request_id = str(request.headers.get("X-Request-ID", "")).strip()
    return JSONResponse(
        status_code=exc.status_code,
        content=to_error_payload(
            code=exc.code,
            message=exc.message,
            recovery_hint=exc.recovery_hint,
            status_code=exc.status_code,
            request_id=request_id,
        ),
    )


async def unhandled_error_handler(request: Request, _: Exception) -> JSONResponse:
    request_id = str(request.headers.get("X-Request-ID", "")).strip()
    return JSONResponse(
        status_code=500,
        content=to_error_payload(
            code="internal_error",
            message="Internal runtime error.",
            recovery_hint="Retry the request and check local logs.",
            status_code=500,
            request_id=request_id,
        ),
    )
