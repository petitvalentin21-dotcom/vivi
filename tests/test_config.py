from app.config import load_settings


def test_default_config_values(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    names = [
        "VIVI_HOST",
        "VIVI_PORT",
        "VIVI_API_KEY",
        "VIVI_OLLAMA_BASE_URL",
        "VIVI_LLM_MODEL",
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
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.llm_model == ""
    assert settings.llm_timeout_seconds == 60.0
    assert settings.knowledge_vault_path == "knowledge_vault"
    assert settings.session_store_path == "data/runtime/sessions.json"
    assert settings.max_request_bytes == 1048576
    assert settings.rag_top_k == 5


def test_external_providers_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("VIVI_EXTERNAL_PROVIDERS_ENABLED", raising=False)
    settings = load_settings()
    assert settings.external_providers_enabled is False


def test_env_overrides_config_values(monkeypatch) -> None:
    monkeypatch.setenv("VIVI_API_KEY", "unit-test-key")
    monkeypatch.setenv("VIVI_LLM_MODEL", "mistral-small:24b")
    monkeypatch.setenv("VIVI_OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    settings = load_settings()
    assert settings.api_key == "unit-test-key"
    assert settings.llm_model == "mistral-small:24b"
    assert settings.ollama_base_url == "http://127.0.0.1:11434"


def test_local_dotenv_can_set_llm_model(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "VIVI_LLM_MODEL=qwen3:14b\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("VIVI_LLM_MODEL", raising=False)

    settings = load_settings()
    assert settings.llm_model == "qwen3:14b"


def test_system_env_has_priority_over_local_dotenv(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "VIVI_LLM_MODEL=dotenv-model\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("VIVI_LLM_MODEL", "system-model")

    settings = load_settings()
    assert settings.llm_model == "system-model"
