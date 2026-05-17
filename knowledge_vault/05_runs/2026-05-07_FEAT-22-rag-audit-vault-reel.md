---
title: Run Log — FEAT-22
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
  - audit
---

# Run Log — FEAT-22 — 2026-05-07

## Résumé

Audit reproductible du RAG lexical sur le vault réel `knowledge_vault/`, sans amélioration du moteur.

## Fichiers modifiés

- scripts/audit_rag_real_vault.py (créé)
- docs/RAG_REAL_VAULT_AUDIT.md (créé)

## Validation

python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5 → passed ; pytest -q → 93 passed

## Résultat

Audit RAG réel disponible sur 15 questions et 5 familles, avec identification des limites principales : redondance documentaire, extraits coupés, docs/ non indexés.
