from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    local_first: bool


class ProviderInfo(BaseModel):
    name: str
    base_url: str
    model: str
    available: bool
    error: str | None = None


class VaultInfo(BaseModel):
    path: str
    exists: bool
    notes_count: int
    indexed: bool
    error: str | None = None


class SessionsInfo(BaseModel):
    enabled: bool
    store_path: str


class RagInfo(BaseModel):
    enabled: bool
    mode: str
    top_k: int


class RuntimeInfoResponse(BaseModel):
    service: str
    version: str
    local_first: bool
    auth_enabled: bool
    provider: ProviderInfo
    vault: VaultInfo
    sessions: SessionsInfo
    rag: RagInfo
    external_providers_enabled: bool
