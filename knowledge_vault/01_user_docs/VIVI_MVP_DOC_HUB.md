---
title: VIVI MVP — Hub documentaire
status: active
doc_type: developer-guide
scope: mvp
llm_index: true
llm_role: developer_guide
llm_priority: high
updated: 2026-05-28
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

- [[00_product/VIVI_MVP_REPAS_v1.0]] — vision MVP Repas actuelle, modules, stack, critères d'acceptation.
- [[03_decisions/DECISION-pivot-usage-perso]] — décision pivot usage personnel (24 mai 2026).
- [[03_decisions/DECISION-base-v1-conservee]] — décision conservation base v1 et plan FEAT-16→FEAT-30.

## Architecture et runtime

- [[02_architecture/VIVI — Backend MVP Spec v0.1]] — spécification backend initiale (archivée dans 99_archive/legacy-mvp-v0/).
- Voir `app/api/server.py` et les modules `app/meals/` pour l'architecture réelle.

## Guides MVP

- [[01_user_docs/VIVI_OBSIDIAN_RAG_GOVERNANCE]] — gouvernance documentaire pour améliorer le retrieval.
- [[01_user_docs/Écrire pour VIVI et le RAG]] — guide humain pour rédiger des notes utiles au RAG lexical.
- [[02_architecture/VIVI — Frontmatter documentaire MVP]] — standard frontmatter documentaire MVP.

## Décisions importantes

- [[03_decisions/DECISION-02_rag-lexical-sans-vector-db]] — RAG lexical uniquement, sans vector DB ni embeddings.
- [[03_decisions/DECISION-03_vault-indexation-perimetre]] — Périmètre d'indexation du vault, `llm_index: false`.
- [[03_decisions/DECISION-05_ecriture-obsidian-inbox-validation-humaine]] — Écriture Obsidian limitée à `92_inbox/`, validation humaine obligatoire.
- [[03_decisions/DECISION-06_auth-api-key-locale]] — Auth par clé API locale simple, pas de multi-utilisateur.

## Runs récents

- [[05_runs/2026-05-28_FEAT-21bis-vault-realignment]] — recalage vault sur réalité Ollama + modules Repas.
- [[05_runs/2026-05-17_FEAT-ranking-llm-priority]] — ranking lexical pondéré par llm_priority.

## Archives et générés

- `90_generated/` — snapshots générés, non source de vérité.
- `91_runtime/` — données runtime et index temporaires.
- `92_inbox/` — propositions à relire avant promotion.
- `99_archive/` — archives historiques (docs Phase 0-4, notes legacy LM Studio).

## Index retrieval conseillé

Mots-clés utiles pour recherche lexicale :

- backend fastapi ollama
- endpoint chat repas
- runtime info
- modules recettes stock courses preferences
- auth api key
- rag lexical
- source visibility
- session memory
- obsidian frontmatter
- llm_index
- llm_role
- llm_priority
- local-first

## Statut

- Couverture MVP: élevée.
- Couverture post-MVP: volontairement limitée.
- Références legacy VIVI_IA: exclues du chemin actif.
