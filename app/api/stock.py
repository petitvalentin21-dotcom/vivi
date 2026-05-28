from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.meals.stock.repository import BatchRepository, IngredientBaseRepository
from app.meals.stock.schemas import (
    BatchCreate,
    BatchRead,
    BatchUpdate,
    IngredientBaseCreate,
    IngredientBaseRead,
    IngredientBaseUpdate,
)
from app.meals.stock.service import StockService

router = APIRouter(prefix="/stock", tags=["stock"])


def _get_session(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Base de données non configurée")
    with Session(engine) as session:
        yield session


def _get_service(session: Session = Depends(_get_session)) -> StockService:
    return StockService(BatchRepository(session), IngredientBaseRepository(session))


# ------------------------------------------------------------------
# Batchs
# ------------------------------------------------------------------


@router.post("/batchs", response_model=BatchRead, status_code=201)
def create_batch(data: BatchCreate, service: StockService = Depends(_get_service)) -> BatchRead:
    return service.create_batch(data)


@router.get("/batchs", response_model=list[BatchRead])
def list_batchs(
    actifs_seulement: bool = True,
    stockage: str | None = None,
    service: StockService = Depends(_get_service),
) -> list[BatchRead]:
    return service.list_batchs(actifs_seulement=actifs_seulement, stockage=stockage)


@router.get("/batchs/{id}", response_model=BatchRead)
def get_batch(id: uuid.UUID, service: StockService = Depends(_get_service)) -> BatchRead:
    batch = service.get_batch(id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch non trouvé")
    return batch


@router.patch("/batchs/{id}", response_model=BatchRead)
def update_batch(
    id: uuid.UUID,
    data: BatchUpdate,
    service: StockService = Depends(_get_service),
) -> BatchRead:
    try:
        return service.update_batch(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch non trouvé")


@router.post("/batchs/{id}/consommer", response_model=BatchRead)
def consommer_batch(
    id: uuid.UUID,
    body: dict,
    service: StockService = Depends(_get_service),
) -> BatchRead:
    nb = int(body.get("nb", 1))
    if nb < 1:
        raise HTTPException(status_code=422, detail="nb doit être ≥ 1")
    try:
        return service.consommer_portion(id, nb)
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail="Batch non trouvé")
        raise HTTPException(status_code=409, detail=msg)


@router.delete("/batchs/{id}", status_code=204)
def delete_batch(id: uuid.UUID, service: StockService = Depends(_get_service)) -> None:
    try:
        service.soft_delete_batch(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Batch non trouvé")


# ------------------------------------------------------------------
# Ingrédients de base
# NOTE: /ingredients/alertes MUST be declared before /ingredients/{id}
# ------------------------------------------------------------------


@router.get("/ingredients/alertes", response_model=list[IngredientBaseRead])
def get_alertes(service: StockService = Depends(_get_service)) -> list[IngredientBaseRead]:
    return service.get_alertes()


@router.post("/ingredients", response_model=IngredientBaseRead, status_code=201)
def create_ingredient(
    data: IngredientBaseCreate, service: StockService = Depends(_get_service)
) -> IngredientBaseRead:
    return service.create_ingredient(data)


@router.get("/ingredients", response_model=list[IngredientBaseRead])
def list_ingredients(
    categorie: str | None = None,
    service: StockService = Depends(_get_service),
) -> list[IngredientBaseRead]:
    return service.list_ingredients(categorie=categorie)


@router.get("/ingredients/{id}", response_model=IngredientBaseRead)
def get_ingredient(id: uuid.UUID, service: StockService = Depends(_get_service)) -> IngredientBaseRead:
    ingredient = service.get_ingredient(id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingrédient non trouvé")
    return ingredient


@router.patch("/ingredients/{id}", response_model=IngredientBaseRead)
def update_ingredient(
    id: uuid.UUID,
    data: IngredientBaseUpdate,
    service: StockService = Depends(_get_service),
) -> IngredientBaseRead:
    try:
        return service.update_ingredient(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ingrédient non trouvé")


@router.delete("/ingredients/{id}", status_code=204)
def delete_ingredient(id: uuid.UUID, service: StockService = Depends(_get_service)) -> None:
    try:
        service.soft_delete_ingredient(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ingrédient non trouvé")


# ------------------------------------------------------------------
# Vue synthétique
# ------------------------------------------------------------------


@router.get("/resume")
def get_resume(service: StockService = Depends(_get_service)) -> dict:
    stock = service.get_stock_actif()
    return {
        "batchs": [BatchRead.model_validate(b) for b in stock["batchs"]],
        "ingredients_alertes": [IngredientBaseRead.model_validate(i) for i in stock["ingredients_alertes"]],
    }
