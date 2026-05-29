---
title: Run Log — FEAT-21
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
  - preferences
---

## Résumé

Module Preferences créé (clé/valeur typé, encode/decode, upsert, soft delete) + fix convention run logs (CLAUDE.md, AGENTS.md, rattrapage FEAT-20). Écarts spec signalés : section AGENTS.md était §13 non §10 ; révision migration retenue `"0005"` (cohérence avec pattern existant `"0001"…"0004"`) ; `soft_delete → bool` et `update → Preference | None` adoptés conformément au spec (divergence intentionnelle par rapport au pattern raise-ValueError des modules précédents).

## Fichiers créés

- app/meals/preferences/__init__.py
- app/meals/preferences/models.py
- app/meals/preferences/schemas.py
- app/meals/preferences/repository.py
- app/meals/preferences/service.py
- app/meals/preferences/README.md
- app/api/preferences.py
- migrations/versions/0005_add_preferences.py
- tests/test_preferences_model.py
- tests/test_preferences_api.py
- knowledge_vault/05_runs/2026-05-28_FEAT-21-module-preferences.md

## Fichiers modifiés

- app/api/server.py — include_router(preferences_router)
- tests/test_db_alembic.py — head 0004 → 0005
- tests/test_db_health_endpoint.py — head 0004 → 0005
- CLAUDE.md — ajout section `## Conventions de développement` > `### Run logs`
- AGENTS.md — remplacement §13 Run history policy (STRICT)
- knowledge_vault/05_runs/2026-05-28_FEAT-20-module-courses.md — frontmatter + sections conformes

## Validation

```bash
pytest tests/test_preferences_model.py tests/test_preferences_api.py tests/test_db_alembic.py tests/test_db_health_endpoint.py -v
# 55 passed in 11.63s

pytest tests/ -q
# 460 passed in 71.15s
```

## Résultat

- 48 nouveaux tests (28 modèles + 20 API)
- Total suite : 460 tests, 0 régression (412 → 460)
- Endpoints opérationnels : POST/GET/PATCH/PUT/DELETE /preferences, GET /preferences/resume
- PreferenceService.get_value / set_value / get_all_as_dict disponibles pour FEAT-22 (tool calling)
- Commit : non créé — push : non poussé (non demandé)
