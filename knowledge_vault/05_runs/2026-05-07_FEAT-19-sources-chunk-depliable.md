---
title: Run Log — FEAT-19
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
  - sources
  - rag
---

# Run Log — FEAT-19 — 2026-05-07

## Résumé

Sources compactes par défaut et extrait complet dépliable : ajout du champ `chunk_text` au contrat source, conservation de `excerpt`, et adaptation de l'IHM pour afficher le contenu complet uniquement dans un `<details>` fermé par défaut.

## Fichiers modifiés

- app/knowledge/sources.py
- app/knowledge/lexical_retriever.py
- app/api/schemas.py
- app/api/server.py
- app/web/app.js
- app/web/style.css
- tests/test_chat_rag_endpoint.py
- tests/test_lexical_retriever.py
- tests/test_web_interface.py

## Validation

pytest -q tests/test_web_interface.py → 15 passed ; pytest -q → 82 passed

## Résultat

Sources compactes par défaut avec chunk complet dépliable via `<details>` natif, et champ `chunk_text` ajouté au contrat source pour exposer le morceau réellement envoyé au LLM.
