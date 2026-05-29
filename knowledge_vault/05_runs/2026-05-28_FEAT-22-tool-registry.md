---
title: Run Log — FEAT-22
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-28
tags:
  - vivi
  - mvp
  - run
  - tools
  - llm
---

## Résumé

Ajout du module `app/tools/` : registre statique d'outils + 5 callables lecture-seule mappés sur les services métier Repas. Endpoints `GET /tools` et `POST /tools/{name}/invoke` (debug). Correction des 2 notes ambiguës de FEAT-21bis (VIVI_MVP_DOC_HUB et Écrire pour VIVI et le RAG).

Les outils ne sont pas encore appelés automatiquement par le LLM — c'est l'objet de FEAT-23 (prompts) et FEAT-29 (boucle conversationnelle).

## Fichiers créés

- `app/tools/__init__.py`
- `app/tools/registry.py` — dataclass `ToolDefinition`, `REGISTRY`, `register_tool`, `list_tools`, `get_tool`
- `app/tools/schemas.py` — `ToolDescriptor`, `ToolListResponse`, `ToolInvocationRequest`, `ToolInvocationResponse`
- `app/tools/meals_tools.py` — 5 callables + enregistrement dans REGISTRY
- `app/tools/api.py` — router `prefix=/tools`, `GET ""`, `POST /{name}/invoke`
- `app/tools/README.md`
- `tests/test_tool_registry.py` — 10 tests registry
- `tests/test_meals_tools.py` — 16 tests callables
- `tests/test_tools_api.py` — 17 tests API
- `knowledge_vault/05_runs/2026-05-28_FEAT-22-tool-registry.md` — ce run log

## Fichiers modifiés

- `app/api/server.py` — ajout `from app.tools import router as tools_router` + `app.include_router(tools_router)`
- `knowledge_vault/01_user_docs/VIVI_MVP_DOC_HUB.md` — retrait keyword "lm studio provider", liens LM Studio → Ollama/Repas, liens archivés supprimés
- `knowledge_vault/01_user_docs/Écrire pour VIVI et le RAG.md` — exemples LM Studio remplacés par Ollama

## Notes sur les écarts par rapport à la spec

- `list_active_items()` n'existe pas dans `CoursesService`. Remplacement par `list_listes(statut="en_cours")` + `list_items(liste_id)` → retourne une liste de dicts `{id, nom, statut, items: [...]}`.
- `upsert_by_cle()` sur `PreferenceRepository` prend des arguments par mots-clés uniquement — corrigé dans `test_meals_tools.py` après premier run.

## Validation

```
pytest tests/test_tool_registry.py tests/test_meals_tools.py tests/test_tools_api.py -v
43 passed in 6.60s

pytest tests/ -q
503 passed in 73.53s
```

## Résultat

Module `app/tools/` opérationnel. 5 outils lecture-seule accessibles via `GET /tools` et invocables via `POST /tools/{name}/invoke`. Registry alimenté au démarrage par import side-effect de `meals_tools`. Vault aligné (notes FEAT-21bis ambiguës corrigées).
