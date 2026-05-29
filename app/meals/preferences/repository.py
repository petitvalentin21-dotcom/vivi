from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from app.meals.preferences.models import Preference
from app.meals.preferences.schemas import PreferenceUpdate


class PreferenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, *, cle: str, valeur: str, type_valeur: str = "string", categorie: Optional[str] = None, notes: Optional[str] = None) -> Preference:
        existing = self.get_by_cle(cle)
        if existing is not None:
            raise ValueError(f"Clé '{cle}' existe déjà")
        now = datetime.now(timezone.utc)
        pref = Preference(
            cle=cle,
            valeur=valeur,
            type_valeur=type_valeur,
            categorie=categorie,
            notes=notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(pref)
        self.session.commit()
        self.session.refresh(pref)
        return pref

    def update(self, preference_id: uuid.UUID, data: PreferenceUpdate) -> Preference | None:
        pref = self.get(preference_id)
        if pref is None:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(pref, key, value)
        pref.updated_at = datetime.now(timezone.utc)
        self.session.add(pref)
        self.session.commit()
        self.session.refresh(pref)
        return pref

    def upsert_by_cle(self, *, cle: str, valeur: str, type_valeur: str = "string", categorie: Optional[str] = None, notes: Optional[str] = None) -> Preference:
        existing = self.get_by_cle(cle)
        if existing is not None:
            existing.valeur = valeur
            existing.type_valeur = type_valeur
            existing.categorie = categorie
            existing.notes = notes
            existing.updated_at = datetime.now(timezone.utc)
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
        now = datetime.now(timezone.utc)
        pref = Preference(
            cle=cle,
            valeur=valeur,
            type_valeur=type_valeur,
            categorie=categorie,
            notes=notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(pref)
        self.session.commit()
        self.session.refresh(pref)
        return pref

    def soft_delete(self, preference_id: uuid.UUID) -> bool:
        pref = self.get(preference_id)
        if pref is None:
            return False
        now = datetime.now(timezone.utc)
        pref.deleted_at = now
        pref.updated_at = now
        self.session.add(pref)
        self.session.commit()
        return True

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, preference_id: uuid.UUID, include_deleted: bool = False) -> Preference | None:
        stmt = select(Preference).where(Preference.id == preference_id)
        if not include_deleted:
            stmt = stmt.where(Preference.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def get_by_cle(self, cle: str, include_deleted: bool = False) -> Preference | None:
        stmt = select(Preference).where(Preference.cle == cle)
        if not include_deleted:
            stmt = stmt.where(Preference.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list(self, *, categorie: Optional[str] = None) -> list[Preference]:
        stmt = select(Preference).where(Preference.deleted_at.is_(None)).order_by(Preference.cle)
        if categorie is not None:
            stmt = stmt.where(Preference.categorie == categorie)
        return list(self.session.exec(stmt).all())
