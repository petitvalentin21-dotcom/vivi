from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterator, Sequence

import httpx

_ALLOWED_ROLES = {"system", "user", "assistant"}


@dataclass(frozen=True)
class LMStudioError:
    code: str
    message: str
    recovery_hint: str
    status_code: int


@dataclass(frozen=True)
class LMStudioProviderStatus:
    name: str
    base_url: str
    model: str
    available: bool
    model_configured: bool
    model_available: bool | None
    error: str | None = None


@dataclass(frozen=True)
class LMStudioCompletionResult:
    content: str
    model: str
    provider: str
    raw_model: str | None = None
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None


class LMStudioClient:
    provider_name = "lmstudio"

    def __init__(self, *, base_url: str, model: str, api_key: str = "", timeout_seconds: float) -> None:
        self.base_url = self._normalize_base_url(str(base_url or "http://127.0.0.1:1234"))
        self.model = str(model or "").strip()
        self.api_key = str(api_key or "").strip()
        self.timeout_seconds = float(timeout_seconds)

    def list_models(self) -> tuple[list[str], LMStudioError | None]:
        try:
            payload = self._get_json("/models")
        except LMStudioRequestException as exc:
            return [], exc.error

        data = payload.get("data")
        if not isinstance(data, list):
            return [], self._error(
                code="lmstudio_invalid_response",
                message="LM Studio returned an invalid models response.",
                recovery_hint="Verify LM Studio API compatibility and retry.",
                status_code=502,
            )

        models: list[str] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("id", "")).strip()
            if model_id:
                models.append(model_id)

        return models, None

    def check_health(self) -> LMStudioProviderStatus:
        if not self.model:
            return LMStudioProviderStatus(
                name=self.provider_name,
                base_url=self.base_url,
                model=self.model,
                available=False,
                model_configured=False,
                model_available=None,
                error="LM Studio model is not configured.",
            )

        models, err = self.list_models()
        if err is not None:
            return LMStudioProviderStatus(
                name=self.provider_name,
                base_url=self.base_url,
                model=self.model,
                available=False,
                model_configured=True,
                model_available=None,
                error=err.message,
            )

        model_available = self.model in models
        return LMStudioProviderStatus(
            name=self.provider_name,
            base_url=self.base_url,
            model=self.model,
            available=model_available,
            model_configured=True,
            model_available=model_available,
            error=None if model_available else "Configured LM Studio model not found.",
        )

    def get_provider_status(self) -> LMStudioProviderStatus:
        if not self.model:
            models, err = self.list_models()
            if err is not None:
                return LMStudioProviderStatus(
                    name=self.provider_name,
                    base_url=self.base_url,
                    model=self.model,
                    available=False,
                    model_configured=False,
                    model_available=None,
                    error=err.message,
                )
            return LMStudioProviderStatus(
                name=self.provider_name,
                base_url=self.base_url,
                model=self.model,
                available=True,
                model_configured=False,
                model_available=None,
                error="LM Studio model is not configured.",
            )

        return self.check_health()

    def chat_completion(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[LMStudioCompletionResult | None, LMStudioError | None]:
        selected_model = str(model or self.model).strip()
        if not selected_model:
            return None, self._error(
                code="lmstudio_model_missing",
                message="LM Studio model is not configured.",
                recovery_hint="Set VIVI_LMSTUDIO_MODEL before sending a chat completion request.",
                status_code=400,
            )

        validation_error = self._validate_messages(messages)
        if validation_error is not None:
            return None, validation_error

        payload: dict[str, Any] = {
            "model": selected_model,
            "messages": list(messages),
        }
        if temperature is not None:
            payload["temperature"] = float(temperature)
        if max_tokens is not None:
            payload["max_tokens"] = int(max_tokens)

        try:
            body = self._post_json("/chat/completions", payload)
        except LMStudioRequestException as exc:
            return None, exc.error

        choices = body.get("choices")
        if not isinstance(choices, list) or not choices:
            return None, self._invalid_chat_response_error(body, "choices list is missing or empty")

        first = choices[0]
        if not isinstance(first, dict):
            return None, self._invalid_chat_response_error(body, "choices[0] is not an object")

        message = first.get("message")
        if not isinstance(message, dict):
            return None, self._invalid_chat_response_error(body, "choices[0].message is missing or invalid")

        content = str(message.get("content", "")).strip()
        if not content:
            return None, self._error(
                code="lmstudio_empty_response",
                message="LM Studio returned an empty assistant response.",
                recovery_hint="Retry with a simpler prompt or verify model output in LM Studio.",
                status_code=502,
            )

        usage = body.get("usage") if isinstance(body.get("usage"), dict) else None
        finish_reason = str(first.get("finish_reason", "")).strip() or None
        raw_model = str(body.get("model", "")).strip() or None

        return LMStudioCompletionResult(
            content=content,
            model=selected_model,
            provider=self.provider_name,
            raw_model=raw_model,
            usage=usage,
            finish_reason=finish_reason,
        ), None

    def prepare_stream_payload(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any] | None, LMStudioError | None]:
        selected_model = str(model or self.model).strip()
        if not selected_model:
            return None, self._error(
                code="lmstudio_model_missing",
                message="LM Studio model is not configured.",
                recovery_hint="Set VIVI_LMSTUDIO_MODEL before sending a chat completion request.",
                status_code=400,
            )
        validation_error = self._validate_messages(messages)
        if validation_error is not None:
            return None, validation_error
        payload: dict[str, Any] = {
            "model": selected_model,
            "messages": list(messages),
            "stream": True,
        }
        if temperature is not None:
            payload["temperature"] = float(temperature)
        if max_tokens is not None:
            payload["max_tokens"] = int(max_tokens)
        return payload, None

    def iter_stream(self, payload: dict[str, Any]) -> Iterator[str]:
        url = self._build_url("/chat/completions")
        headers = self._outbound_headers()
        try:
            with httpx.stream(
                "POST", url, json=payload, headers=headers, timeout=self.timeout_seconds
            ) as response:
                if response.status_code >= 400:
                    response.read()
                    raise LMStudioRequestException(
                        self._error(
                            code="lmstudio_http_error",
                            message=f"LM Studio returned HTTP {response.status_code}.",
                            recovery_hint="Verify LM Studio endpoint and model setup.",
                            status_code=502,
                        )
                    )
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                        continue
        except httpx.TimeoutException as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_timeout",
                    message="LM Studio request timed out.",
                    recovery_hint="Increase VIVI_LLM_TIMEOUT_SECONDS or verify LM Studio responsiveness.",
                    status_code=504,
                )
            ) from exc
        except httpx.RequestError as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_unavailable",
                    message="LM Studio is unavailable.",
                    recovery_hint="Start LM Studio and verify VIVI_LMSTUDIO_BASE_URL.",
                    status_code=503,
                )
            ) from exc

    def _validate_messages(self, messages: Sequence[dict[str, Any]]) -> LMStudioError | None:
        if not isinstance(messages, Sequence) or not messages:
            return self._error(
                code="lmstudio_invalid_response",
                message="Messages payload must not be empty.",
                recovery_hint="Send at least one chat message.",
                status_code=400,
            )

        for msg in messages:
            if not isinstance(msg, dict):
                return self._error(
                    code="lmstudio_invalid_response",
                    message="Each message must be an object with role and content.",
                    recovery_hint="Use OpenAI-compatible message format.",
                    status_code=400,
                )
            role = str(msg.get("role", "")).strip().lower()
            content = str(msg.get("content", "")).strip()
            if role not in _ALLOWED_ROLES or not content:
                return self._error(
                    code="lmstudio_invalid_response",
                    message="Invalid message format for LM Studio.",
                    recovery_hint="Use roles system/user/assistant with non-empty content.",
                    status_code=400,
                )
        return None

    def _get_json(self, path: str) -> dict[str, Any]:
        url = self._build_url(path)
        headers = self._outbound_headers()
        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout_seconds)
        except httpx.TimeoutException as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_timeout",
                    message="LM Studio request timed out.",
                    recovery_hint="Increase VIVI_LLM_TIMEOUT_SECONDS or verify LM Studio responsiveness.",
                    status_code=504,
                )
            ) from exc
        except httpx.RequestError as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_unavailable",
                    message="LM Studio is unavailable.",
                    recovery_hint="Start LM Studio and verify VIVI_LMSTUDIO_BASE_URL.",
                    status_code=503,
                )
            ) from exc

        return self._parse_response(response)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self._build_url(path)
        headers = self._outbound_headers()
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
        except httpx.TimeoutException as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_timeout",
                    message="LM Studio request timed out.",
                    recovery_hint="Increase VIVI_LLM_TIMEOUT_SECONDS or verify LM Studio responsiveness.",
                    status_code=504,
                )
            ) from exc
        except httpx.RequestError as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_unavailable",
                    message="LM Studio is unavailable.",
                    recovery_hint="Start LM Studio and verify VIVI_LMSTUDIO_BASE_URL.",
                    status_code=503,
                )
            ) from exc

        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            recovery_hint = "Verify LM Studio endpoint and model setup."
            if response.status_code == 401:
                recovery_hint = (
                    "Verify LM Studio auth configuration. "
                    "Use VIVI_LMSTUDIO_API_KEY if LM Studio requires authentication."
                )
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_http_error",
                    message=f"LM Studio returned HTTP {response.status_code}.",
                    recovery_hint=recovery_hint,
                    status_code=502,
                )
            )
        try:
            payload = response.json()
        except ValueError as exc:
            content_type = response.headers.get("content-type", "unknown")
            snippet = response.text[:120].replace("\n", " ").strip()
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_invalid_response",
                    message=f"LM Studio returned invalid JSON (content-type={content_type}).",
                    recovery_hint=f"Retry and check LM Studio server output. body_preview={snippet!r}",
                    status_code=502,
                )
            ) from exc

        if not isinstance(payload, dict):
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_invalid_response",
                    message="LM Studio returned an unexpected response body.",
                    recovery_hint="Retry and verify OpenAI-compatible output format.",
                    status_code=502,
                )
            )
        return payload

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _normalize_base_url(self, base_url: str) -> str:
        base = str(base_url or "").strip().rstrip("/")
        if not base:
            base = "http://127.0.0.1:1234"
        if base.endswith("/v1"):
            return base
        return f"{base}/v1"

    def _outbound_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _invalid_chat_response_error(self, body: dict[str, Any], reason: str) -> LMStudioError:
        choices = body.get("choices") if isinstance(body, dict) else None
        has_choices = isinstance(choices, list)
        first_choice = choices[0] if has_choices and choices else None
        first_choice_is_dict = isinstance(first_choice, dict)
        message = first_choice.get("message") if first_choice_is_dict else None
        message_is_dict = isinstance(message, dict)
        has_content = bool(str(message.get("content", "")).strip()) if message_is_dict else False
        payload_type = type(body).__name__
        choices_type = type(choices).__name__ if choices is not None else "missing"
        detail = (
            f"reason={reason}; payload_type={payload_type}; choices_type={choices_type}; "
            f"has_choices={has_choices}; first_choice_is_dict={first_choice_is_dict}; "
            f"message_is_dict={message_is_dict}; has_content={has_content}"
        )
        return self._error(
            code="lmstudio_invalid_response",
            message="LM Studio returned an invalid chat response.",
            recovery_hint=f"Verify LM Studio response format and retry. ({detail})",
            status_code=502,
        )

    def _error(self, *, code: str, message: str, recovery_hint: str, status_code: int) -> LMStudioError:
        return LMStudioError(code=code, message=message, recovery_hint=recovery_hint, status_code=status_code)


class LMStudioRequestException(Exception):
    def __init__(self, error: LMStudioError) -> None:
        super().__init__(error.message)
        self.error = error
