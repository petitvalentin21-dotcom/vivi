---
title: Run Log — FEAT-28
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
  - obsidian
  - api
---

# Run Log — FEAT-28 — 2026-05-07

## Résumé

Ajout de l'endpoint API explicite et protégé `POST /obsidian/inbox` pour créer une note de proposition dans `knowledge_vault/92_inbox/`.

## Fichiers modifiés

- app/api/server.py
- app/api/schemas.py
- docs/OBSIDIAN_INBOX.md
- tests/test_obsidian_inbox_api.py (créé)

## Validation

pytest -q tests/test_obsidian_inbox_api.py → 8 passed ; pytest -q → 128 passed

## Résultat

Endpoint `POST /obsidian/inbox` ajouté, protégé par auth API key existante, avec réponse minimale et sécurité chemin stricte héritée de FEAT-27.
