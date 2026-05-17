---
title: Run Log — Extension FEAT-19
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
  - markdown
---

# Run Log — Extension FEAT-19 — 2026-05-07

## Résumé

Extension frontend FEAT-19 : ajout d'un rendu Markdown léger et sécurisé pour les réponses VIVI dans la conversation, sans dépendance externe, sans changement backend, prompt ou provider.

## Fichiers modifiés

- app/web/app.js
- app/web/style.css
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 19 passed ; pytest -q → 86 passed

## Résultat

Rendu Markdown léger ajouté pour les réponses VIVI (paragraphes, titres, gras, listes, séparateurs) avec protection XSS via `textContent` et fallback texte brut.
