from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.meals.courses.repository import ItemCourseRepository, ListeCoursesRepository
from app.meals.courses.schemas import (
    ItemCourseBody,
    ItemCourseCreate,
    ItemCourseRead,
    ItemCourseUpdate,
    ListeCoursesCreate,
    ListeCoursesRead,
    ListeCoursesUpdate,
)
from app.meals.courses.service import CoursesService

router = APIRouter(prefix="/courses", tags=["courses"])


def _get_session(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Base de données non configurée")
    with Session(engine) as session:
        yield session


def _get_service(session: Session = Depends(_get_session)) -> CoursesService:
    return CoursesService(ListeCoursesRepository(session), ItemCourseRepository(session))


# ------------------------------------------------------------------
# Listes de courses
# ------------------------------------------------------------------


@router.post("/listes", response_model=ListeCoursesRead, status_code=201)
def create_liste(data: ListeCoursesCreate, service: CoursesService = Depends(_get_service)) -> ListeCoursesRead:
    return service.creer_liste(data)


@router.get("/listes", response_model=list[ListeCoursesRead])
def list_listes(
    statut: str | None = None,
    service: CoursesService = Depends(_get_service),
) -> list[ListeCoursesRead]:
    return service.list_listes(statut=statut)


# NOTE: routes spécifiques (/resume, /archiver, /items, /tout-acheter) déclarées
# avant /{id} pour éviter tout conflit de résolution de chemin au même niveau.


@router.get("/listes/{id}/resume")
def get_resume(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> dict:
    liste = service.get_liste(id)
    if liste is None:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    return service.get_resume(id)


@router.get("/listes/{id}", response_model=ListeCoursesRead)
def get_liste(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> ListeCoursesRead:
    liste = service.get_liste(id)
    if liste is None:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    return liste


@router.patch("/listes/{id}", response_model=ListeCoursesRead)
def update_liste(
    id: uuid.UUID,
    data: ListeCoursesUpdate,
    service: CoursesService = Depends(_get_service),
) -> ListeCoursesRead:
    try:
        return service.update_liste(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Liste non trouvée")


@router.post("/listes/{id}/archiver", response_model=ListeCoursesRead)
def archiver_liste(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> ListeCoursesRead:
    try:
        return service.archiver_liste(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Liste non trouvée")


@router.delete("/listes/{id}", status_code=204)
def delete_liste(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> None:
    try:
        service.soft_delete_liste(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Liste non trouvée")


@router.post("/listes/{id}/items", response_model=ItemCourseRead, status_code=201)
def add_item(
    id: uuid.UUID,
    data: ItemCourseBody,
    service: CoursesService = Depends(_get_service),
) -> ItemCourseRead:
    liste = service.get_liste(id)
    if liste is None:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    create_data = ItemCourseCreate(liste_id=id, **data.model_dump())
    return service.create_item(create_data)


@router.get("/listes/{id}/items", response_model=list[ItemCourseRead])
def list_items(
    id: uuid.UUID,
    achetes_seulement: bool = False,
    service: CoursesService = Depends(_get_service),
) -> list[ItemCourseRead]:
    liste = service.get_liste(id)
    if liste is None:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    return service.list_items(id, achetes_seulement=achetes_seulement)


@router.post("/listes/{id}/tout-acheter")
def tout_acheter(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> dict:
    liste = service.get_liste(id)
    if liste is None:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    nb = service.tout_marquer_achete(id)
    return {"nb_mis_a_jour": nb}


# ------------------------------------------------------------------
# Items (actions directes sur un item)
# ------------------------------------------------------------------


@router.patch("/items/{id}", response_model=ItemCourseRead)
def update_item(
    id: uuid.UUID,
    data: ItemCourseUpdate,
    service: CoursesService = Depends(_get_service),
) -> ItemCourseRead:
    try:
        return service.update_item(id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Item non trouvé")


@router.post("/items/{id}/acheter", response_model=ItemCourseRead)
def acheter_item(id: uuid.UUID, body: dict, service: CoursesService = Depends(_get_service)) -> ItemCourseRead:
    valeur = bool(body.get("valeur", True))
    try:
        return service.marquer_achete(id, valeur)
    except ValueError:
        raise HTTPException(status_code=404, detail="Item non trouvé")


@router.delete("/items/{id}", status_code=204)
def delete_item(id: uuid.UUID, service: CoursesService = Depends(_get_service)) -> None:
    try:
        service.soft_delete_item(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Item non trouvé")
