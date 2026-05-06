from __future__ import annotations

from fastapi import Header, HTTPException

from app.config import Settings


def require_api_key(settings: Settings):
    def _dependency(
        authorization: str | None = Header(default=None, alias="Authorization"),
        x_vivi_api_key: str | None = Header(default=None, alias="X-VIVI-API-Key"),
    ) -> None:
        if not settings.auth_enabled:
            return

        expected = settings.api_key.strip()
        bearer = ""
        if authorization:
            raw = authorization.strip()
            if raw.lower().startswith("bearer "):
                bearer = raw[7:].strip()
        header_key = str(x_vivi_api_key or "").strip()
        if bearer == expected or header_key == expected:
            return
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "auth_required",
                    "message": "Authentication required.",
                    "recovery_hint": "Send Authorization: Bearer <VIVI_API_KEY> or X-VIVI-API-Key.",
                }
            },
        )

    return _dependency
