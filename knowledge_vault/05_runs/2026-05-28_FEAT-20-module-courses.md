---
title: Run Log — FEAT-20
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
  - courses
---

## Résumé

Module Courses créé en miroir de FEAT-19 (Stock) : deux entités (`ListeCourses`, `ItemCourse`), repository, service, 13 endpoints REST, migration Alembic 0004. Infrastructure uniquement — pas de génération LLM (FEAT-22).

## Fichiers créés

- app/meals/courses/__init__.py
- app/meals/courses/models.py
- app/meals/courses/schemas.py
- app/meals/courses/repository.py
- app/meals/courses/service.py
- app/api/courses.py
- migrations/versions/0004_create_courses_tables.py
- tests/test_courses_models.py
- tests/test_courses_api.py

## Fichiers modifiés

- app/api/server.py — include_router(courses_router)
- tests/test_db_alembic.py — head 0003 → 0004
- tests/test_db_health_endpoint.py — head 0003 → 0004
- README.md — section FEAT-20

## Validation

```bash
pytest tests/test_courses_models.py tests/test_courses_api.py tests/test_db_alembic.py tests/test_db_health_endpoint.py -v
# 90 passed in 16.59s

pytest tests/ -q
# 412 passed in 55.68s
```

## Résultat

- 86 nouveaux tests (36 modèles + 50 API) + 4 tests mis à jour
- Total suite : 412 tests, 0 régression
- Endpoints opérationnels : POST/GET/PATCH/DELETE /courses/listes, /archiver, /resume, /items, /tout-acheter, PATCH/DELETE/acheter /courses/items
- Soft delete, creer_liste_avec_items atomique, get_resume, archiver_si_terminee fonctionnels
