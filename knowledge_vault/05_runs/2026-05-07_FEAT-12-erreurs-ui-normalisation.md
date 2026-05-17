---
title: Run Log — FEAT-12
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
  - erreurs
---

# Run Log — FEAT-12 — 2026-05-07

## Résumé

Uniformisation légère des erreurs UI MVP dans `app/web/app.js` avec normalisation centralisée et messages courts cohérents, sans changement backend.

## Fichiers modifiés

- app/web/app.js
- app/web/index.html
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 13 passed ; pytest -q complet → 1 échec hors périmètre (valeurs config non neutres, corrigé en FEAT-12B)

## Résultat

Couche de normalisation frontend des erreurs UI ajoutée avec messages lisibles et déterministes pour tous les cas d'erreur MVP.
