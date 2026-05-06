from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.api.errors import ApiError, api_error_handler, unhandled_error_handler
from app.api.schemas import HealthResponse, RuntimeInfoResponse
from app.config import Settings, ensure_runtime_dirs, load_settings
from app.runtime.status import build_runtime_info
from app.sessions.store import SessionStore


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    ensure_runtime_dirs(cfg)
    SessionStore(cfg.session_store_path).ensure_store()

    app = FastAPI(title="VIVI Backend", version=__version__)
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="vivi", version=__version__, local_first=True)

    @app.get("/runtime/info", response_model=RuntimeInfoResponse)
    def runtime_info() -> RuntimeInfoResponse:
        payload = build_runtime_info(cfg)
        return RuntimeInfoResponse(**payload.__dict__)

    return app


app = create_app()
