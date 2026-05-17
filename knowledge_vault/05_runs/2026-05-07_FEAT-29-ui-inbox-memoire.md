---
title: Run Log — FEAT-29
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
  - inbox
---

# Run Log — FEAT-29 — 2026-05-07

## Résumé

Ajout du panneau UI secondaire `Mémoire VIVI` pour capturer explicitement une information ou une proposition d'amélioration vers Obsidian Inbox via `POST /obsidian/inbox`.

## Fichiers modifiés

- app/web/index.html
- app/web/app.js
- app/web/style.css
- tests/test_web_interface.py
- docs/OBSIDIAN_INBOX.md

## Validation

pytest -q tests/test_web_interface.py → 28 passed ; pytest -q → 135 passed

## Résultat

Panneau `Mémoire VIVI` ajouté en `<details>` natif secondaire avec deux actions explicites : mémoriser une information et proposer une amélioration, sans écriture automatique.
