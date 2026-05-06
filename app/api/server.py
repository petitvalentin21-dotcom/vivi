from __future__ import annotations

from fastapi import Depends, FastAPI

from app import __version__
from app.api.auth import require_api_key
from app.api.errors import ApiError, api_error_handler, unhandled_error_handler
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse, RuntimeInfoResponse
from app.config import Settings, ensure_runtime_dirs, load_settings
from app.llm import LMStudioClient
from app.runtime.status import build_runtime_info
from app.sessions.store import SessionStore

_SYSTEM_PROMPT = (
    "VIVI est une IA locale d'assistance personnelle. "
    "Reponds clairement et simplement. "
    "N'invente pas de sources. "
    "Aucun outil externe n'est disponible."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    ensure_runtime_dirs(cfg)
    session_store = SessionStore(cfg.session_store_path)
    session_store.ensure_store()

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

    @app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key(cfg))])
    def chat(payload: ChatRequest) -> ChatResponse:
        message = payload.message.strip()
        if not message:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Message must not be empty.",
                recovery_hint="Provide a non-empty message.",
            )

        mode = str(payload.mode or "chat").strip().lower()
        if mode != "chat":
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Mode is not supported in FEAT-03. Use mode='chat'.",
                recovery_hint="Retry with mode='chat'.",
            )

        if payload.use_rag:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="RAG is not available yet. It will be added in FEAT-04.",
                recovery_hint="Retry with use_rag=false.",
            )

        session_id = str(payload.session_id or "").strip()
        if not session_id:
            session_id = session_store.create_session()
        else:
            if session_store.get_session(session_id) is None:
                raise ApiError(
                    status_code=404,
                    code="session_not_found",
                    message="Session not found.",
                    recovery_hint="Create a new session or use a known session_id.",
                )

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        messages.extend(session_store.last_messages_for_prompt(session_id, limit=4))
        messages.append({"role": "user", "content": message})

        client = LMStudioClient(
            base_url=cfg.lmstudio_base_url,
            model=cfg.lmstudio_model,
            timeout_seconds=cfg.llm_timeout_seconds,
        )
        completion, err = client.chat_completion(
            messages=messages,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
        if err is not None:
            raise ApiError(
                status_code=err.status_code,
                code=err.code,
                message=err.message,
                recovery_hint=err.recovery_hint,
            )
        if completion is None:
            raise ApiError(
                status_code=502,
                code="lmstudio_invalid_response",
                message="LM Studio returned an invalid chat response.",
                recovery_hint="Retry and verify LM Studio configuration.",
            )

        answer = completion.content
        session_store.append_messages(
            session_id,
            [
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer},
            ],
        )

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            provider={"name": "lmstudio", "model": completion.model},
            mode="chat",
            sources=[],
            runtime={"rag_used": False, "sources_count": 0, "external_call_used": False},
            error=None,
        )

    return app


app = create_app()
