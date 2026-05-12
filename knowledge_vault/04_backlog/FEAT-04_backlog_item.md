---
title: FEAT-04 — Backlog RAG Obsidian lexical minimal
status: archived
doc_type: backlog
scope: mvp
llm_index: true
llm_role: backlog
llm_priority: medium
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - backlog
  - rag
  - obsidian
---

# FEAT-04 — Backlog suivant

- ID: FEAT-04
- Titre: RAG Obsidian lexical minimal + endpoint `/knowledge/search`
- Priorité: MVP (assumption: élevée)
- Statut: ready
- Dépendance: FEAT-03 terminé

## Scope cible

- Loader markdown simple
- Retriever lexical explicable
- Contrat sources (path/title/section/score/excerpt)
- Endpoint debug contrôlé `/knowledge/search`
- Tests mockés et unitaires associés

## Hors scope

- Pas de branchage RAG au `/chat` dans FEAT-04
