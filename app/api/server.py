from __future__ import annotations

import sys
from pathlib import Path

from fastapi import Depends, FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.auth import require_api_key
from app.api.errors import ApiError, api_error_handler, unhandled_error_handler
from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationExportRequest,
    ConversationExportResponse,
    HealthResponse,
    KnowledgeSearchResponse,
    ObsidianInboxCreateRequest,
    ObsidianInboxCreateResponse,
    RuntimeInfoResponse,
)
from app.config import Settings, ensure_runtime_dirs, load_settings
from app.knowledge import ObsidianInboxError, create_inbox_note, load_markdown_notes, retrieve_lexical, split_into_chunks
from app.knowledge.sources import Source
from app.llm import LMStudioClient
from app.runtime.status import build_runtime_info
from app.sessions.logger import SessionLogger
from app.sessions.store import SessionStore

_SYSTEM_PROMPT = (
    "VIVI est une IA locale d'assistance personnelle. "
    "Reponds clairement et simplement. "
    "N'invente pas de sources. "
    "Aucun outil externe n'est disponible."
)

_RAG_PROMPT = (
    "Utilise le contexte documentaire si pertinent. "
    "N'invente pas de sources. "
    "Si le contexte est insuffisant, dis-le clairement. "
    "Reponds en francais si l'utilisateur parle francais."
)


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    ensure_runtime_dirs(cfg)
    session_store = SessionStore(cfg.session_store_path)
    session_store.ensure_store()

    try:
        session_logger = SessionLogger(cfg.session_log_path, cfg.log_encryption_key)
    except ValueError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(1)

    app = FastAPI(title="VIVI Backend", version=__version__)
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    web_dir = Path(__file__).resolve().parents[1] / "web"
    app.mount("/web", StaticFiles(directory=web_dir), name="web")

    @app.get("/", include_in_schema=False)
    def web_index() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="vivi", version=__version__, local_first=True)

    @app.get("/runtime/info", response_model=RuntimeInfoResponse)
    def runtime_info() -> RuntimeInfoResponse:
        payload = build_runtime_info(cfg)
        return RuntimeInfoResponse(**payload.__dict__)

    @app.get("/knowledge/search", response_model=KnowledgeSearchResponse)
    def knowledge_search(q: str = Query(...), top_k: int | None = Query(default=None)) -> KnowledgeSearchResponse:
        query = q.strip()
        if not query:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Query must not be empty.",
                recovery_hint="Provide a non-empty q parameter.",
            )

        exists, notes, error = load_markdown_notes(cfg.knowledge_vault_path)
        if not exists:
            raise ApiError(
                status_code=404,
                code="vault_not_found",
                message=error or "Knowledge vault not found.",
                recovery_hint="Set VIVI_KNOWLEDGE_VAULT_PATH to a valid vault directory.",
            )

        chunks = split_into_chunks(notes)
        selected_top_k = top_k if top_k is not None else cfg.rag_top_k
        results = retrieve_lexical(query, chunks, selected_top_k)

        return KnowledgeSearchResponse(
            query=query,
            results=[_source_api_payload(item) for item in results],
            count=len(results),
            mode="lexical",
        )

    @app.post(
        "/obsidian/inbox",
        response_model=ObsidianInboxCreateResponse,
        dependencies=[Depends(require_api_key(cfg))],
    )
    def obsidian_inbox(payload: ObsidianInboxCreateRequest) -> ObsidianInboxCreateResponse:
        try:
            result = create_inbox_note(
                cfg.knowledge_vault_path,
                title=payload.title,
                body=payload.body,
                note_type=payload.note_type,
                status=payload.status,
                related=payload.related,
                prompt_summary=payload.prompt_summary,
                confidence=payload.confidence,
                source_paths=payload.source_paths,
            )
        except ObsidianInboxError as exc:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Obsidian inbox note could not be created.",
                recovery_hint=str(exc),
            ) from exc

        return ObsidianInboxCreateResponse(
            created=True,
            relative_path=result.relative_path,
            filename=result.filename,
            note_type=str(result.frontmatter["type"]),
            status=str(result.frontmatter["status"]),
            index=bool(result.frontmatter["index"]),
            review_required=bool(result.frontmatter["review_required"]),
        )

    @app.post(
        "/conversation/export",
        response_model=ConversationExportResponse,
        dependencies=[Depends(require_api_key(cfg))],
    )
    def conversation_export(payload: ConversationExportRequest) -> ConversationExportResponse:
        user_messages = [m for m in payload.messages if m.role == "user"]
        if not user_messages:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="No user messages to export.",
                recovery_hint="Send at least one user message before exporting.",
            )

        session_id = str(payload.session_id or "").strip() or None
        session_short = session_id[:8] if session_id else "anonyme"
        from datetime import date

        today = date.today().isoformat()
        title = f"Conversation VIVI — {today} — {session_short}"
        body = _format_conversation_body(payload.messages, session_id)

        try:
            result = create_inbox_note(
                cfg.knowledge_vault_path,
                title=title,
                body=body,
                note_type="conversation_summary",
                status="draft",
            )
        except ObsidianInboxError as exc:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Conversation export failed.",
                recovery_hint=str(exc),
            ) from exc

        return ConversationExportResponse(
            exported=True,
            relative_path=result.relative_path,
            filename=result.filename,
        )

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
        if mode not in {"chat", "document"}:
            raise ApiError(
                status_code=400,
                code="invalid_request",
                message="Mode is not supported. Use mode='chat' or mode='document'.",
                recovery_hint="Retry with mode='chat' or mode='document'.",
            )

        rag_used = payload.use_rag if payload.use_rag is not None else False
        if mode == "document":
            rag_used = True

        session_id = str(payload.session_id or "").strip()
        if not session_id:
            session_id = session_store.create_session()
        elif session_store.get_session(session_id) is None:
            raise ApiError(
                status_code=404,
                code="session_not_found",
                message="Session not found.",
                recovery_hint="Create a new session or use a known session_id.",
            )

        sources = []
        rag_context = ""
        if rag_used:
            exists, notes, error = load_markdown_notes(cfg.knowledge_vault_path)
            if not exists:
                raise ApiError(
                    status_code=404,
                    code="vault_not_found",
                    message=error or "Knowledge vault not found.",
                    recovery_hint="Set VIVI_KNOWLEDGE_VAULT_PATH to a valid vault directory.",
                )

            chunks = split_into_chunks(notes)
            selected_top_k = payload.max_sources if payload.max_sources is not None else cfg.rag_top_k
            sources = retrieve_lexical(message, chunks, selected_top_k)
            rag_context = _build_rag_context(sources)

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        if rag_used:
            if rag_context:
                messages.append({"role": "system", "content": f"{_RAG_PROMPT}\n\n{rag_context}"})
            else:
                messages.append(
                    {
                        "role": "system",
                        "content": f"{_RAG_PROMPT}\n\nAucune source Obsidian pertinente n'a ete trouvee.",
                    }
                )

        messages.extend(session_store.last_messages_for_prompt(session_id, limit=4))
        messages.append({"role": "user", "content": message})

        client = LMStudioClient(
            base_url=cfg.lmstudio_base_url,
            model=cfg.lmstudio_model,
            api_key=cfg.lmstudio_api_key,
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

        session_logger.log_exchange(message, answer, completion.model)

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            provider={"name": "lmstudio", "model": completion.model},
            mode=mode,
            sources=[_source_api_payload(item) for item in sources],
            runtime={"rag_used": rag_used, "sources_count": len(sources), "external_call_used": False},
            error=None,
        )

    return app


