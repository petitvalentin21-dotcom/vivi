---
title: Run Log — FEAT-23
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
  - rag
  - diversification
---

# Run Log — FEAT-23 — 2026-05-07

## Résumé

Implémentation d'une diversification documentaire ciblée dans le top K du RAG lexical.

## Fichiers modifiés

- app/knowledge/lexical_retriever.py
- tests/test_lexical_retriever.py
- docs/RAG_VALIDATION.md
- docs/RAG_REAL_VAULT_AUDIT.md
- scripts/audit_rag_real_vault.py

## Validation

pytest -q tests/test_lexical_retriever.py → 7 passed ; pytest -q → 96 passed

## Résultat

Diversification documentaire ajoutée avec limite par chemin (`DEFAULT_MAX_CHUNKS_PER_PATH = 2`) et second passage de complétion, sans refonte du scoring lexical.
