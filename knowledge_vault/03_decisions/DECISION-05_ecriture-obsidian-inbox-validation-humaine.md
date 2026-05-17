---
title: Décision — Écriture Obsidian limitée à l'inbox, validation humaine obligatoire
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
  - inbox
  - ecriture
  - gouvernance
  - validation
---

# Décision — Écriture Obsidian limitée à l'inbox, validation humaine obligatoire

## Contexte

VIVI a accès au vault Obsidian en lecture (RAG) et peut écrire via l'endpoint `POST /obsidian/inbox`. La gouvernance de cette écriture est critique : les notes sources (architecture, décisions, produit) ne doivent jamais être modifiées automatiquement.

Cette décision a été posée lors de FEAT-25 (audit vault, 07/05/2026) et formalisée lors de FEAT-26 (gouvernance écriture, 07/05/2026), puis implémentée dans FEAT-28 (`POST /obsidian/inbox`) et FEAT-29 (panneau Mémoire VIVI).

## Décision

Principe directeur : VIVI propose, l'utilisateur valide. Les notes sources restent humaines et protégées.

VIVI ne peut écrire que dans `knowledge_vault/92_inbox/`, et uniquement sur action explicite de l'utilisateur (via le panneau "Mémoire VIVI" dans l'IHM ou appel API direct).

Toute note créée dans `92_inbox/` est non indexée par défaut (`index: false`, `review_required: true`). Elle ne participe pas au RAG tant qu'elle n'a pas été validée et promue manuellement par l'utilisateur.

Les zones interdites à toute écriture automatique VIVI :

- `00_product/`
- `01_user_docs/`
- `02_architecture/`
- `03_decisions/`
- `04_backlog/`
- `05_runs/`
- `99_archive/`
- `.obsidian/`
- toutes les notes sources existantes.

## Conséquences

- `POST /obsidian/inbox` est le seul endpoint d'écriture Obsidian exposé.
- L'écriture est protégée par `VIVI_API_KEY` (même mécanisme que `/chat`).
- La réponse API ne renvoie pas le contenu complet de la note créée.
- Aucune indexation automatique n'est déclenchée après écriture.
- Aucune promotion automatique, validation automatique ou cycle de vie automatisé n'existe.
- Le workflow de validation reste humain : l'utilisateur lit, édite si besoin, et déplace la note dans le dossier approprié.

## Alternatives écartées

- **Écriture automatique après chaque chat** : écarté, risque de pollution du vault avec des synthèses non relues.
- **Écriture directe dans les dossiers sources** : écarté, risque de modifier ou d'effacer une source de vérité validée.
- **Indexation automatique des notes inbox** : écarté, une note non validée ne doit pas devenir source RAG.
- **Cycle de vie entièrement automatisé** : post-MVP uniquement, si le volume de notes le justifie.
