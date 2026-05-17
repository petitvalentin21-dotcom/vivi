---
title: Run Log — FEAT Auth bypass localhost
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - run
  - auth
  - localhost
---

# Run Log — FEAT Auth bypass localhost — 2026-05-17

## Résumé

Les requêtes provenant de `127.0.0.1` ou `::1` court-circuitent la vérification de clé API, même quand `auth_enabled = True`. Accès local sans friction, sécurité LAN préservée.

## Fichiers modifiés

- app/api/auth.py
- tests/test_auth.py (nouveau)

## Changements clés

- `require_api_key` injecte désormais `Request` FastAPI pour lire `request.client.host`.
- Si `host in ("127.0.0.1", "::1")` → return immédiat, pas de vérification de clé.
- `tests/test_auth.py` : 8 tests couvrant bypass localhost, clé valide, clé invalide, auth désactivée.

## Validation

- `pytest tests/test_auth.py -q` → 8 passed
- `pytest tests/ -q` → 153 passed

## Résultat

Accès VIVI sans clé en local, clé requise depuis le LAN.
