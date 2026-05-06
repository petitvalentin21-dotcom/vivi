from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class LMStudioHealth:
    name: str
    base_url: str
    model: str
    available: bool
    error: str | None = None


class LMStudioClient:
    provider_name = "lmstudio"

    def __init__(self, *, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> LMStudioHealth:
        url = f"{self.base_url}/models"
        try:
            response = httpx.get(url, timeout=self.timeout_seconds)
            if response.status_code >= 400:
                return LMStudioHealth(
                    name=self.provider_name,
                    base_url=self.base_url,
                    model=self.model,
                    available=False,
                    error=f"HTTP {response.status_code} from LM Studio.",
                )
            return LMStudioHealth(
                name=self.provider_name,
                base_url=self.base_url,
                model=self.model,
                available=True,
                error=None,
            )
        except Exception as exc:
            return LMStudioHealth(
                name=self.provider_name,
                base_url=self.base_url,
                model=self.model,
                available=False,
                error=f"LM Studio unavailable: {exc.__class__.__name__}",
            )
