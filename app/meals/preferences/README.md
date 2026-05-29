# Module Preferences

Stockage clé/valeur typé pour les préférences utilisateur. Point d'entrée pour FEAT-22 (tool calling LLM) et FEAT-29 (mémoire conversationnelle).

## Modèle

| Champ | Type | Description |
|---|---|---|
| `id` | UUID | Clé primaire |
| `cle` | str (unique) | Identifiant de la préférence |
| `valeur` | str | Valeur sérialisée |
| `type_valeur` | Literal | `string`, `int`, `float`, `bool`, `list`, `dict` |
| `categorie` | str? | Regroupement fonctionnel |
| `notes` | str? | Commentaire libre |
| `created_at` | datetime | |
| `updated_at` | datetime | |
| `deleted_at` | datetime? | Soft delete |

## Endpoints

| Méthode | Chemin | Description |
|---|---|---|
| POST | `/preferences` | Créer (409 si clé existante) |
| GET | `/preferences` | Lister, filtre `?categorie=` |
| GET | `/preferences/resume` | Dict typé `{cle: valeur_décodée}` |
| GET | `/preferences/{cle}` | Lire par clé |
| PATCH | `/preferences/{preference_id}` | Mise à jour partielle (UUID) |
| PUT | `/preferences/{cle}` | Upsert par clé |
| DELETE | `/preferences/{preference_id}` | Soft delete (UUID) |

## Usage du PreferenceService

```python
svc = PreferenceService(repo)

# Écrire
svc.set_value("regime", "végétarien")
svc.set_value("temps_cuisine_max", 45, type_valeur="int", categorie="planning")
svc.set_value("allergies", ["gluten", "lactose"], type_valeur="list")
svc.set_value("aime_epice", True, type_valeur="bool")

# Lire (typé, sans lever d'exception)
regime = svc.get_value("regime")               # "végétarien"
temps  = svc.get_value("temps_cuisine_max")    # 45 (int)
absent = svc.get_value("inconnu", default="") # ""

# Vue complète pour le LLM
d = svc.get_all_as_dict()
# {"regime": "végétarien", "temps_cuisine_max": 45, "allergies": [...], ...}
```

## Clés conventionnelles

| Clé | Type | Description |
|---|---|---|
| `regime` | string | Ex : `"végétarien"`, `"omnivore"` |
| `allergies` | list | Ex : `["gluten", "lactose"]` |
| `temps_cuisine_max` | int | En minutes |
| `aime_epice` | bool | Tolérance aux épices |
| `materiel_dispo` | list | Ex : `["wok", "cocotte-minute"]` |
| `batch_cooking_actif` | bool | Cuisine en lot le week-end |
| `taille_foyer` | int | Nombre de personnes |
