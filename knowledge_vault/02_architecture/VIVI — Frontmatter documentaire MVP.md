---
title: VIVI — Frontmatter documentaire MVP
status: active
doc_type: architecture
scope: mvp
llm_index: true
llm_role: architecture
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - obsidian
  - frontmatter
  - rag
  - retrieval
---

# VIVI — Frontmatter documentaire MVP

## Objectif

Standardiser les métadonnées des notes Obsidian utiles à VIVI pour améliorer la lisibilité humaine et le retrieval lexical.

Le standard reste simple. Il décrit le rôle documentaire d'une note sans transformer le vault en système complexe.

## Frontmatter recommandé

```yaml
---
title: Titre explicite et stable
status: draft
doc_type: architecture
scope: mvp
llm_index: true
llm_role: architecture
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - rag
---
```

## Champs

### title

Titre lisible, explicite et stable.

Bon exemple:

- `VIVI MVP — Architecture réelle`

À éviter:

- `Notes`
- `Divers`
- `À trier`

### status

Valeurs recommandées:

- `draft` — brouillon en cours, à utiliser avec prudence.
- `active` — documentation utile et actuelle, mais encore évolutive.
- `validated` — référence validée ou source de vérité.
- `archived` — contenu historique, non prioritaire.

Règles:

- Les documents MVP validés doivent être indexables.
- Les brouillons peuvent être indexés seulement s'ils sont utiles et propres.
- Les archives doivent rester non prioritaires ou non indexées.

### doc_type

Valeurs recommandées:

- `product` — cadrage produit, principes, périmètre.
- `architecture` — architecture cible ou réelle.
- `developer-guide` — runbook, exploitation, diagnostic.
- `decision` — décision structurante.
- `backlog` — tâche, idée, prochaine FEAT.
- `run` — compte rendu d'exécution.
- `generated` — contenu produit automatiquement.
- `archive` — contenu historique.

### scope

Valeurs recommandées:

- `mvp` — utile au MVP actif.
- `post-mvp` — idée ou extension future.
- `legacy` — référence historique VIVI_IA ou ancienne approche.
- `runtime` — état généré, log, index ou donnée d'exécution.

Règles:

- Le scope `mvp` doit rester lisible et maintenable.
- Le scope `post-mvp` ne doit pas être mélangé à l'état runtime réel.
- Le scope `runtime` ne doit pas polluer la documentation produit.

### llm_index

Valeurs:

- `true` — note utile au retrieval lexical.
- `false` — note à exclure ou à faible intérêt pour VIVI.

Règles:

- Les documents MVP validés doivent être indexables.
- Les contenus générés doivent être clairement identifiés avant indexation.
- Les archives doivent être `llm_index: false` ou `llm_priority: low`.
- Les notes brutes, dumps, journaux longs ou brouillons confus doivent être `llm_index: false`.

Compatibilité runtime actuelle:

- Le loader actuel exclut déjà les dossiers `90_generated`, `91_runtime`, `92_inbox` et `99_archive`.
- Le loader comprend `llm_index: false` comme exclusion explicite.
- Le loader comprend aussi `index: false` comme exclusion explicite pour compatibilité.
- `llm_index: true` exprime une intention documentaire, mais ne force pas l'indexation si la note se trouve dans un dossier hors périmètre.
- Les dossiers hors périmètre restent contrôlés par la configuration du loader.
- Pour une exclusion compatible, `llm_index: false` suffit dans le standard actuel; `index: false` reste accepté pour les notes historiques.

```yaml
llm_index: false
```

## Périmètre de dossiers

Le loader RAG MVP indexe les dossiers documentaires suivants:

- `00_product/`
- `01_user_docs/`
- `02_architecture/`
- `03_decisions/`
- `04_backlog/`
- `05_runs/`

Décision: `00_navigation/` reste hors index.

Conséquences:

- les notes de navigation, hubs et taxonomies ne remontent pas directement comme sources RAG ;
- les documents de fond restent les sources privilégiées ;
- les hubs peuvent continuer à pointer vers les documents utiles via liens Obsidian.

### llm_role

Valeurs recommandées:

- `source_of_truth` — source documentaire principale.
- `architecture` — architecture cible ou réelle.
- `developer_guide` — procédures d'exploitation ou de maintenance.
- `product` — vision, périmètre, principes.
- `decision` — décision structurante.
- `backlog` — tâche ou idée priorisable.
- `run_log` — trace d'exécution.
- `generated` — contenu généré.
- `archive` — historique.

Règles:

- Une note doit avoir un rôle principal.
- Les décisions structurantes doivent être faciles à retrouver via `llm_role: decision`.
- Les snapshots générés ne doivent pas devenir source de vérité implicite.

### llm_priority

Valeurs:

- `high` — document à privilégier pour répondre sur le MVP.
- `medium` — document utile mais secondaire.
- `low` — archive, log, brouillon ou contenu de contexte.

Règles:

- `high` est réservé aux documents MVP propres, actuels et maintenus.
- `medium` convient aux guides, backlogs et runs utiles.
- `low` convient aux archives, générés et contenus incomplets.

### updated

Date de dernière mise à jour documentaire au format `YYYY-MM-DD`.

Cette date n'est pas un historique complet. Elle sert seulement à repérer la fraîcheur d'une note.

### tags

Tags courts, stables et utiles au retrieval lexical.

Exemples:

- `vivi`
- `mvp`
- `backend`
- `rag`
- `obsidian`
- `lm-studio`
- `runtime`
- `security`

Règles:

- Préférer peu de tags bien choisis.
- Réutiliser le même vocabulaire pour le même concept.
- Éviter les tags trop génériques comme `note`, `todo`, `misc`.

## Exemples par type de document

### Source de vérité produit

```yaml
---
title: VIVI MVP — Cadrage produit v0.1
status: validated
doc_type: product
scope: mvp
llm_index: true
llm_role: source_of_truth
llm_priority: high
updated: 2026-05-12
tags: [vivi, mvp, produit, local-first]
---
```

### Architecture réelle

```yaml
---
title: VIVI MVP — Architecture réelle
status: active
doc_type: architecture
scope: mvp
llm_index: true
llm_role: architecture
llm_priority: high
updated: 2026-05-12
tags: [vivi, mvp, architecture, fastapi, rag]
---
```

### Run log

```yaml
---
title: Run Log — FEAT-03
status: active
doc_type: run
scope: mvp
llm_index: true
llm_role: run_log
llm_priority: medium
updated: 2026-05-06
tags: [vivi, mvp, run, chat, lm-studio]
---
```

### Archive ou généré

```yaml
---
title: Snapshot généré
status: archived
doc_type: generated
scope: runtime
llm_index: false
index: false
llm_role: generated
llm_priority: low
updated: 2026-05-12
tags: [vivi, generated]
---
```

## Règles de gouvernance

- Les documents MVP validés doivent être indexables.
- Les archives restent non prioritaires ou non indexées.
- Les contenus générés doivent être clairement identifiés.
- Les documents runtime ne doivent pas polluer la documentation produit.
- Les décisions structurantes doivent être faciles à retrouver.
- Le frontmatter ne remplace pas une rédaction claire.
- Une note confuse avec un bon frontmatter reste une mauvaise source RAG.
