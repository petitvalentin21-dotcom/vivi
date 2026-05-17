---
title: Run Log — FEAT Ranking lexical llm_priority
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
  - rag
  - retriever
  - llm-priority
  - ranking
---

# Run Log — FEAT Ranking lexical llm_priority — 2026-05-17

## Résumé

Le retriever lexical utilise désormais `llm_priority` comme tie-breaker de tri. À score égal, les sources `high` remontent avant `medium`, et `medium` avant `low`. Le score reste le critère primaire.

## Fichiers modifiés

- app/knowledge/lexical_retriever.py
- tests/test_lexical_retriever.py

## Changements clés

- `_priority_rank(metadata)` : `high` → 0, absent/`medium` → 1, `low` → 2.
- `scored` passe de `list[tuple[float, Source]]` à `list[tuple[float, int, Source]]`.
- Tri : `(-score, priority_rank, path, section, source_id)`.
- `_select_diverse_sources` mis à jour pour déballer le nouveau tuple.

## Validation

- `pytest -q tests/test_knowledge_loader.py tests/test_lexical_retriever.py tests/test_knowledge_search_endpoint.py tests/test_rag_validation.py` → 29 passed (3 nouveaux tests)

## Résultat

Standard frontmatter entièrement consommé par le retriever.

## Note méthode

Premier FEAT développé directement par Claude (sans Codex). Historique migré de tmp/ vers 05_runs/.
