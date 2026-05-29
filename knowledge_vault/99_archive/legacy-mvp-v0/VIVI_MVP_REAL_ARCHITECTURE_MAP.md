---
title: VIVI MVP — Architecture réelle
status: archived
doc_type: architecture
scope: mvp
llm_index: false
llm_role: architecture
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - architecture
  - runtime
  - fastapi
  - rag
---

# VIVI MVP — Architecture réelle (code validé)

## Scope

Cette note décrit l'état réellement implémenté du code VIVI MVP.

## Backend runtime

- Framework API: FastAPI (`app/api/server.py`).
- Entrée serveur: `app.api.server:app`.
- UI servie localement: `/` + assets `app/web/`.
- Statut runtime: `GET /runtime/info` construit via `app/runtime/status.py`.

## Endpoints réellement exposés

- `GET /health`
- `GET /runtime/info`
- `GET /knowledge/search`
- `POST /chat`
- `POST /obsidian/inbox`

### Protection API

- `POST /chat` protégé par API key si `VIVI_API_KEY` est défini.
- `POST /obsidian/inbox` protégé par API key si `VIVI_API_KEY` est défini.
- Les endpoints de lecture (`/health`, `/runtime/info`, `/knowledge/search`) restent accessibles pour diagnostic local.

## Flux chat

1. Validation payload (`message`, `mode`, paramètres optionnels).
2. Résolution session (`session_id` existant ou création).
3. Mode `document` => RAG lexical forcé.
4. Chargement notes Markdown du vault.
5. Chunking textuel.
6. Retrieval lexical top-k.
7. Construction prompt système + contexte RAG.
8. Appel LM Studio (`chat/completions`).
9. Sauvegarde messages user/assistant en session.
10. Réponse API avec sources et runtime flags.

## LM Studio provider

Client: `app/llm/lmstudio.py`.

Comportements MVP:

- normalisation base URL (`/v1` compatible) ;
- healthcheck provider ;
- `chat_completion` ;
- erreurs provider mappées en erreurs safe API.

## Sessions

Stockage: `data/runtime/sessions.json` (via `app/sessions/store.py`).

Contenu:

- `session_id`
- timestamps
- messages `{role, content, created_at}`

Politique active:

- mémoire courte pour prompt (`last_messages_for_prompt(limit=4)`)
- session inspectable/supprimable côté store.

## RAG lexical

Modules:

- loader markdown: `app/knowledge/markdown_loader.py`
- chunker: `app/knowledge/chunker.py`
- retriever: `app/knowledge/lexical_retriever.py`
- schéma source: `app/knowledge/sources.py`

Caractéristiques:

- scoring lexical explicable (titre/path/tags/section/content) ;
- diversification par chemin (`max_chunks_per_path`) ;
- label de confiance (`normal` / `low`) ;
- exposé via `/knowledge/search` et `sources` de `/chat`.

## Runtime observabilité

`/runtime/info` expose:

- service/version/local_first ;
- auth activée ;
- provider status (sans secret) ;
- statut vault + notes_count ;
- statut session store ;
- statut RAG ;
- drapeau providers externes.

## UI MVP

Fichiers:

- `app/web/index.html`
- `app/web/app.js`
- `app/web/style.css`

Capacités visibles:

- chat local ;
- mode chat/document ;
- affichage runtime ;
- affichage sources ;
- reset conversation ;
- erreurs lisibles.

## Docker / exécution

Référence actuelle d'exploitation: `docs/MVP_LOCAL_RELEASE.md`.

Aucune orchestration multi-service complexe requise pour l'usage MVP local.

## Limites volontaires confirmées

Non implémenté volontairement:

- multi-provider routing ;
- fallback cloud ;
- agents spécialisés ;
- vector DB / embeddings obligatoires ;
- orchestrateur complexe.
