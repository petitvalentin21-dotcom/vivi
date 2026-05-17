---
title: Run Log — FEAT-18
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
  - ux
  - sources
---

# Run Log — FEAT-18 — 2026-05-07

## Résumé

Micro-correction UX MVP : amélioration de la lisibilité des sources RAG dans l'IHM sans changement backend, RAG, API ou architecture.

## Fichiers modifiés

- app/web/app.js
- app/web/style.css
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 15 passed ; pytest -q → 81 passed

## Résultat

Sources RAG rendues dans des cartes `article` sémantiques avec `<details open>` natif pour l'extrait, numérotation et accessibilité clavier conservées.
