# app/tools — Tool Registry

Module de registre d'outils pour le LLM. Fournit 5 outils lecture-seule, exposés via une API de debug (`/tools`).

**Note :** les outils ne sont pas encore appelés automatiquement par le LLM dans cette FEAT. Le branchement LLM ↔ outils est prévu en FEAT-23 (prompts système) et FEAT-29 (boucle conversationnelle).

## Concept

Registre statique en dictionnaire Python. Pas de décorateur magique.

```
REGISTRY: dict[str, ToolDefinition]
```

Chaque outil est une `ToolDefinition` (dataclass frozen) avec :
- `name` — identifiant unique
- `description` — phrase courte en français, lisible par le LLM
- `parameters_schema` — JSON Schema (style OpenAI tools)
- `callable` — fonction `(session: Session, **kwargs) -> Any sérialisable JSON`
- `read_only: bool` — toujours `True` pour FEAT-22

## Les 5 outils (FEAT-22)

| Outil | Service métier | Paramètres | Note |
|-------|---------------|------------|------|
| `list_recettes` | `RecetteService.list()` | aucun | |
| `get_recette_by_id` | `RecetteService.get(id)` | `recette_id: UUID str` | ValueError si inconnu |
| `list_stock` | `StockService.list_batchs()` + `list_ingredients()` | `categorie: str?` | Batchs actifs seulement |
| `list_courses` | `CoursesService.list_listes(statut="en_cours")` + `list_items()` | aucun | `list_active_items()` n'existe pas dans CoursesService — on liste les listes "en_cours" |
| `get_preferences_resume` | `PreferenceService.get_all_as_dict()` | aucun | Dict typé décodé |

## Format `parameters_schema`

JSON Schema valide, style OpenAI :

```python
{
    "type": "object",
    "properties": {
        "param_name": {
            "type": "string",
            "description": "Description lisible.",
        }
    },
    "required": ["param_name"],  # vide [] si aucun paramètre obligatoire
}
```

## Contrat callable

```python
def _mon_outil(session: Session, **kwargs) -> Any:
    # kwargs = paramètres issus de parameters_schema
    # retourner un objet sérialisable JSON (dict, list, str, int, ...)
    ...
```

Le callable ne doit jamais lever autre chose que `ValueError` pour les erreurs métier (404/400 côté API) et `TypeError` pour les mauvais arguments (422 côté API).

## Ajouter un outil futur (FEAT-23/29)

1. Définir le callable dans `meals_tools.py` (ou un nouveau fichier `*_tools.py`)
2. Appeler `register_tool(ToolDefinition(...))` au niveau module
3. Importer le fichier dans `app/tools/__init__.py` comme side-effect import
4. Ajouter les tests dans `tests/test_meals_tools.py` ou un fichier dédié

## Endpoints

- `GET /tools` — liste les outils (nom, description, schema, read_only)
- `POST /tools/{name}/invoke` — invoque un outil (debug, pas d'auth requis en FEAT-22)
