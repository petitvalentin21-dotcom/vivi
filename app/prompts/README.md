# app/prompts — Prompts système versionnés

Prompts système pour le LLM, stockés en fichiers Markdown, versionnés par dossier.

## Concept

Chaque version est un sous-dossier `vN/` contenant des fichiers `.md`. Le loader Python lit ces fichiers directement depuis le filesystem — aucune base de données, aucun templating.

```
app/prompts/
  loader.py        — fonctions load_prompt / list_prompts / list_versions
  api.py           — endpoints GET /prompts et GET /prompts/{name}
  schemas.py       — Pydantic schemas
  v1/
    system.md      — identité, domaine, ton, capacités, limites
    tool_calling.md — instructions d'usage des outils
```

## Prompts actuels (v1)

| Fichier | Rôle |
|---------|------|
| `system.md` | Prompt système principal : qui est Vivi, son domaine, son ton, ses capacités et ses limites |
| `tool_calling.md` | Instructions pour l'appel des outils LLM : quand appeler, format attendu, interprétation, erreurs |

## Ajouter un prompt

1. Créer le fichier `.md` dans `v1/` (ou la version cible).
2. Ajouter un test qui vérifie que `list_prompts()` retourne le nouveau nom.
3. Documenter le rôle dans ce README.

## Versionner (v2 et au-delà)

1. Créer `v2/` à côté de `v1/`.
2. Y copier et modifier les prompts nécessaires.
3. Changer `DEFAULT_VERSION = "v2"` dans `loader.py` quand la version est prête.
4. `v1/` reste accessible via le paramètre `?version=v1`.

## Endpoints

- `GET /prompts` — liste les prompts et versions disponibles
- `GET /prompts/{name}` — retourne le contenu d'un prompt (`?version=v1` optionnel)

## Note — pas de templating dans FEAT-23

L'injection de contexte dynamique (préférences utilisateur, état du stock, date du jour, etc.) est l'objet de **FEAT-29**. Dans cette version, les prompts sont des fichiers statiques. Ne pas introduire de variables `{{...}}` ou `{...}` avant FEAT-29.
