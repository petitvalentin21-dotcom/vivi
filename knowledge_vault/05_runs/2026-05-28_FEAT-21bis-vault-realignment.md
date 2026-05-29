---
title: Run Log — FEAT-21bis
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-28
tags:
  - vivi
  - mvp
  - run
  - vault
  - documentation
---

## Résumé

FEAT documentaire pure : recalage du vault Obsidian sur la réalité du code après le pivot vers Ollama + modules Repas (FEAT-16 à FEAT-21). 8 notes LM Studio / chat générique archivées, 3 notes pivot créées, `VIVI HOME.md` réécrit. Aucun code Python touché.

## Fichiers créés

- `knowledge_vault/00_product/VIVI_MVP_REPAS_v1.0.md` — source de vérité produit actuelle
- `knowledge_vault/03_decisions/DECISION-pivot-usage-perso.md` — trace du pivot usage perso (24 mai 2026)
- `knowledge_vault/03_decisions/DECISION-base-v1-conservee.md` — trace de la décision Option A + plan FEAT-16→FEAT-30
- `knowledge_vault/99_archive/legacy-mvp-v0/` — sous-dossier créé pour les notes archivées
- `knowledge_vault/05_runs/2026-05-28_FEAT-21bis-vault-realignment.md` — ce run log

## Fichiers modifiés

- `knowledge_vault/VIVI HOME.md` — réécriture complète : nouveau frontmatter, Ollama, modules Repas, liens vers les 3 nouvelles notes pivot, suppression des références LM Studio comme provider actuel

### Notes archivées (déplacées vers `99_archive/legacy-mvp-v0/` + `status: archived` + `llm_index: false`)

- `knowledge_vault/99_archive/legacy-mvp-v0/VIVI_MVP_CADRAGE_v0.1.md` (ex `00_product/`) — cadrage LM Studio / chat générique v0.1
- `knowledge_vault/99_archive/legacy-mvp-v0/VIVI — Backend MVP Spec v0.1.md` (ex `02_architecture/`) — spec backend LM Studio v0.1
- `knowledge_vault/99_archive/legacy-mvp-v0/FEAT-04_backlog_item.md` (ex `04_backlog/`) — backlog FEAT terminée, llm_index corrigé
- `knowledge_vault/99_archive/legacy-mvp-v0/VIVI_MVP_REAL_ARCHITECTURE_MAP.md` (ex `01_user_docs/`) — architecture réelle LM Studio
- `knowledge_vault/99_archive/legacy-mvp-v0/VIVI_DEVELOPER_OPERATIONS_MVP.md` (ex `01_user_docs/`) — runbook LM Studio
- `knowledge_vault/99_archive/legacy-mvp-v0/VIVI_MVP_PRODUCT_OPERATING_PRINCIPLES.md` (ex `01_user_docs/`) — "LM Studio unique provider MVP"
- `knowledge_vault/99_archive/legacy-mvp-v0/DECISION-01_provider-lm-studio-unique.md` (ex `03_decisions/`) — supersédée par Ollama (FEAT-16)
- `knowledge_vault/99_archive/legacy-mvp-v0/DECISION-04_perimetre-mvp-local-first.md` (ex `03_decisions/`) — disait "Ollama = provider externe exclu"

## Notes ambiguës laissées en place — à arbitrer manuellement

- `knowledge_vault/01_user_docs/VIVI_MVP_DOC_HUB.md` — hub de navigation toujours utile structurellement ; mentionne "lm studio provider" comme keyword de retrieval et lie DECISION-01 archivée. À mettre à jour manuellement dans une FEAT ultérieure.
- `knowledge_vault/01_user_docs/Écrire pour VIVI et le RAG.md` — guide rédactionnel toujours valide ; LM Studio n'apparaît qu'en exemples (exemples de titres, de vocabulaire stable). Non archivé car le fond reste correct.

## Vérification `markdown_loader.py`

Aucun changement nécessaire. `_INCLUDED_PREFIXES` et `_EXCLUDED_PARTS` déjà corrects :

```python
_INCLUDED_PREFIXES = {"00_product", "01_user_docs", "02_architecture", "03_decisions", "04_backlog", "05_runs", "10_nutrition"}
_EXCLUDED_PARTS = {".obsidian", "90_generated", "91_runtime", "92_inbox", "99_archive", "tmp", "data"}
```

## Validation

```
pytest tests/ -q
460 passed in 72.36s
```

Check manuel :
- ✅ 8 notes archivées ont `status: archived` et `llm_index: false`
- ✅ 3 notes pivot créées avec `llm_index: true` et frontmatter conforme
- ✅ `VIVI HOME.md` ne mentionne plus LM Studio comme provider actuel
- ✅ `99_archive/` (18 docs Phase 0-4) intact — aucun fichier touché
- ✅ `99_archive/legacy-mvp-v0/` créé avec les 8 notes archivées

## Résultat

Le RAG vault est désormais aligné sur la réalité du code : Ollama comme provider, modules `app/meals/` comme domaine métier, FastAPI + SQLite. La requête `/knowledge/search?query=quel+est+le+mvp+vivi` devrait retourner `VIVI_MVP_REPAS_v1.0` en top 1 plutôt que l'ancien `VIVI_MVP_CADRAGE_v0.1` (devenu invisible — archivé dans une zone exclue).
