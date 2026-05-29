---
title: Décision — Conservation de la base Vivi v1 (Option A)
status: validated
doc_type: decision
scope: mvp
llm_index: true
llm_role: decision
llm_priority: high
updated: 2026-05-28
tags:
  - vivi
  - décision
  - architecture
  - audit
---

# Décision — Conservation de la base Vivi v1 (Option A)

## Contexte

Après les phases 0–3 (cadrage stratégique, vision produit personnelle, architecture cible), la Phase 4 a audité le repo VIVI v1 existant (branche main, commit `ce02600`).

Date de décision : 25 mai 2026.

## Résultat d'audit

La stack v1 recoupe à environ **80%** la cible Phase 3 :

- Stack minimaliste et saine (FastAPI, Pydantic, httpx, pytest — 6 dépendances).
- Architecture modulaire déjà en place (`app/api/`, `app/llm/`, `app/knowledge/`, `app/sessions/`, `app/runtime/`).
- Philosophie produit documentée et mature (CLAUDE.md de 146 lignes, AGENTS.md de 658 lignes).
- Vault Obsidian (`knowledge_vault/`) comme source de vérité documentaire.
- Conventions claires : workflow Git, tests, sécurité, FEAT-NN.
- Politique stricte hors-scope MVP.

## Décision

**Option A retenue** : continuité avec extension — garder le repo v1 comme base, l'étendre par FEATs ciblées.

Option B (refonte from scratch) et Option C (import VIVI_IA) ont été écartées — refonte non justifiée, complexité VIVI_IA inutile.

## Conséquences et FEATs d'extension

| Évolution | FEAT | État |
|-----------|------|------|
| Remplacement client LM Studio par Ollama dans `app/llm/` | FEAT-16 | ✅ livré |
| Ajout SQLite + SQLModel + Alembic (`app/db/`) | FEAT-17 | ✅ livré |
| Module Recettes (`app/meals/recettes/`) | FEAT-18 | ✅ livré |
| Module Stock (`app/meals/stock/`) | FEAT-19 | ✅ livré |
| Module Courses (`app/meals/courses/`) | FEAT-20 | ✅ livré |
| Module Préférences (`app/meals/preferences/`) | FEAT-21 | ✅ livré |
| Vault realignment (FEAT-21bis) | FEAT-21bis | ✅ livré |
| Tool registry + outils LLM | FEAT-22 | À faire |

## Ce qui a été conservé tel quel

- Stack `requirements.txt`
- Structure `app/` (étendue, pas remplacée)
- Endpoints existants (`/health`, `/runtime/info`, `/chat`, `/knowledge/search`, `/obsidian/inbox`)
- Auth locale par clé API (`VIVI_API_KEY`)
- Politique `.env` / `.env.example`
- Vault Obsidian + politique AI-generated writes → zones dédiées (`90_generated/`, `91_runtime/`, `92_inbox/`)
- Convention FEAT-NN
- Politique Git (pas d'auto-commit, branches sur demande, pas de PR auto)

## Référence historique

Source longue : `99_archive/01-audit-vivi-v1.md` (Phase 4 — audit Vivi v1 et plan d'extension FEAT-16→FEAT-30, validé le 25 mai 2026).
