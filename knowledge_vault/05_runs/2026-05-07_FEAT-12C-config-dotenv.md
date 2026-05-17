---
title: Run Log — FEAT-12C
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
  - dotenv
---

# Run Log — FEAT-12C — 2026-05-07

## Résumé

Ajout d'un chargement local `.env` MVP au démarrage de la config, avec priorité stricte aux variables d'environnement système et sans exposition de secrets.

## Fichiers modifiés

- app/config.py
- tests/test_config.py
- README.md
- requirements.txt

## Validation

pytest -q tests/test_config.py → 5 passed ; pytest -q → 74 passed

## Résultat

Chargement local `.env` ajouté sans dépendance externe, avec priorité système stricte et isolation dans les tests.
