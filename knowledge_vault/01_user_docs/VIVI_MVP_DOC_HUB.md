---
title: VIVI MVP — Hub documentaire
status: active
doc_type: developer-guide
scope: mvp
llm_index: true
llm_role: developer_guide
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - documentation
  - hub
  - navigation
---

# VIVI MVP — Documentation Hub

## But

Ce hub est l'entrée principale de la documentation MVP VIVI.

Il centralise la documentation exploitable pour :

- l'usage humain ;
- la maintenance backend ;
- le retrieval lexical VIVI ;
- les futures passes documentaires.

## Produit

- [[00_product/VIVI_MVP_CADRAGE_v0.1]] — vision et périmètre MVP.
- [[01_user_docs/VIVI_MVP_PRODUCT_OPERATING_PRINCIPLES]] — principes produit et non-objectifs.

## Architecture et runtime

- [[02_architecture/VIVI — Backend MVP Spec v0.1]] — spécification backend cible.
- [[01_user_docs/VIVI_MVP_REAL_ARCHITECTURE_MAP]] — architecture réelle observée dans le code.

## Guides MVP

- [[01_user_docs/VIVI_DEVELOPER_OPERATIONS_MVP]] — runbook dev local, smoke, debug.
- [[01_user_docs/VIVI_OBSIDIAN_RAG_GOVERNANCE]] — gouvernance documentaire pour améliorer le retrieval.
- [[01_user_docs/Écrire pour VIVI et le RAG]] — guide humain pour rédiger des notes utiles au RAG lexical.
- [[02_architecture/VIVI — Frontmatter documentaire MVP]] — standard frontmatter documentaire MVP.
- [[00_navigation/VIVI — Taxonomie documentaire MVP]] — rôles des dossiers du vault.

## Décisions importantes

- [[03_decisions/DECISION-01_provider-lm-studio-unique]] — LM Studio unique, pas de fallback cloud.
- [[03_decisions/DECISION-02_rag-lexical-sans-vector-db]] — RAG lexical uniquement, sans vector DB ni embeddings.
- [[03_decisions/DECISION-03_vault-indexation-perimetre]] — Périmètre d'indexation du vault, `00_navigation/` hors index, `llm_index: false`.
- [[03_decisions/DECISION-04_perimetre-mvp-local-first]] — Périmètre MVP et non-objectifs (multi-agent, Docker, SSE, etc.).
- [[03_decisions/DECISION-05_ecriture-obsidian-inbox-validation-humaine]] — Écriture Obsidian limitée à `92_inbox/`, validation humaine obligatoire.
- [[03_decisions/DECISION-06_auth-api-key-locale]] — Auth par clé API locale simple, pas de multi-utilisateur.

## Backlog MVP

- [[04_backlog/FEAT-04_backlog_item]] — historique backlog initial RAG lexical.

## Runs importants

- [[05_runs/2026-05-06_FEAT-03_run_log]] — trace FEAT-03 chat LM Studio et sessions.

## Archives et générés

- `90_generated/` — snapshots générés, non source de vérité.
- `91_runtime/` — données runtime et index temporaires, à ne pas utiliser comme documentation produit.
- `92_inbox/` — propositions à relire avant promotion.
- `99_archive/` — archives historiques à faible priorité RAG.

## Index retrieval conseillé

Mots-clés utiles pour recherche lexicale :

- backend fastapi
- endpoint chat
- runtime info
- lm studio provider
- auth api key
- rag lexical
- source visibility
- session memory
- obsidian frontmatter
- llm_index
- llm_role
- llm_priority
- llm index false
- smoke tests
- docker

## Statut

- Couverture MVP: élevée.
- Couverture post-MVP: volontairement limitée.
- Références legacy VIVI_IA: exclues du chemin actif.
