---
title: Run Log — FEAT Vault nutrition + CLAUDE.md
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - run
  - vault
  - nutrition
  - claude-code
---

# Run Log — FEAT Vault nutrition + CLAUDE.md — 2026-05-17

## Résumé

Création de la zone vault `10_nutrition/` (indexée dans le RAG), initialisation de deux notes de profil personnel, et ajout du fichier `CLAUDE.md` à la racine pour instruire Claude Code automatiquement à chaque session.

## Fichiers modifiés

- app/knowledge/markdown_loader.py
- CLAUDE.md (nouveau)
- AGENTS.md
- knowledge_vault/10_nutrition/profil-nutrition.md (nouveau)
- knowledge_vault/10_nutrition/batch-cooking-preferences.md (nouveau)

## Changements clés

- `_INCLUDED_PREFIXES` dans `markdown_loader.py` : ajout de `"10_nutrition"`.
- `CLAUDE.md` : instructions complètes pour Claude Code (identité projet, état MVP, architecture, conventions, hors-MVP).
- `AGENTS.md` : note de redirection → Claude Code utilise `CLAUDE.md`.
- Vault nutrition : deux notes `llm_priority: high`, `doc_type: personal_profile`, indexées.

## Validation

- `pytest tests/ -q` → 153 passed

## Résultat

VIVI peut répondre aux questions nutrition en s'appuyant sur le profil vault. Claude Code charge ses instructions automatiquement sans prompt manuel.
