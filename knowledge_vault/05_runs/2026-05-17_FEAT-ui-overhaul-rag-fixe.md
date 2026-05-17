---
title: Run Log — FEAT UI overhaul RAG fixe
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
  - ui
  - rag
  - markdown
---

# Run Log — FEAT UI overhaul RAG fixe — 2026-05-17

## Résumé

Refonte UI complète : suppression du sélecteur de mode (RAG toujours actif), sources converties en `<details>` fermé par défaut, rendu markdown enrichi (tableaux, blocs de code fencés, code inline), simplification du panneau runtime.

## Fichiers modifiés

- app/web/app.js
- app/web/index.html
- app/web/style.css
- tests/test_web_interface.py

## Changements clés

- Sélecteur `mode` supprimé ; `use_rag: true, mode: "chat"` fixés dans la requête `/chat`.
- Sources : `<section id="sources-panel">` → `<details class="sources-panel hidden">`, fermé par défaut.
- `renderMarkdownLite` : ajout `flushMarkdownTable`, blocs `<pre><code>`, code inline, flush systématique avant chaque nouveau bloc.
- Runtime : grille `meta-grid` → ligne `runtime-meta` compacte.
- Session label : "Session locale" → "Session", inline dans la barre d'actions.
- Textarea : `rows=3`, `resize: vertical`, `min-height: 3.5rem`.
- CSS : styles `table`, `pre`, `code`, `.session-inline`, `.runtime-meta`.

## Validation

- `pytest tests/test_web_interface.py -q` → 35 passed
- `pytest tests/ -q` → 153 passed

## Résultat

UI plus lisible, moins de friction, rendu markdown complet pour les réponses VIVI.
