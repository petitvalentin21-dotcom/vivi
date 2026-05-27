from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMError:
    code: str
    message: str
    recovery_hint: str
    status_code: int


@dataclass(frozen=True)
class LLMProviderStatus:
    name: str
    base_url: str
    model: str
    available: bool
    model_configured: bool
    model_available: bool | None
    error: str | None = None


@dataclass(frozen=True)
class LLMCompletionResult:
    content: str
    model: str
    provider: str
    raw_model: str | None = None
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None


class LLMRequestException(Exception):
    def __init__(self, error: LLMError) -> None:
        super().__init__(error.message)
        self.error = error
