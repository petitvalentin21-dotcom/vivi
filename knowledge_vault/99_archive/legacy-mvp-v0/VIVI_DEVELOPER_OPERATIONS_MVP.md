---
title: VIVI MVP — Guide développeur opérationnel
status: archived
doc_type: developer-guide
scope: mvp
llm_index: false
llm_role: developer_guide
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - developpement
  - runbook
  - tests
  - smoke
---

# VIVI MVP — Guide développeur opérationnel

## Démarrage minimal

1. `pip install -r requirements.txt`
2. copier `.env.example` vers `.env`
3. lancer LM Studio Local Server
4. lancer backend: `uvicorn app.api.server:app --host 127.0.0.1 --port 8000`
5. ouvrir `http://127.0.0.1:8000/`

## Variables clés

- `VIVI_LMSTUDIO_BASE_URL`
- `VIVI_LMSTUDIO_MODEL`
- `VIVI_LMSTUDIO_API_KEY` (si requis côté provider)
- `VIVI_API_KEY` (protection API VIVI)
- `VIVI_KNOWLEDGE_VAULT_PATH`
- `VIVI_RAG_TOP_K`
- `VIVI_LLM_TIMEOUT_SECONDS`

## Smoke et tests

Automatisés:

- `pytest -q`

Smoke local:

- `python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --verbose`
- avec auth: `--api-key <VIVI_API_KEY>`

## Debug rapide

- `/health` pour disponibilité serveur.
- `/runtime/info` pour auth/provider/vault.
- `/knowledge/search?q=<query>` pour diagnostic retrieval.
- `/chat` mode `document` pour vérifier sources.

## Workflow recommandé

- petits changements atomiques ;
- tests ciblés puis `pytest -q` ;
- aucune feature post-MVP pendant maintenance MVP ;
- pas de refactor opportuniste.

## Limitations MVP à respecter

- provider unique LM Studio ;
- pas de fallback externe ;
- pas de multi-agents ;
- pas de vector DB obligatoire ;
- mémoire session simple.
