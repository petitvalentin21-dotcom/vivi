---
title: Run Log — FEAT-04
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
  - rag
  - obsidian
---

# Run Log — FEAT-04 — 2026-05-06

## Résumé

Implémentation du RAG Obsidian lexical minimal (loader + chunker + retriever) et de l'endpoint `GET /knowledge/search`, avec tests dédiés et sans brancher le RAG à `POST /chat`.

## Fichiers modifiés

- app/knowledge/markdown_loader.py
- app/knowledge/chunker.py
- app/knowledge/lexical_retriever.py
- app/knowledge/sources.py
- app/knowledge/__init__.py
- app/api/server.py
- app/api/schemas.py
- README.md
- tests/test_knowledge_loader.py (créé)
- tests/test_lexical_retriever.py (créé)
- tests/test_knowledge_search_endpoint.py (créé)

## Validation

pytest -q → 44 passed

## Résultat

RAG Obsidian lexical MVP opérationnel avec endpoint `GET /knowledge/search` et tests dédiés.
