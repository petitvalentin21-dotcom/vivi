from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

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

    def __init__(self, *, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = str(base_url or "http://localhost:1234/v1").rstrip("/")
        self.model = str(model or "").strip()
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
            return None, self._error(
                code="lmstudio_invalid_response",
                message="LM Studio returned an invalid chat response.",
                recovery_hint="Verify LM Studio response format and retry.",
                status_code=502,
            )

        first = choices[0]
        if not isinstance(first, dict):
            return None, self._error(
                code="lmstudio_invalid_response",
                message="LM Studio returned an invalid choice entry.",
                recovery_hint="Verify LM Studio response format and retry.",
                status_code=502,
            )

        message = first.get("message")
        if not isinstance(message, dict):
            return None, self._error(
                code="lmstudio_invalid_response",
                message="LM Studio response is missing assistant message.",
                recovery_hint="Retry and ensure LM Studio returns OpenAI-compatible choices.",
                status_code=502,
            )

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
        try:
            response = httpx.get(url, timeout=self.timeout_seconds)
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
        try:
            response = httpx.post(url, json=payload, timeout=self.timeout_seconds)
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
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_http_error",
                    message=f"LM Studio returned HTTP {response.status_code}.",
                    recovery_hint="Verify LM Studio endpoint and model setup.",
                    status_code=502,
                )
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise LMStudioRequestException(
                self._error(
                    code="lmstudio_invalid_response",
                    message="LM Studio returned invalid JSON.",
                    recovery_hint="Retry and check LM Studio server output.",
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

    def _error(self, *, code: str, message: str, recovery_hint: str, status_code: int) -> LMStudioError:
        return LMStudioError(code=code, message=message, recovery_hint=recovery_hint, status_code=status_code)


class LMStudioRequestException(Exception):
    def __init__(self, error: LMStudioError) -> None:
        super().__init__(error.message)
        self.error = error
