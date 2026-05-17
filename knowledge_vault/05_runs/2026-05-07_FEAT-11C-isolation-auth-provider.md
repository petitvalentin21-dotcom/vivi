---
title: Run Log — FEAT-11C
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-07
tags:
  - vivi
  - mvp
  - run
  - auth
  - securite
---

# Run Log — FEAT-11C — 2026-05-07

## Résumé

Isolation stricte de l'auth VIVI vs auth LM Studio, avec amélioration des erreurs 401 provider et couverture de tests associée.

## Fichiers modifiés

- app/config.py
- app/api/server.py
- app/runtime/status.py
- app/llm/lmstudio.py
- app/web/app.js
- tests/test_config.py
- tests/test_chat_endpoint.py
- tests/test_lmstudio_client.py
- tests/test_runtime_info.py
- tests/test_web_interface.py

## Validation

pytest -q → 69 passed

## Résultat

Isolation stricte VIVI API key / LM Studio API key réussie avec variable `VIVI_LMSTUDIO_API_KEY` dédiée et erreur 401 provider plus lisible.
