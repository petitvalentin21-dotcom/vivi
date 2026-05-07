from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class SmokeResult:
    ok_count: int
    warn_count: int
    fail_count: int
    auth_enabled: bool
    provider_available: bool
    model_configured: bool
    knowledge_ok: bool
    chat_ok: bool
    document_ok: bool
    document_sources_count: int

    @property
    def success(self) -> bool:
        return self.fail_count == 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test VIVI backend against a running API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--api-key", default=os.getenv("VIVI_API_KEY", "") or None)
    parser.add_argument("--message", default="Bonjour VIVI, réponds en une phrase.")
    parser.add_argument("--document-message", default="Quelle est ton architecture ?")
    parser.add_argument("--knowledge-query", default="architecture")
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


def _print_check(level: str, label: str, detail: str | None = None) -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"[{level}] {label}{suffix}")


def _error_code(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return ""
    err = payload.get("error")
    if not isinstance(err, dict):
        return ""
    return str(err.get("code", "")).strip()


def _error_message(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return ""
    err = payload.get("error")
    if not isinstance(err, dict):
        return ""
    return str(err.get("message", "")).strip()


def run_smoke(args: argparse.Namespace) -> SmokeResult:
    ok_count = 0
    warn_count = 0
    fail_count = 0

    base_headers: dict[str, str] = {}
    if args.api_key:
        base_headers["Authorization"] = f"Bearer {args.api_key}"

    with httpx.Client(base_url=args.base_url.rstrip("/"), headers=base_headers, timeout=args.timeout) as client:
        health_ok, _, health_payload, health_err = _request_json(client, "GET", "/health")
        if health_ok and isinstance(health_payload, dict) and str(health_payload.get("status", "")).lower() == "ok":
            ok_count += 1
            _print_check("OK", "health")
        else:
            fail_count += 1
            _print_check("FAIL", "health", health_err or "backend non accessible")

        runtime_ok, runtime_status, runtime_payload, runtime_err = _request_json(client, "GET", "/runtime/info")
        auth_enabled = False
        provider_name = "unknown"
        provider_available = False
        provider_model = ""
        vault_exists = False
        notes_count = 0
        model_configured = False

        if runtime_ok and isinstance(runtime_payload, dict):
            auth_enabled = bool(runtime_payload.get("auth_enabled", False))
            provider = runtime_payload.get("provider", {})
            vault = runtime_payload.get("vault", {})
            if isinstance(provider, dict):
                provider_name = str(provider.get("name", "unknown"))
                provider_available = bool(provider.get("available", False))
                provider_model = str(provider.get("model", "")).strip()
            if isinstance(vault, dict):
                vault_exists = bool(vault.get("exists", False))
                notes_count = int(vault.get("notes_count", 0) or 0)
            model_configured = bool(provider_model)

            ok_count += 1
            _print_check(
                "OK",
                "runtime",
                f"auth_enabled={auth_enabled} provider={provider_name} model={provider_model or '(non configuré)'} "
                f"provider_available={provider_available} vault_exists={vault_exists} notes_count={notes_count}",
            )
        else:
            fail_count += 1
            _print_check("FAIL", "runtime", runtime_err or f"HTTP {runtime_status}")

        if auth_enabled and not args.api_key:
            fail_count += 1
            _print_check("FAIL", "auth", "auth activée mais clé absente. Fournir --api-key (ou VIVI_API_KEY).")

        if runtime_ok and not model_configured:
            fail_count += 1
            _print_check("FAIL", "model missing", "configurer VIVI_LMSTUDIO_MODEL puis redémarrer le backend.")

        if runtime_ok and not provider_available:
            fail_count += 1
            _print_check(
                "FAIL",
                "provider unavailable",
                "lancer LM Studio Local Server avec le modèle chargé.",
            )

        knowledge_ok, _, knowledge_payload, knowledge_err = _request_json(
            client,
            "GET",
            "/knowledge/search",
            params={"q": args.knowledge_query, "top_k": 3},
        )
        if knowledge_ok and isinstance(knowledge_payload, dict):
            ok_count += 1
            count = int(knowledge_payload.get("count", 0) or 0)
            _print_check("OK", "knowledge search", f"count={count}")
        else:
            fail_count += 1
            _print_check("FAIL", "knowledge search", knowledge_err or "réponse invalide")

        chat_ok = args.skip_chat
        if args.skip_chat:
            _print_check("WARN", "chat", "skipped")
            warn_count += 1
        else:
            chat_ok, _, chat_payload, chat_err = _request_json(
                client,
                "POST",
                "/chat",
                json_payload={"message": args.message, "mode": "chat"},
            )
            if chat_ok and isinstance(chat_payload, dict):
                answer = str(chat_payload.get("answer", "")).strip()
                runtime = chat_payload.get("runtime", {})
                rag_used = bool(runtime.get("rag_used", True)) if isinstance(runtime, dict) else True
                sources = chat_payload.get("sources", [])
                if answer and not rag_used and (isinstance(sources, list) and len(sources) == 0):
                    ok_count += 1
                    _print_check("OK", "chat")
                else:
                    fail_count += 1
                    _print_check("FAIL", "chat", "réponse invalide (answer/rag_used/sources).")
            else:
                fail_count += 1
                detail = chat_err or f"{_error_code(chat_payload)} {_error_message(chat_payload)}".strip()
                _print_check("FAIL", "chat", detail or "échec requête")

        document_ok = args.skip_document
        document_sources_count = 0
        if args.skip_document:
            _print_check("WARN", "document chat", "skipped")
            warn_count += 1
        else:
            document_ok, _, document_payload, document_err = _request_json(
                client,
                "POST",
                "/chat",
                json_payload={"message": args.document_message, "mode": "document"},
            )
            if document_ok and isinstance(document_payload, dict):
                answer = str(document_payload.get("answer", "")).strip()
                runtime = document_payload.get("runtime", {})
                rag_used = bool(runtime.get("rag_used", False)) if isinstance(runtime, dict) else False
                sources = document_payload.get("sources", [])
                if not isinstance(sources, list):
                    sources = []
                document_sources_count = len(sources)
                if answer and rag_used:
                    ok_count += 1
                    _print_check("OK", "document chat")
                    if document_sources_count == 0:
                        warn_count += 1
                        _print_check("WARN", "document chat returned no sources")
                    else:
                        for idx, src in enumerate(sources[:3], start=1):
                            title = str(src.get("title") or src.get("section") or "source")
                            path = str(src.get("path", ""))
                            score = src.get("score", "n/a")
                            _print_check("OK", f"source {idx}", f"title={title} path={path} score={score}")
                else:
                    fail_count += 1
                    _print_check("FAIL", "document chat", "réponse invalide (answer/rag_used).")
            else:
                fail_count += 1
                detail = document_err or f"{_error_code(document_payload)} {_error_message(document_payload)}".strip()
                _print_check("FAIL", "document chat", detail or "échec requête")

        print(f"Summary: ok={ok_count} warn={warn_count} fail={fail_count}")

        if args.verbose:
            if health_err:
                print(f"debug health_error: {health_err}")
            if runtime_err:
                print(f"debug runtime_error: {runtime_err}")
            if knowledge_err:
                print(f"debug knowledge_error: {knowledge_err}")

        return SmokeResult(
            ok_count=ok_count,
            warn_count=warn_count,
            fail_count=fail_count,
            auth_enabled=auth_enabled,
            provider_available=provider_available,
            model_configured=model_configured,
            knowledge_ok=knowledge_ok,
            chat_ok=chat_ok,
            document_ok=document_ok,
            document_sources_count=document_sources_count,
        )


def main() -> int:
    args = _build_parser().parse_args()
    result = run_smoke(args)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

