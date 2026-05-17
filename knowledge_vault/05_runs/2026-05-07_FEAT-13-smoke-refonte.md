---
title: Run Log — FEAT-13
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
  - smoke
  - validation
---

# Run Log — FEAT-13 — 2026-05-07

## Résumé

Refonte ciblée du smoke local MVP pour valider le parcours complet backend/runtime/knowledge/chat/document sur backend déjà lancé, avec sorties lisibles `[OK]/[WARN]/[FAIL]`, résumé final et code retour non-zéro en cas d'échec critique.

## Fichiers modifiés

- scripts/smoke_backend.py
- tests/test_smoke_backend.py
- README.md

## Validation

pytest -q tests/test_smoke_backend.py → 2 passed ; pytest -q → 79 passed

## Résultat

Smoke backend MVP refondu avec sorties standardisées `[OK]/[WARN]/[FAIL]`, gestion auth et code retour non-zéro en cas d'échec critique.
