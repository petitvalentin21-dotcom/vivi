from app.config import load_settings


def test_default_config_values(monkeypatch) -> None:
    names = [
        "VIVI_HOST",
        "VIVI_PORT",
        "VIVI_API_KEY",
        "VIVI_LMSTUDIO_BASE_URL",
        "VIVI_LMSTUDIO_MODEL",
        "VIVI_LMSTUDIO_API_KEY",
        "VIVI_LLM_TIMEOUT_SECONDS",
        "VIVI_KNOWLEDGE_VAULT_PATH",
        "VIVI_SESSION_STORE_PATH",
        "VIVI_MAX_REQUEST_BYTES",
        "VIVI_RAG_TOP_K",
        "VIVI_EXTERNAL_PROVIDERS_ENABLED",
    ]
    for name in names:
        monkeypatch.delenv(name, raising=False)

    settings = load_settings()
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.api_key == ""
    assert settings.lmstudio_base_url == "http://localhost:1234/v1"
    assert settings.lmstudio_model == ""
    assert settings.lmstudio_api_key == ""
    assert settings.llm_timeout_seconds == 60.0
    assert settings.knowledge_vault_path == "knowledge_vault"
    assert settings.session_store_path == "data/runtime/sessions.json"
    assert settings.max_request_bytes == 1048576
    assert settings.rag_top_k == 5


def test_external_providers_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("VIVI_EXTERNAL_PROVIDERS_ENABLED", raising=False)
    settings = load_settings()
    assert settings.external_providers_enabled is False
