---
title: VIVI — Gouvernance Obsidian et qualité retrieval
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
  - obsidian
  - rag
  - retrieval
  - frontmatter
---

# VIVI — Gouvernance Obsidian & qualité retrieval

## Objectif

Maximiser la qualité du retrieval lexical MVP avec des notes claires, chunkables et sourceables.

## Conventions frontmatter recommandées

Référence actuelle:

- [[02_architecture/VIVI — Frontmatter documentaire MVP]]

Le standard documentaire VIVI MVP utilise `llm_index` pour exprimer l'intention d'indexation. Le runtime comprend désormais `llm_index: false` comme exclusion stricte, équivalente à `index: false`.

```yaml
---
title: Titre explicite
status: draft | active | validated | archived
doc_type: product | architecture | developer-guide | decision | backlog | run | generated | archive
scope: mvp | post-mvp | legacy | runtime
llm_index: true
llm_role: source_of_truth | architecture | developer_guide | product | decision | backlog | run_log | generated | archive
llm_priority: high | medium | low
updated: 2026-05-12
tags: [vivi, mvp, backend]
index: true
---
```

Règles:

- `llm_index: false` exclut la note du retrieval.
- `index: false` exclut la note du retrieval.
- `index: false` reste supporté pour compatibilité.
- `llm_index: true` exprime une intention documentaire, mais ne force pas l'indexation si la note se trouve dans un dossier hors périmètre.
- Les dossiers hors périmètre restent contrôlés par la configuration du loader.
- `title` doit être descriptif et stable.
- `tags` courts et normalisés.

## Bonnes pratiques rédactionnelles

- Un document = un rôle principal.
- Titres H1/H2 explicites.
- Sections courtes et thématiques.
- Éviter paragraphes massifs.
- Nommer endpoints, variables et chemins réels.
- Ajouter exemples concrets plutôt que prose vague.

## Ce qui améliore le retrieval

- mots métier répétés de façon naturelle ;
- présence de termes API exacts (`/chat`, `runtime/info`) ;
- frontmatter propre ;
- sections spécialisées (architecture, tests, sécurité) ;
- absence d'ambiguïté terminologique.

## Ce qui dégrade le retrieval

- documents fourre-tout ;
- titres génériques (`Notes`, `Divers`) ;
- duplication non contrôlée ;
- vocabulaire instable pour un même concept ;
- informations futures non implémentées mêlées à l'état réel ;
- markdown non structuré.

## Stratégie de chunking compatible MVP

- chunking par sections markdown prioritaire ;
- chunks courts autoportants ;
- conserver contexte minimal (titre + section + chemin) ;
- éviter listes gigantesques non segmentées.

## Exclusions recommandées

Exclure de l'index via `llm_index: false`, `index: false` ou zone dédiée:

- brouillons bruyants ;
- dumps runtime volumineux ;
- archives historiques non opérationnelles ;
- contenus incomplets sans statut.

## Dossiers indexés

Le loader indexe les dossiers documentaires de fond du MVP:

- `00_product/`
- `01_user_docs/`
- `02_architecture/`
- `03_decisions/`
- `04_backlog/`
- `05_runs/`

Décision actuelle: `00_navigation/` reste hors index.

Raison:

- les hubs, taxonomies et cartes de navigation peuvent polluer les réponses ;
- les documents restent accessibles par liens Obsidian depuis les hubs indexés ;
- le retrieval lexical doit privilégier les documents de fond comme sources.

## Niveaux de trust documentaire

- `validated`: utilisable comme source forte.
- `draft`: exploitable avec prudence.
- `archive`: référence historique, faible priorité.

## Anti-patterns documentaires

- annoncer des features non codées ;
- conserver des décisions contradictoires sans statut ;
- multiplier les hubs sans maintenance ;
- transformer `90_generated/` en source de vérité implicite.
