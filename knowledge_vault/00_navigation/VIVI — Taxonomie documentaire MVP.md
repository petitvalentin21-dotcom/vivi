---
title: VIVI — Taxonomie documentaire MVP
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
  - taxonomie
  - documentation
  - rag
---

# VIVI — Taxonomie documentaire MVP

## Objectif

Décrire simplement le rôle des dossiers du vault Obsidian VIVI pour garder une documentation lisible, indexable et maintenable.

La taxonomie sert à éviter les documents fourre-tout et à protéger le RAG lexical contre les zones bruyantes.

## 00_product

Rôle:

- cadrage produit ;
- vision MVP ;
- périmètre ;
- non-objectifs.

Contenu attendu:

- sources de vérité produit ;
- principes MVP ;
- limites strictes du produit.

Indexation RAG recommandée:

- `llm_index: true`
- `llm_priority: high`
- `llm_role: source_of_truth` ou `product`

Exemples:

- [[00_product/VIVI_MVP_CADRAGE_v0.1]]

Pièges à éviter:

- mélanger roadmap post-MVP et état MVP réel ;
- ajouter des idées non validées comme si elles étaient décidées.

## 01_user_docs

Rôle:

- guides humains ;
- runbooks ;
- documentation d'usage et de maintenance ;
- hubs documentaires.

Contenu attendu:

- guide développeur ;
- guide RAG ;
- hub MVP ;
- architecture réelle vulgarisée.

Indexation RAG recommandée:

- `llm_index: true` pour les guides propres ;
- `llm_priority: high` ou `medium` selon importance.

Exemples:

- [[01_user_docs/VIVI_MVP_DOC_HUB]]
- [[01_user_docs/VIVI_DEVELOPER_OPERATIONS_MVP]]
- [[01_user_docs/Écrire pour VIVI et le RAG]]

Pièges à éviter:

- transformer un guide en journal de toutes les modifications ;
- dupliquer la source de vérité produit.

## 02_architecture

Rôle:

- spécifications techniques ;
- architecture cible ;
- standards documentaires ;
- contrats structurants.

Contenu attendu:

- backend MVP spec ;
- conventions frontmatter ;
- notes d'architecture validées.

Indexation RAG recommandée:

- `llm_index: true`
- `llm_priority: high`
- `llm_role: architecture`

Exemples:

- [[02_architecture/VIVI — Backend MVP Spec v0.1]]
- [[02_architecture/VIVI — Frontmatter documentaire MVP]]

Pièges à éviter:

- documenter des architectures post-MVP comme si elles étaient actives ;
- ajouter des abstractions futures non décidées.

## 03_decisions

Rôle:

- décisions structurantes ;
- arbitrages durables ;
- alternatives écartées.

Contenu attendu:

- notes courtes avec contexte, décision, conséquences et alternatives.

Indexation RAG recommandée:

- `llm_index: true` pour décisions validées ;
- `llm_priority: high` pour décisions MVP structurantes ;
- `llm_role: decision`.

Exemples:

- décision provider LM Studio unique ;
- décision pas de vector DB obligatoire au MVP ;
- décision écriture Obsidian limitée à inbox/generated/runtime.

Pièges à éviter:

- laisser des décisions contradictoires sans statut ;
- confondre proposition et décision validée.

## 04_backlog

Rôle:

- tâches ;
- idées ;
- prochaines FEAT ;
- éléments à prioriser.

Contenu attendu:

- backlog MVP ;
- propositions post-MVP séparées ;
- scope et hors scope.

Indexation RAG recommandée:

- `llm_index: true` pour backlog propre ;
- `llm_priority: medium` par défaut ;
- `llm_role: backlog`.

Exemples:

- [[04_backlog/FEAT-04_backlog_item]]

Pièges à éviter:

- inventer des priorités ;
- mélanger backlog actif, idées futures et décisions.

## 05_runs

Rôle:

- comptes rendus d'exécution ;
- traces de FEAT ;
- validation et risques.

Contenu attendu:

- résumé ;
- fichiers modifiés ;
- tests ;
- résultat ;
- risques ;
- prochaine étape.

Indexation RAG recommandée:

- `llm_index: true` si le run est court et utile ;
- `llm_priority: medium` ou `low` ;
- `llm_role: run_log`.

Exemples:

- [[05_runs/2026-05-06_FEAT-03_run_log]]

Pièges à éviter:

- coller des logs bruts volumineux ;
- copier un historique de conversation complet ;
- laisser un run contredire une architecture mise à jour.

## 90_generated

Rôle:

- contenus générés ;
- snapshots ;
- exports temporaires.

Contenu attendu:

- état généré ;
- synthèse automatique ;
- documents à relire avant promotion.

Indexation RAG recommandée:

- `llm_index: false` par défaut ;
- `index: false` si exclusion runtime explicite nécessaire ;
- `llm_priority: low`;
- `llm_role: generated`.

Exemples:

- [[90_generated/FEAT-03_PROJECT_STATE_2026-05-06]]

Pièges à éviter:

- utiliser un snapshot généré comme source de vérité ;
- dupliquer durablement les notes validées.

## 91_runtime

Rôle:

- données d'exécution ;
- index ;
- logs runtime ;
- fichiers temporaires.

Contenu attendu:

- fichiers produits par le runtime ;
- caches ;
- index techniques.

Indexation RAG recommandée:

- `llm_index: false`
- `index: false`
- dossier exclu du loader actuel.

Exemples:

- index runtime Obsidian ;
- logs locaux ;
- caches.

Pièges à éviter:

- écrire de la documentation produit dans runtime ;
- exposer des chemins privés ou secrets ;
- indexer des dumps.

## 92_inbox

Rôle:

- propositions à relire ;
- captures explicites depuis VIVI ;
- brouillons non validés.

Contenu attendu:

- clarifications ;
- propositions backlog ;
- notes à promouvoir manuellement.

Indexation RAG recommandée:

- `llm_index: false`
- `index: false`
- dossier exclu du loader actuel.

Exemples:

- note de clarification ;
- proposition d'amélioration.

Pièges à éviter:

- traiter une proposition comme une décision ;
- indexer des notes non relues.

## 99_archive

Rôle:

- historique ;
- contenu obsolète ;
- legacy ;
- références non actives.

Contenu attendu:

- anciennes notes ;
- archives VIVI_IA si nécessaires ;
- décisions remplacées.

Indexation RAG recommandée:

- `llm_index: false` par défaut ;
- `llm_priority: low` si indexation nécessaire ;
- `llm_role: archive`.

Exemples:

- archive legacy ;
- ancienne spécification remplacée.

Pièges à éviter:

- mélanger archive et documentation active ;
- laisser une archive répondre avant une source MVP validée.

## Règle de promotion

Une note peut monter de `92_inbox` ou `90_generated` vers une zone active seulement après relecture humaine ou tâche documentaire explicite.

La promotion doit clarifier:

- le statut ;
- le type documentaire ;
- le scope ;
- l'indexation ;
- le rôle LLM ;
- la priorité LLM.
