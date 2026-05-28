---
title: Run Log — FEAT-19 Module Stock
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
  - stock
  - meals
---

# Run Log — FEAT-19 — 2026-05-28

## Résumé

Module Stock : modèles SQLModel `Batch` + `IngredientBase`, repositories, service avec
garde `consommer_portion` (soft-delete auto à 0 portion), 13 endpoints REST sous `/stock`,
migration Alembic 0003.

## Fichiers créés

- app/meals/stock/__init__.py
- app/meals/stock/models.py — Batch + IngredientBase SQLModel
- app/meals/stock/schemas.py — Create/Read/Update + StockageType Literal
- app/meals/stock/repository.py — BatchRepository (7 méthodes) + IngredientBaseRepository (6 méthodes)
- app/meals/stock/service.py — StockService + get_stock_actif()
- app/api/stock.py — 13 endpoints REST
- migrations/versions/0003_create_stock_tables.py
- tests/test_stock_models.py — 47 tests unitaires
- tests/test_stock_api.py — 35 tests intégration

## Fichiers modifiés

- app/api/server.py — include_router(stock_router)
- README.md — section FEAT-19
- tests/test_db_alembic.py — head 0002 → 0003
- tests/test_db_health_endpoint.py — head 0002 → 0003

## Validation

pytest -q → 329 passed (247 avant + 82 nouveaux)

## Résultat

Module Stock opérationnel. Batchs et ingrédients de base stockés, consommation
de portions avec soft-delete automatique, vue synthétique via GET /stock/resume.