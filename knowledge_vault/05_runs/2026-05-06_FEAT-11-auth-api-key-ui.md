---
title: Run Log — FEAT-11
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
  - securite
  - auth
---

# Run Log — FEAT-11 — 2026-05-06

## Résumé

Ajout d'une sécurité MVP légère côté interface web: détection auth_enabled via /runtime/info, saisie locale de clé API (mémoire JS uniquement), envoi du header d'auth sur /chat, et messages d'erreur d'auth lisibles.

## Fichiers modifiés

- app/web/index.html
- app/web/app.js
- app/web/style.css
- tests/test_web_interface.py

## Validation

pytest -q → 58 passed

## Résultat

Sécurité MVP légère ajoutée côté UI avec saisie de clé API locale, envoi du header Authorization et messages d'erreur d'auth lisibles.
