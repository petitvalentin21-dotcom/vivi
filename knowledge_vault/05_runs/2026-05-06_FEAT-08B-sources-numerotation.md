---
title: Run Log — FEAT-08B
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
  - sources
---

# Run Log — FEAT-08B — 2026-05-06

## Résumé

Correction ciblée du rendu des numéros de sources dans l'interface web: suppression de la dépendance à la numérotation implicite des listes HTML, remplacement par un label explicite `Source N` généré côté frontend.

## Fichiers modifiés

- app/web/index.html
- app/web/app.js
- tests/test_web_interface.py

## Validation

pytest -q → 56 passed

## Résultat

Numérotation des sources corrigée avec label explicite `Source N` généré côté frontend, éliminant la double numérotation possible selon le navigateur.
