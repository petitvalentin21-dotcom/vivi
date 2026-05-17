---
title: Décision — Provider LM Studio unique, pas de fallback cloud
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
  - lm-studio
  - provider
  - local-first
---

# Décision — Provider LM Studio unique, pas de fallback cloud

## Contexte

Le projet VIVI est local-first. Le choix du provider LLM est structurant : il détermine l'architecture du client, les erreurs possibles, la configuration et la philosophie du produit.

Cette décision a été posée dès FEAT-01 (06/05/2026) et renforcée à chaque FEAT suivante.

## Décision

LM Studio est le seul provider LLM du MVP VIVI.

Aucun fallback cloud n'est ajouté. Aucun provider externe (OpenAI, Ollama, Mammouth.ai) n'est activé par défaut.

Si LM Studio est indisponible, le backend répond avec une erreur safe (`lmstudio_unavailable`) mais continue de fonctionner sur les autres endpoints.

La base URL LM Studio (`VIVI_LMSTUDIO_BASE_URL`) accepte les deux formes : `http://127.0.0.1:1234` et `http://127.0.0.1:1234/v1`. La normalisation `/v1` est gérée automatiquement côté client.

## Conséquences

- Le client LM Studio (`app/llm/lmstudio.py`) est le seul module LLM actif.
- Les erreurs provider sont toutes prefixées `lmstudio_*` et ne fuient pas de secret.
- Le runtime info (`GET /runtime/info`) reflète l'état de LM Studio sans exposer la clé API LM Studio.
- L'utilisateur doit lancer LM Studio Local Server et charger un modèle avant d'utiliser VIVI.
- `VIVI_LMSTUDIO_MODEL` doit être configuré dans `.env`. Si absent, l'erreur `lmstudio_model_missing` est retournée de façon safe.
- `VIVI_LMSTUDIO_API_KEY` est séparée de `VIVI_API_KEY` : l'une protège VIVI, l'autre authentifie optionnellement auprès de LM Studio.

## Alternatives écartées

- **OpenAI comme provider par défaut** : écarté, contraire au principe local-first et à la confidentialité des données.
- **Multi-provider avec registry** : écarté, complexité non justifiée pour le MVP.
- **Ollama** : non exclu à terme mais hors périmètre MVP.
- **Fallback automatique cloud si LM Studio down** : écarté, comportement silencieux inacceptable pour un outil local-first.
