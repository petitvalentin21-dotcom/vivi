from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.meals.courses.models import ItemCourse, ListeCourses
from app.meals.courses.repository import ItemCourseRepository, ListeCoursesRepository
from app.meals.courses.schemas import (
    ItemCourseBody,
    ItemCourseCreate,
    ItemCourseUpdate,
    ListeCoursesCreate,
    ListeCoursesUpdate,
)


class CoursesService:
    def __init__(self, liste_repo: ListeCoursesRepository, item_repo: ItemCourseRepository) -> None:
        self.liste_repo = liste_repo
        self.item_repo = item_repo

    # ------------------------------------------------------------------
    # ListeCourses
    # ------------------------------------------------------------------

    def creer_liste(self, data: ListeCoursesCreate) -> ListeCourses:
        return self.liste_repo.create(data)

    def get_liste(self, id: uuid.UUID) -> ListeCourses | None:
        return self.liste_repo.get(id)

    def list_listes(self, statut: str | None = None) -> list[ListeCourses]:
        return self.liste_repo.list(statut=statut)

    def update_liste(self, id: uuid.UUID, data: ListeCoursesUpdate) -> ListeCourses:
        return self.liste_repo.update(id, data)

    def soft_delete_liste(self, id: uuid.UUID) -> None:
        self.liste_repo.soft_delete(id)

    def archiver_liste(self, id: uuid.UUID) -> ListeCourses:
        return self.liste_repo.archiver(id)

    # ------------------------------------------------------------------
    # ItemCourse
    # ------------------------------------------------------------------

    def create_item(self, data: ItemCourseCreate) -> ItemCourse:
        return self.item_repo.create(data)

    def get_item(self, id: uuid.UUID) -> ItemCourse | None:
        return self.item_repo.get(id)

    def list_items(self, liste_id: uuid.UUID, achetes_seulement: bool = False) -> list[ItemCourse]:
        return self.item_repo.list_by_liste(liste_id, achetes_seulement=achetes_seulement)

    def update_item(self, id: uuid.UUID, data: ItemCourseUpdate) -> ItemCourse:
        return self.item_repo.update(id, data)

    def marquer_achete(self, id: uuid.UUID, valeur: bool = True) -> ItemCourse:
        return self.item_repo.marquer_achete(id, valeur)

    def soft_delete_item(self, id: uuid.UUID) -> None:
        self.item_repo.soft_delete(id)

    def tout_marquer_achete(self, liste_id: uuid.UUID) -> int:
        return self.item_repo.tout_marquer_achete(liste_id)

    # ------------------------------------------------------------------
    # Opérations complexes
    # ------------------------------------------------------------------

    def creer_liste_avec_items(self, liste_data: ListeCoursesCreate, items: list[ItemCourseBody]) -> ListeCourses:
        """Création atomique : liste + items dans une seule transaction."""
        session = self.liste_repo.session
        now = datetime.now(timezone.utc)
        liste = ListeCourses(
            nom=liste_data.nom,
            statut=liste_data.statut,
            notes=liste_data.notes,
            created_at=now,
            updated_at=now,
        )
        session.add(liste)
        session.flush()
        for item_data in items:
            item = ItemCourse(
                liste_id=liste.id,
                nom=item_data.nom,
                quantite=item_data.quantite,
                unite=item_data.unite,
                categorie=item_data.categorie,
                recette_id=item_data.recette_id,
                achete=item_data.achete,
                notes=item_data.notes,
                created_at=now,
                updated_at=now,
            )
            session.add(item)
        session.commit()
        session.refresh(liste)
        return liste

    def get_resume(self, liste_id: uuid.UUID) -> dict:
        items = self.item_repo.list_by_liste(liste_id, achetes_seulement=False)
        total = len(items)
        nb_achetes = sum(1 for item in items if item.achete)
        nb_restants = total - nb_achetes
        pct = round(nb_achetes / total * 100) if total > 0 else 0
        return {
            "total": total,
            "nb_achetes": nb_achetes,
            "nb_restants": nb_restants,
            "pct_avancement": pct,
        }

    def archiver_si_terminee(self, liste_id: uuid.UUID) -> bool:
        """Archive la liste si tous les items non-supprimés sont achetés."""
        items = self.item_repo.list_by_liste(liste_id, achetes_seulement=False)
        if not items:
            return False
        if all(item.achete for item in items):
            self.liste_repo.archiver(liste_id)
            return True
        return False
