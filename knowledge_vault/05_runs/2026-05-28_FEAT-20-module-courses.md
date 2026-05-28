# Run log — FEAT-20 Module Courses

Date : 2026-05-28
Branche : main (à commit)

## Résultats des tests

```
412 passed in 55.68s
```

### Nouveaux tests FEAT-20

| Fichier | Tests |
|---------|-------|
| tests/test_courses_models.py | 36 |
| tests/test_courses_api.py | 50 |
| **Sous-total FEAT-20** | **86** |

### Couverture périmètre FEAT-20

- ListeCoursesRepository : create, get, list, update, soft_delete, archiver ✓
- ItemCourseRepository : create, get, list_by_liste, marquer_achete, update, soft_delete, tout_marquer_achete ✓
- CoursesService : creer_liste_avec_items (atomique), get_resume, archiver_si_terminee ✓
- API /courses/listes : POST, GET, GET/{id}, PATCH, DELETE, /archiver, /resume, /items, /tout-acheter ✓
- API /courses/items : PATCH, DELETE, /acheter ✓
- Migration 0004 : upgrade + downgrade ✓
- Alembic head 0003 → 0004 ✓
- 503 sans DB ✓

### Total suite

- Avant FEAT-20 : 329 tests
- Après FEAT-20 : **412 tests** (+83 nets, dont 4 tests alembic/health mis à jour)
- Aucune régression

## Fichiers créés / modifiés

### Créés
- app/meals/courses/__init__.py
- app/meals/courses/models.py
- app/meals/courses/schemas.py
- app/meals/courses/repository.py
- app/meals/courses/service.py
- app/api/courses.py
- migrations/versions/0004_create_courses_tables.py
- tests/test_courses_models.py
- tests/test_courses_api.py
- docs/run_logs/FEAT-20_run_log.md

### Modifiés
- app/api/server.py — include_router(courses_router)
- tests/test_db_alembic.py — head 0003 → 0004
- tests/test_db_health_endpoint.py — head 0003 → 0004
- README.md — section FEAT-20
