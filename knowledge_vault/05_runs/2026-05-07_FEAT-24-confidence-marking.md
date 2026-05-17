---
title: Run Log — FEAT-24 Marquage confiance faible RAG
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
  - rag
  - confidence
  - lexical-retriever
---

# Run Log — FEAT-24 Marquage confiance faible RAG — 2026-05-07

## Résumé

Ajout d'un marquage explicite de confiance faible pour les sources RAG lexicales, sans filtrage agressif. Les sources reçoivent `confidence_label` (`normal` ou `low`) et `is_low_confidence` (bool). Le marquage ne filtre pas les résultats.

## Fichiers modifiés

- app/knowledge/sources.py
- app/knowledge/lexical_retriever.py
- app/api/server.py
- tests/test_lexical_retriever.py
- scripts/audit_rag_real_vault.py
- docs/RAG_VALIDATION.md
- docs/RAG_REAL_VAULT_AUDIT.md

## Règle de confiance

- `low` si `score < 3.0` ou `score < 35%` du meilleur score de la requête.
- `normal` sinon.
- Pas de filtrage — toutes les sources remontent.

## Validation

- `pytest -q` → 98 passed
- `pytest -q tests/test_lexical_retriever.py` → 9 passed
- `pytest -q tests/test_rag_validation.py` → 5 passed
- Audit réel vault relancé → sources fortes restent `normal`, cas bruités marqués `low`

## Résultat

Succès. Le marquage `low` n'était pas encore affiché dans l'IHM au moment de cette FEAT.

## Note

FEAT-24 a été enregistrée deux fois dans tmp/ (même label, contenu différent). Ce fichier correspond au premier rapport (confidence marking). Le second rapport FEAT-24 (documentation LAN) est dans `2026-05-07_FEAT-24-lan-doc.md`.
