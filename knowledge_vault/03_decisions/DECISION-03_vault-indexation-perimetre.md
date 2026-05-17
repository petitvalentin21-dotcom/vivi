---
title: Décision — Périmètre d'indexation du vault Obsidian
status: validated
doc_type: decision
scope: mvp
llm_index: true
llm_role: decision
llm_priority: high
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - decision
  - obsidian
  - vault
  - indexation
  - rag
  - llm-index
---

# Décision — Périmètre d'indexation du vault Obsidian

## Contexte

Le vault Obsidian contient plusieurs types de contenus : documentation active, navigation, generated, inbox, runtime, archives. Tous ne doivent pas être injectés dans le RAG. Un périmètre explicite est nécessaire pour éviter que des contenus non validés ou structurellement bruyants polluent les réponses VIVI.

Ces décisions ont été consolidées lors des FEAT Retrieval-first (12/05/2026) et Alignement loader (12/05/2026).

## Décision

Le loader RAG (`app/knowledge/markdown_loader.py`) indexe uniquement les dossiers suivants :

- `00_product/`
- `01_user_docs/`
- `02_architecture/`
- `03_decisions/`
- `04_backlog/`
- `05_runs/`

Les dossiers suivants sont exclus par construction :

- `00_navigation/` — hubs, taxonomies, cartes de navigation. Ne doivent pas remonter comme sources directes.
- `90_generated/` — contenus générés automatiquement, non validés.
- `91_runtime/` — données runtime, index techniques, logs.
- `92_inbox/` — propositions en attente de validation humaine.
- `99_archive/` — contenu historique à faible pertinence.

Le contrôle d'indexation par note est possible via le frontmatter :

- `llm_index: false` — exclut explicitement la note du retrieval, même si elle est dans un dossier indexé.
- `index: false` — alias accepté pour compatibilité avec les notes antérieures au standard.
- `llm_index: true` — exprime une intention documentaire mais ne force pas l'inclusion si la note est dans un dossier hors périmètre.

## Conséquences

- `00_navigation/` reste navigable via liens Obsidian depuis les hubs, sans polluer le RAG.
- Les notes de navigation (taxonomie, hub) restent utiles à l'humain mais ne deviennent pas sources VIVI.
- Les notes brouillons ou générées peuvent être placées dans les dossiers indexés à condition d'avoir `llm_index: false`.
- Le loader est déterministe et ne dépend pas d'un index externe.

## Alternatives écartées

- **Indexer tout le vault sans exclusion** : écarté, risque de remonter des contenus non validés, des archives et des logs comme sources VIVI.
- **Inclure `00_navigation/` dans l'index** : écarté explicitement lors de la FEAT Retrieval-first. Les hubs sont des cartes, pas des sources de fond.
- **Exclure `04_backlog/` et `05_runs/`** : non retenu, ces dossiers contiennent des informations utiles au contexte projet. La sélectivité est gérée par `llm_index` et `llm_priority`.
