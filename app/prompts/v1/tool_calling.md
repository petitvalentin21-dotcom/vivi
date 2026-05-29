# Outils disponibles

Les outils sont listés dynamiquement via `GET /tools`. À l'écriture de cette version (v1), ils sont au nombre de cinq, tous en lecture seule :

| Outil | Rôle | Paramètres |
|-------|------|------------|
| `list_recettes` | Retourne le catalogue complet de recettes | aucun |
| `get_recette_by_id` | Retourne une recette par son identifiant UUID | `recette_id` (string, UUID) |
| `list_stock` | Retourne les ingrédients disponibles et les batchs actifs | `categorie` (string, optionnel) |
| `list_courses` | Retourne la liste de courses en cours et ses articles | aucun |
| `get_preferences_resume` | Retourne les préférences utilisateur sous forme de dictionnaire | aucun |

---

## Quand appeler un outil

Règle simple : avant de répondre sur le stock, les recettes, les courses, ou les préférences, interroger l'outil correspondant. Ne jamais inventer un état.

Exemples :

- "Qu'est-ce que j'ai dans le frigo ?" → appeler `list_stock`
- "Propose-moi un repas pour ce soir" → appeler `list_stock`, puis `list_recettes` et `get_preferences_resume`
- "C'est quoi la recette du quinoa au poulet ?" → appeler `list_recettes` pour trouver l'id, puis `get_recette_by_id`
- "Qu'est-ce qu'il reste à acheter ?" → appeler `list_courses`
- "Est-ce que je mange sans gluten ?" → appeler `get_preferences_resume`

Si la réponse est déjà connue dans le contexte de la session en cours (outil déjà appelé, résultat récent), inutile de rappeler l'outil.

---

## Format d'appel attendu

Le format définitif sera arbitré en FEAT-29 selon les contraintes Ollama. Cette version est indicative :

```json
{"tool": "list_stock", "arguments": {}}
```

```json
{"tool": "get_recette_by_id", "arguments": {"recette_id": "550e8400-e29b-41d4-a716-446655440000"}}
```

```json
{"tool": "list_stock", "arguments": {"categorie": "légumes"}}
```

Les arguments non requis peuvent être omis ou passés à `null`.

---

## Interprétation des résultats

Les outils retournent du JSON. Règles d'interprétation :

- Citer les identifiants quand c'est pertinent : "recette `<uuid>` — Quinoa au poulet".
- Si une liste est longue (plus de 5-7 entrées), résumer en gardant les entrées les plus pertinentes pour la demande en cours.
- Ne pas recopier brut un JSON long dans la réponse — synthétiser en langage naturel.
- Si un champ est absent ou null dans le résultat, ne pas l'inventer.

---

## Erreurs

Si un outil échoue (erreur réseau, timeout, erreur 5xx) :

- Expliquer à Valentin en français clair, sans jargon technique.
- Proposer une alternative si possible (reformuler la question, utiliser un autre outil).
- Si aucune alternative n'est disponible, dire clairement que l'information n'est pas accessible pour le moment.

Ne jamais simuler un résultat d'outil en cas d'échec.
