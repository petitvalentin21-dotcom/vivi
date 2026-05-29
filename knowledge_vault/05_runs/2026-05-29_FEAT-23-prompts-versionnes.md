---
title: Run Log — FEAT-23
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-29
tags:
  - vivi
  - mvp
  - run
  - prompts
  - llm
---

## Résumé

Mise en place du module `app/prompts/` : loader Python pur filesystem, deux prompts Markdown versionnés (`system.md`, `tool_calling.md`), deux endpoints debug `/prompts` et `/prompts/{name}`, 16 tests (loader + API). Le router est branché dans `app/api/server.py`.

## Fichiers créés

- `app/prompts/__init__.py`
- `app/prompts/loader.py`
- `app/prompts/api.py`
- `app/prompts/schemas.py`
- `app/prompts/README.md`
- `app/prompts/v1/system.md`
- `app/prompts/v1/tool_calling.md`
- `tests/test_prompts_loader.py`
- `tests/test_prompts_api.py`
- `knowledge_vault/05_runs/2026-05-29_FEAT-23-prompts-versionnes.md`

## Fichiers modifiés

- `app/api/server.py` — import et `include_router(prompts_router)` ajoutés

## Validation

```
pytest tests/test_prompts_loader.py tests/test_prompts_api.py -v
16 passed in 1.81s

pytest tests/ -q
519 passed in 68.81s
```

## Résultat

Module opérationnel. `GET /prompts` liste les deux prompts v1. `GET /prompts/system` et `GET /prompts/tool_calling` retournent le contenu. Pas de templating, pas de dépendance ajoutée. Structure prête pour FEAT-29 (boucle conversationnelle).
