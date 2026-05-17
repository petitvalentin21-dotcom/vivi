---
title: Run Log — FEAT-20
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
  - ui
  - layout
---

# Run Log — FEAT-20 — 2026-05-07

## Résumé

Micro-correction UX frontend : recentrage de l'IHM sur la conversation, avec aide et runtime status repliés par défaut et zone de conversation agrandie.

## Fichiers modifiés

- app/web/index.html
- app/web/style.css
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 21 passed ; pytest -q → 88 passed

## Résultat

IHM recentrée sur la conversation avec aide et runtime en `<details>` repliés par défaut, zone de chat agrandie et priorité DOM à la conversation.
