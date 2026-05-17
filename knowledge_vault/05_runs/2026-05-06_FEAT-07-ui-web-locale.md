---
title: Run Log — FEAT-07
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-06
tags:
  - vivi
  - mvp
  - run
  - ui
  - frontend
---

# Run Log — FEAT-07 — 2026-05-06

## Résumé

Ajout d'une interface web locale MVP simple servie par FastAPI, connectée aux endpoints backend existants (`/runtime/info`, `/chat`) avec support des modes `chat` et `document`, affichage des sources et erreurs lisibles.

## Fichiers modifiés

- app/api/server.py
- README.md
- app/web/index.html (créé)
- app/web/style.css (créé)
- app/web/app.js (créé)
- tests/test_web_interface.py (créé)

## Validation

pytest -q → 55 passed

## Résultat

Interface web locale MVP opérationnelle, servie par FastAPI, avec chat/document, sources visibles et erreurs lisibles.
