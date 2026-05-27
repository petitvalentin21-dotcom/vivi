from __future__ import annotations

import httpx

from app.llm.ollama import OllamaClient


def test_provider_name_is_ollama() -> None:
    client = OllamaClient(base_url="http://localhost:11434/v1", model="m1", timeout_seconds=60)
    assert client.provider_name == "ollama"


def test_base_url_default_shape() -> None:
    client = OllamaClient(base_url="http://localhost:11434/v1/", model="m1", timeout_seconds=60)
    assert client.base_url == "http://localhost:11434/v1"


def test_base_url_without_v1_is_normalized() -> None:
    client = OllamaClient(base_url="http://localhost:11434", model="m1", timeout_seconds=60)
    assert client.base_url == "http://localhost:11434/v1"


def test_healthcheck_unavailable_when_server_inaccessible(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(httpx, "get", fake_get)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="m1", timeout_seconds=1)

    status = client.get_provider_status()
    assert status.available is False
    assert status.error is not None


def test_list_models_parses_valid_response(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        return httpx.Response(200, json={"data": [{"id": "model-a"}, {"id": "model-b"}]})

    monkeypatch.setattr(httpx, "get", fake_get)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    models, err = client.list_models()
    assert err is None
    assert models == ["model-a", "model-b"]


def test_healthcheck_detects_configured_model_present(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        return httpx.Response(200, json={"data": [{"id": "model-a"}]})

    monkeypatch.setattr(httpx, "get", fake_get)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    status = client.check_health()
    assert status.available is True
    assert status.model_configured is True
    assert status.model_available is True


def test_healthcheck_signals_configured_model_absent(monkeypatch) -> None:
    def fake_get(*args, **kwargs):
        return httpx.Response(200, json={"data": [{"id": "other"}]})

    monkeypatch.setattr(httpx, "get", fake_get)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    status = client.check_health()
    assert status.available is False
    assert status.model_available is False
    assert status.error is not None


def test_chat_completion_posts_expected_payload(monkeypatch) -> None:
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return httpx.Response(
            200,
            json={
                "model": "model-a",
                "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=7)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "hi"}])
    assert err is None
    assert result is not None
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["json"]["model"] == "model-a"
    assert captured["json"]["messages"][0]["content"] == "hi"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert "Authorization" not in captured["headers"]


def test_chat_completion_sends_no_authorization_header(monkeypatch) -> None:
    """Ollama ne nécessite pas d'authentification — aucun header Authorization."""
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["headers"] = headers
        return httpx.Response(
            200,
            json={
                "model": "model-a",
                "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=7)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "hi"}])
    assert err is None
    assert result is not None
    assert "Authorization" not in captured["headers"]


def test_chat_completion_extracts_choices_content(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(
            200,
            json={
                "model": "model-a",
                "usage": {"total_tokens": 12},
                "choices": [{"message": {"content": "assistant output"}, "finish_reason": "stop"}],
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "prompt"}])
    assert err is None
    assert result is not None
    assert result.content == "assistant output"
    assert result.finish_reason == "stop"
    assert result.provider == "ollama"


def test_chat_completion_handles_empty_response(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, json={"choices": [{"message": {"content": ""}}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_empty_response"


def test_chat_completion_handles_invalid_response(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, json={"foo": "bar"})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_invalid_response"
    assert "choices list is missing or empty" in err.recovery_hint


def test_chat_completion_handles_empty_choices_list(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, json={"choices": []})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)
    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_invalid_response"
    assert "choices list is missing or empty" in err.recovery_hint


def test_chat_completion_handles_missing_message(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop"}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)
    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_invalid_response"
    assert "choices[0].message is missing or invalid" in err.recovery_hint


def test_chat_completion_handles_missing_content(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, json={"choices": [{"message": {}}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)
    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_empty_response"


def test_chat_completion_handles_timeout(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=1)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_timeout"


def test_chat_completion_fails_when_model_not_configured() -> None:
    client = OllamaClient(base_url="http://localhost:11434/v1", model="", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_model_missing"


def test_errors_do_not_contain_unexpected_secrets(monkeypatch) -> None:
    secret = "sk-super-secret"

    def fake_post(*args, **kwargs):
        raise httpx.RequestError(secret)

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert secret not in err.message
    assert secret not in err.recovery_hint


def test_http_error_returns_ollama_http_error_code(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(500, json={"error": "internal"})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)

    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_http_error"


def test_invalid_json_error_contains_safe_diagnostic(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return httpx.Response(200, text="<html>oops</html>", headers={"content-type": "text/html"})

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434/v1", model="model-a", timeout_seconds=5)
    result, err = client.chat_completion(messages=[{"role": "user", "content": "x"}])
    assert result is None
    assert err is not None
    assert err.code == "ollama_invalid_response"
    assert "content-type=text/html" in err.message
    assert "body_preview=" in err.recovery_hint
