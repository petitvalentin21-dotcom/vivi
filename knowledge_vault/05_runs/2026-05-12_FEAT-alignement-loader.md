---
title: Run Log — FEAT Alignement loader RAG
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - run
  - rag
  - loader
  - frontmatter
---

# Run Log — FEAT Alignement loader RAG — 2026-05-12

## Résumé

Alignement du loader Markdown RAG sur le standard frontmatter documentaire MVP.

## Fichiers modifiés

- app/knowledge/markdown_loader.py
- tests/test_knowledge_loader.py
- knowledge_vault/01_user_docs/VIVI_OBSIDIAN_RAG_GOVERNANCE.md
- knowledge_vault/02_architecture/VIVI — Frontmatter documentaire MVP.md

## Changements clés

- `llm_index: false` reconnu comme exclusion stricte équivalente à `index: false`.
- `llm_index: true` n'écrase pas l'exclusion par dossier.
- `00_navigation/` confirmé hors index.

## Validation

- `pytest -q tests/test_knowledge_loader.py tests/test_lexical_retriever.py tests/test_knowledge_search_endpoint.py tests/test_rag_validation.py` → 26 passed

## Résultat

Standard frontmatter entièrement honoré par le loader.
