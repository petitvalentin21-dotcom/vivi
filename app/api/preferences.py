from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.meals.preferences.repository import PreferenceRepository
from app.meals.preferences.schemas import (
    PreferenceCreate,
    PreferenceListResponse,
    PreferenceRead,
    PreferenceResumeResponse,
    PreferenceUpdate,
    PreferenceUpsert,
)
from app.meals.preferences.service import PreferenceService

router = APIRouter(prefix="/preferences", tags=["preferences"])


def _get_session(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Base de données non configurée")
    with Session(engine) as session:
        yield session


def _get_repository(session: Session = Depends(_get_session)) -> PreferenceRepository:
    return PreferenceRepository(session)


def _get_service(repo: PreferenceRepository = Depends(_get_repository)) -> PreferenceService:
    return PreferenceService(repo)


@router.post("", response_model=PreferenceRead, status_code=201)
def create_preference(data: PreferenceCreate, service: PreferenceService = Depends(_get_service)) -> PreferenceRead:
    try:
        return service.create(data)
    except ValueError:
        raise HTTPException(status_code=409, detail="Clé déjà existante")


@router.get("", response_model=PreferenceListResponse)
def list_preferences(
    categorie: Optional[str] = None,
    service: PreferenceService = Depends(_get_service),
) -> PreferenceListResponse:
    items = service.list(categorie=categorie)
    return PreferenceListResponse(items=items, count=len(items))


# NOTE: /resume DOIT être déclaré avant /{cle} pour éviter que "resume" soit capturé comme paramètre
@router.get("/resume", response_model=PreferenceResumeResponse)
def get_resume(service: PreferenceService = Depends(_get_service)) -> PreferenceResumeResponse:
    prefs = service.get_all_as_dict()
    return PreferenceResumeResponse(preferences=prefs, count=len(prefs))


@router.get("/{cle}", response_model=PreferenceRead)
def get_preference(cle: str, service: PreferenceService = Depends(_get_service)) -> PreferenceRead:
    pref = service.get_by_cle(cle)
    if pref is None:
        raise HTTPException(status_code=404, detail="Préférence non trouvée")
    return pref


@router.patch("/{preference_id}", response_model=PreferenceRead)
def update_preference(
    preference_id: uuid.UUID,
    data: PreferenceUpdate,
    service: PreferenceService = Depends(_get_service),
) -> PreferenceRead:
    pref = service.update(preference_id, data)
    if pref is None:
        raise HTTPException(status_code=404, detail="Préférence non trouvée")
    return pref


@router.put("/{cle}", response_model=PreferenceRead)
def upsert_preference(
    cle: str,
    data: PreferenceUpsert,
    service: PreferenceService = Depends(_get_service),
) -> PreferenceRead:
    return service.upsert_by_cle(cle, data)


@router.delete("/{preference_id}", status_code=204)
def delete_preference(preference_id: uuid.UUID, service: PreferenceService = Depends(_get_service)) -> None:
    deleted = service.soft_delete(preference_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Préférence non trouvée")
