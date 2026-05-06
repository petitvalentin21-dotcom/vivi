from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class SmokeResult:
    health_ok: bool
    runtime_ok: bool
    knowledge_ok: bool
    chat_ok: bool
    document_ok: bool
    provider_available: bool

    @property
    def success(self) -> bool:
        essential_ok = self.health_ok and self.runtime_ok
        chat_checks_ok = self.chat_ok and self.document_ok
        return essential_ok and (chat_checks_ok or not self.provider_available)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test VIVI backend against a running API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--message", default="Bonjour VIVI, réponds en une phrase.")
    parser.add_argument(
        "--document-message",
        default="Quels sont les objectifs du MVP ?",
    )
    parser.add_argument("--knowledge-query", default="mvp")
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--skip-document", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--verbose", action="store_true")
    return parser


def _request_json(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    json_payload: dict | None = None,
    params: dict | None = None,
) -> tuple[bool, int | None, dict | None, str | None]:
    try:
        response = client.request(method, path, json=json_payload, params=params)
    except httpx.RequestError as exc:
        return False, None, None, str(exc)

    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = None

    if 200 <= response.status_code < 300:
        return True, response.status_code, payload, None
    return False, response.status_code, payload, f"HTTP {response.status_code}"


def run_smoke(args: argparse.Namespace) -> SmokeResult:
    headers: dict[str, str] = {}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    with httpx.Client(base_url=args.base_url.rstrip("/"), headers=headers, timeout=args.timeout) as client:
        health_ok, _, health_payload, health_err = _request_json(client, "GET", "/health")
        runtime_ok, _, runtime_payload, runtime_err = _request_json(client, "GET", "/runtime/info")

        provider_name = "unknown"
        provider_available = False
        model_configured = "unknown"
        if runtime_payload and isinstance(runtime_payload, dict):
            provider = runtime_payload.get("provider", {})
            vault = runtime_payload.get("vault", {})
            provider_name = str(provider.get("name", "unknown"))
            provider_available = bool(provider.get("available", False))
            model_configured = provider.get("model", "")
            vault_exists = bool(vault.get("exists", False))
            notes_count = int(vault.get("notes_count", 0))
        else:
            vault_exists = False
            notes_count = 0

        knowledge_ok, _, _, knowledge_err = _request_json(
            client,
            "GET",
            "/knowledge/search",
            params={"q": args.knowledge_query, "top_k": 3},
        )

        chat_ok = args.skip_chat
        chat_err = None
        if not args.skip_chat:
            chat_ok, _, chat_payload, chat_err = _request_json(
                client,
                "POST",
                "/chat",
                json_payload={"message": args.message, "mode": "chat"},
            )
            if chat_ok and isinstance(chat_payload, dict):
                external_call_used = bool(chat_payload.get("runtime", {}).get("external_call_used", True))
                if external_call_used:
                    chat_ok = False
                    chat_err = "external_call_used is not false on mode=chat"

        document_ok = args.skip_document
        document_err = None
        document_sources_count = 0
        if not args.skip_document:
            document_ok, _, document_payload, document_err = _request_json(
                client,
                "POST",
                "/chat",
                json_payload={
                    "message": args.document_message,
                    "mode": "document",
                },
            )
            if document_ok and isinstance(document_payload, dict):
                runtime = document_payload.get("runtime", {})
                external_call_used = bool(runtime.get("external_call_used", True))
                document_sources_count = int(runtime.get("sources_count", 0))
                if external_call_used:
                    document_ok = False
                    document_err = "external_call_used is not false on mode=document"

        print(f"health: {'OK' if health_ok else 'FAIL'}")
        print(f"runtime_info: {'OK' if runtime_ok else 'FAIL'}")
        print(f"provider_name: {provider_name}")
        print(f"provider_available: {provider_available}")
        print(f"model_configured: {model_configured if model_configured else '(empty)'}")
        print(f"vault_exists: {vault_exists}")
        print(f"notes_count: {notes_count}")
        print(f"knowledge_search: {'OK' if knowledge_ok else 'FAIL'}")
        print(f"chat_simple: {'OK' if chat_ok else 'FAIL'}")
        print(f"document_chat: {'OK' if document_ok else 'FAIL'}")
        print(f"document_sources_count: {document_sources_count}")

        if args.verbose:
            if health_err:
                print(f"health_error: {health_err}")
            if runtime_err:
                print(f"runtime_error: {runtime_err}")
            if knowledge_err:
                print(f"knowledge_error: {knowledge_err}")
            if chat_err:
                print(f"chat_error: {chat_err}")
            if document_err:
                print(f"document_error: {document_err}")

        if runtime_ok and not provider_available and (not args.skip_chat or not args.skip_document):
            print("info: LM Studio indisponible. Les checks chat/document nécessitent LM Studio actif.")

        return SmokeResult(
            health_ok=health_ok,
            runtime_ok=runtime_ok,
            knowledge_ok=knowledge_ok,
            chat_ok=chat_ok,
            document_ok=document_ok,
            provider_available=provider_available,
        )


def main() -> int:
    args = _build_parser().parse_args()
    result = run_smoke(args)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
