from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.meals.courses.models import ItemCourse, ListeCourses
from app.meals.courses.schemas import (
    ItemCourseCreate,
    ItemCourseUpdate,
    ListeCoursesCreate,
    ListeCoursesUpdate,
)


class ListeCoursesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: ListeCoursesCreate) -> ListeCourses:
        now = datetime.now(timezone.utc)
        liste = ListeCourses(
            nom=data.nom,
            statut=data.statut,
            notes=data.notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(liste)
        self.session.commit()
        self.session.refresh(liste)
        return liste

    def update(self, id: uuid.UUID, data: ListeCoursesUpdate) -> ListeCourses:
        liste = self.get(id)
        if liste is None:
            raise ValueError(f"ListeCourses {id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(liste, key, value)
        liste.updated_at = datetime.now(timezone.utc)
        self.session.add(liste)
        self.session.commit()
        self.session.refresh(liste)
        return liste

    def soft_delete(self, id: uuid.UUID) -> None:
        liste = self.get(id)
        if liste is None:
            raise ValueError(f"ListeCourses {id} not found")
        now = datetime.now(timezone.utc)
        liste.deleted_at = now
        liste.updated_at = now
        self.session.add(liste)
        self.session.commit()

    def archiver(self, id: uuid.UUID) -> ListeCourses:
        liste = self.get(id)
        if liste is None:
            raise ValueError(f"ListeCourses {id} not found")
        liste.statut = "archivée"
        liste.updated_at = datetime.now(timezone.utc)
        self.session.add(liste)
        self.session.commit()
        self.session.refresh(liste)
        return liste

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: uuid.UUID, include_deleted: bool = False) -> ListeCourses | None:
        stmt = select(ListeCourses).where(ListeCourses.id == id)
        if not include_deleted:
            stmt = stmt.where(ListeCourses.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list(self, statut: str | None = None) -> list[ListeCourses]:
        stmt = (
            select(ListeCourses)
            .where(ListeCourses.deleted_at.is_(None))
            .order_by(ListeCourses.created_at.desc())
        )
        if statut is not None:
            stmt = stmt.where(ListeCourses.statut == statut)
        return list(self.session.exec(stmt).all())


class ItemCourseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create(self, data: ItemCourseCreate) -> ItemCourse:
        now = datetime.now(timezone.utc)
        item = ItemCourse(
            liste_id=data.liste_id,
            nom=data.nom,
            quantite=data.quantite,
            unite=data.unite,
            categorie=data.categorie,
            recette_id=data.recette_id,
            achete=data.achete,
            notes=data.notes,
            created_at=now,
            updated_at=now,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update(self, id: uuid.UUID, data: ItemCourseUpdate) -> ItemCourse:
        item = self.get(id)
        if item is None:
            raise ValueError(f"ItemCourse {id} not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        item.updated_at = datetime.now(timezone.utc)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def marquer_achete(self, id: uuid.UUID, valeur: bool = True) -> ItemCourse:
        item = self.get(id)
        if item is None:
            raise ValueError(f"ItemCourse {id} not found")
        item.achete = valeur
        item.updated_at = datetime.now(timezone.utc)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def soft_delete(self, id: uuid.UUID) -> None:
        item = self.get(id)
        if item is None:
            raise ValueError(f"ItemCourse {id} not found")
        now = datetime.now(timezone.utc)
        item.deleted_at = now
        item.updated_at = now
        self.session.add(item)
        self.session.commit()

    def tout_marquer_achete(self, liste_id: uuid.UUID) -> int:
        items = self.list_by_liste(liste_id, achetes_seulement=False)
        now = datetime.now(timezone.utc)
        count = 0
        for item in items:
            if not item.achete:
                item.achete = True
                item.updated_at = now
                self.session.add(item)
                count += 1
        self.session.commit()
        return count

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: uuid.UUID, include_deleted: bool = False) -> ItemCourse | None:
        stmt = select(ItemCourse).where(ItemCourse.id == id)
        if not include_deleted:
            stmt = stmt.where(ItemCourse.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    def list_by_liste(self, liste_id: uuid.UUID, achetes_seulement: bool = False) -> list[ItemCourse]:
        stmt = (
            select(ItemCourse)
            .where(ItemCourse.liste_id == liste_id)
            .where(ItemCourse.deleted_at.is_(None))
            .order_by(ItemCourse.created_at)
        )
        if achetes_seulement:
            stmt = stmt.where(ItemCourse.achete.is_(True))
        return list(self.session.exec(stmt).all())
