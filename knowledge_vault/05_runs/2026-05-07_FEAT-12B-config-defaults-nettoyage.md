---
title: Run Log — FEAT-12B
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
  - config
  - nettoyage
---

# Run Log — FEAT-12B — 2026-05-07

## Résumé

Nettoyage de la configuration MVP: suppression des valeurs codées en dur non neutres, alignement des defaults sur un mode local-first sûr, et validation complète des tests.

## Fichiers modifiés

- app/config.py
- tests/test_config.py
- README.md

## Validation

pytest -q → 72 passed

## Résultat

Configuration MVP nettoyée avec defaults neutres (clés vides, modèle vide, URL LM Studio alignée sur `http://127.0.0.1:1234`) et suite de tests complète au vert.
