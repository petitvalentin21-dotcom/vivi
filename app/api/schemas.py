from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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
    model_configured: bool
    model_available: bool | None = None
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


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    mode: str = "chat"
    use_rag: bool | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    max_sources: int | None = None


class ChatProviderInfo(BaseModel):
    name: str
    model: str


class ChatRuntimeInfo(BaseModel):
    rag_used: bool = False
    sources_count: int = 0
    external_call_used: bool = False


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    provider: ChatProviderInfo
    mode: str
    sources: list[Any] = Field(default_factory=list)
    runtime: ChatRuntimeInfo
    error: dict[str, Any] | None = None


class KnowledgeSearchResult(BaseModel):
    source_id: str
    path: str
    title: str
    section: str
    score: float
    excerpt: str
    chunk_text: str
    confidence_label: str = "unknown"
    is_low_confidence: bool = False


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]
    count: int
    mode: str


class ObsidianInboxCreateRequest(BaseModel):
    title: str
    body: str
    note_type: str = "generated_note"
    status: str = "draft"
    related: list[str] | None = None
    prompt_summary: str | None = None
    confidence: str | None = None
    source_paths: list[str] | None = None


class ObsidianInboxCreateResponse(BaseModel):
    created: bool
    relative_path: str
    filename: str
    note_type: str
    status: str
    index: bool
    review_required: bool
