---
title: Run Log — FEAT-14
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
  - documentation
---

# Run Log — FEAT-14 — 2026-05-07

## Résumé

Ajout d'un encart d'aide locale MVP visible dans l'IHM pour expliquer rapidement l'usage de VIVI (modes chat/document, sources, LM Studio, actions en cas de modèle indisponible), sans modifier le comportement fonctionnel.

## Fichiers modifiés

- app/web/index.html
- app/web/style.css
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 13 passed ; pytest -q → 79 passed

## Résultat

Encart d'aide contextuelle ajouté dans l'IHM avec explication des modes chat/document, sources et diagnostic LM Studio, sans changement fonctionnel.
