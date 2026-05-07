from __future__ import annotations

from dataclasses import dataclass

from app import __version__
from app.config import Settings
from app.knowledge.markdown_loader import count_markdown_notes
from app.llm.lmstudio import LMStudioClient


@dataclass(frozen=True)
class RuntimeInfo:
    service: str
    version: str
    local_first: bool
    auth_enabled: bool
    provider: dict
    vault: dict
    sessions: dict
    rag: dict
    external_providers_enabled: bool


def build_runtime_info(settings: Settings) -> RuntimeInfo:
    provider_client = LMStudioClient(
        base_url=settings.lmstudio_base_url,
        model=settings.lmstudio_model,
        api_key=settings.lmstudio_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    provider = provider_client.get_provider_status().__dict__

    exists, notes_count, vault_error = count_markdown_notes(settings.knowledge_vault_path)

    vault = {
        "path": settings.knowledge_vault_path,
        "exists": exists,
        "notes_count": notes_count,
        "indexed": False,
        "error": vault_error,
    }

    sessions = {
        "enabled": True,
        "store_path": settings.session_store_path,
    }

    rag = {
        "enabled": True,
        "mode": "lexical",
        "top_k": settings.rag_top_k,
    }

    return RuntimeInfo(
        service="vivi",
        version=__version__,
        local_first=True,
        auth_enabled=settings.auth_enabled,
        provider=provider,
        vault=vault,
        sessions=sessions,
        rag=rag,
        external_providers_enabled=settings.external_providers_enabled,
    )