def _format_conversation_body(messages: list, session_id: str | None) -> str:
    session_short = session_id[:8] if session_id else "anonyme"
    exchanges = sum(1 for m in messages if m.role == "user")
    lines = [
        f"Session : {session_short}",
        f"Échanges : {exchanges}",
        "",
        "---",
        "",
    ]
    for msg in messages:
        if msg.role == "user":
            lines.append(f"**[vous]** {msg.content}")
            lines.append("")
        elif msg.role == "assistant":
            lines.append(f"**[VIVI]** {msg.content}")
            lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines).rstrip()


def _build_rag_context(sources: list) -> str:
    if not sources:
        return ""

    blocks: list[str] = ["Contexte documentaire Obsidian :"]
    for idx, src in enumerate(sources, start=1):
        blocks.append(f"[{idx}] {src.title} - {src.path} - {src.section}")
        blocks.append(str(src.chunk_text).strip())
        blocks.append("")
    return "\n".join(blocks).strip()


def _source_api_payload(source: Source) -> dict:
    return {
        "source_id": source.source_id,
        "path": source.path,
        "title": source.title,
        "section": source.section,
        "score": source.score,
        "excerpt": source.excerpt,
        "chunk_text": source.chunk_text,
        "confidence_label": source.confidence_label,
        "is_low_confidence": source.is_low_confidence,
    }


app = create_app()
