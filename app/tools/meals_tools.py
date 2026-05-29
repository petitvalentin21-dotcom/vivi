"""
5 outils lecture-seule pour le domaine Repas.

Contrat callable : (session: Session, **kwargs) -> Any sérialisable JSON.
list_active_items() n'existe pas dans CoursesService — on utilise
list_listes(statut="en_cours") + list_items(liste_id).
"""
from __future__ import annotations

import uuid
from typing import Optional

from sqlmodel import Session

from app.meals.courses.repository import ItemCourseRepository, ListeCoursesRepository
from app.meals.courses.schemas import ItemCourseRead, ListeCoursesRead
from app.meals.courses.service import CoursesService
from app.meals.preferences.repository import PreferenceRepository
from app.meals.preferences.service import PreferenceService
from app.meals.recettes.repository import RecetteRepository
from app.meals.recettes.schemas import RecetteRead
from app.meals.recettes.service import RecetteService
from app.meals.stock.repository import BatchRepository, IngredientBaseRepository
from app.meals.stock.schemas import BatchRead, IngredientBaseRead
from app.meals.stock.service import StockService
from app.tools.registry import ToolDefinition, register_tool


# ---------------------------------------------------------------------------
# list_recettes
# ---------------------------------------------------------------------------


def _list_recettes(session: Session) -> list[dict]:
    repo = RecetteRepository(session)
    service = RecetteService(repo)
    items = service.list()
    return [RecetteRead.model_validate(r).model_dump(mode="json") for r in items]


register_tool(ToolDefinition(
    name="list_recettes",
    description="Liste toutes les recettes connues de Vivi (id, titre, tags).",
    parameters_schema={"type": "object", "properties": {}, "required": []},
    callable=_list_recettes,
))


# ---------------------------------------------------------------------------
# get_recette_by_id
# ---------------------------------------------------------------------------


def _get_recette_by_id(session: Session, recette_id: str) -> dict:
    try:
        rid = uuid.UUID(recette_id)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"recette_id invalide : {recette_id!r}") from exc
    repo = RecetteRepository(session)
    service = RecetteService(repo)
    recette = service.get(rid)
    if recette is None:
        raise ValueError(f"Recette introuvable : {recette_id}")
    return RecetteRead.model_validate(recette).model_dump(mode="json")


register_tool(ToolDefinition(
    name="get_recette_by_id",
    description="Récupère le détail complet d'une recette par son id (ingrédients, étapes, tags).",
    parameters_schema={
        "type": "object",
        "properties": {
            "recette_id": {
                "type": "string",
                "format": "uuid",
                "description": "Identifiant UUID de la recette à récupérer.",
            }
        },
        "required": ["recette_id"],
    },
    callable=_get_recette_by_id,
))


# ---------------------------------------------------------------------------
# list_stock
# ---------------------------------------------------------------------------


def _list_stock(session: Session, categorie: Optional[str] = None) -> dict:
    batch_repo = BatchRepository(session)
    ingredient_repo = IngredientBaseRepository(session)
    service = StockService(batch_repo, ingredient_repo)
    batchs = service.list_batchs(actifs_seulement=True)
    ingredients = service.list_ingredients(categorie=categorie)
    return {
        "batchs": [BatchRead.model_validate(b).model_dump(mode="json") for b in batchs],
        "ingredients": [IngredientBaseRead.model_validate(i).model_dump(mode="json") for i in ingredients],
    }


register_tool(ToolDefinition(
    name="list_stock",
    description="Liste le stock courant : batchs en cours (préparations cuisinées) + ingrédients de base présents.",
    parameters_schema={
        "type": "object",
        "properties": {
            "categorie": {
                "type": "string",
                "description": "Filtre optionnel sur la catégorie d'ingrédient (ex: 'légumes', 'féculents').",
            }
        },
        "required": [],
    },
    callable=_list_stock,
))


# ---------------------------------------------------------------------------
# list_courses
# ---------------------------------------------------------------------------


def _list_courses(session: Session) -> list[dict]:
    liste_repo = ListeCoursesRepository(session)
    item_repo = ItemCourseRepository(session)
    service = CoursesService(liste_repo, item_repo)
    listes = service.list_listes(statut="en_cours")
    result = []
    for liste in listes:
        items = service.list_items(liste.id)
        result.append({
            **ListeCoursesRead.model_validate(liste).model_dump(mode="json"),
            "items": [ItemCourseRead.model_validate(item).model_dump(mode="json") for item in items],
        })
    return result


register_tool(ToolDefinition(
    name="list_courses",
    description="Liste les items de la liste de courses active (listes en cours).",
    parameters_schema={"type": "object", "properties": {}, "required": []},
    callable=_list_courses,
))


# ---------------------------------------------------------------------------
# get_preferences_resume
# ---------------------------------------------------------------------------


def _get_preferences_resume(session: Session) -> dict:
    repo = PreferenceRepository(session)
    service = PreferenceService(repo)
    return service.get_all_as_dict()


register_tool(ToolDefinition(
    name="get_preferences_resume",
    description="Retourne toutes les préférences utilisateur sous forme de dictionnaire typé (régime, allergies, contraintes, etc.).",
    parameters_schema={"type": "object", "properties": {}, "required": []},
    callable=_get_preferences_resume,
))
