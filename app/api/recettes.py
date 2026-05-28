from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.meals.recettes.repository import RecetteRepository
from app.meals.recettes.schemas import RecetteCreate, RecetteRead, RecetteUpdate
from app.meals.recettes.service import RecetteService

router = APIRouter(prefix="/recettes", tags=["recettes"])


def _get_session(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Base de données non configurée")
    with Session(engine) as session:
        yield session


def _get_service(session: Session = Depends(_get_session)) -> RecetteService:
    return RecetteService(RecetteRepository(session))


# /count BEFORE /{id} — "count" is not a valid UUID and must not match /{id}.
@router.get("/count")
def count_recettes(service: RecetteService = Depends(_get_service)) -> dict:
    return {"count": service.count()}


@router.post("", response_model=RecetteRead, status_code=201)
def create_recette(data: RecetteCreate, service: RecetteService = Depends(_get_service)) -> RecetteRead:
    return service.create(data)


@router.get("", response_model=list[RecetteRead])
def list_recettes(
    limit: int = 50,
    offset: int = 0,
    tag: str | None = None,
    service: RecetteService = Depends(_get_service),
) -> list[RecetteRead]:
    return service.list(limit=limit, offset=offset, tag=tag)


@router.get("/{id}", response_model=RecetteRead)
def get_recette(id: uuid.UUID, service: RecetteService = Depends(_get_service)) -> RecetteRead:
    recette = service.get(id)
    if recette is None:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
    return recette


@router.patch("/{id}", response_model=RecetteRead)
def update_recette(
    id: uuid.UUID,
    data: RecetteUpdate,
    service: RecetteService = Depends(_get_service),
) -> RecetteRead:
    try:
        return service.update(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recette non trouvée")


@router.delete("/{id}", status_code=204)
def delete_recette(id: uuid.UUID, service: RecetteService = Depends(_get_service)) -> None:
    try:
        service.soft_delete(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recette non trouvée")
