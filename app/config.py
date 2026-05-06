from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    api_key: str = ""
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = ""
    llm_timeout_seconds: float = 60.0
    knowledge_vault_path: str = "knowledge_vault"
    session_store_path: str = "data/runtime/sessions.json"
    max_request_bytes: int = 1_048_576
    rag_top_k: int = 5
    external_providers_enabled: bool = False

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_key.strip())


def load_settings() -> Settings:
    return Settings(
        host=_env_str("VIVI_HOST", "127.0.0.1"),
        port=_env_int("VIVI_PORT", 8000),
        api_key=_env_str("VIVI_API_KEY", ""),
        lmstudio_base_url=_env_str("VIVI_LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
        lmstudio_model=_env_str("VIVI_LMSTUDIO_MODEL", ""),
        llm_timeout_seconds=_env_float("VIVI_LLM_TIMEOUT_SECONDS", 60.0),
        knowledge_vault_path=_env_str("VIVI_KNOWLEDGE_VAULT_PATH", "knowledge_vault"),
        session_store_path=_env_str("VIVI_SESSION_STORE_PATH", "data/runtime/sessions.json"),
        max_request_bytes=_env_int("VIVI_MAX_REQUEST_BYTES", 1_048_576),
        rag_top_k=_env_int("VIVI_RAG_TOP_K", 5),
        external_providers_enabled=_env_bool("VIVI_EXTERNAL_PROVIDERS_ENABLED", False),
    )


def ensure_runtime_dirs(settings: Settings) -> None:
    Path(settings.session_store_path).parent.mkdir(parents=True, exist_ok=True)


def _env_str(name: str, default: str) -> str:
    value = str(os.getenv(name, "")).strip()
    return value if value else default


def _env_int(name: str, default: int) -> int:
    value = str(os.getenv(name, "")).strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = str(os.getenv(name, "")).strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = str(os.getenv(name, "")).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default
