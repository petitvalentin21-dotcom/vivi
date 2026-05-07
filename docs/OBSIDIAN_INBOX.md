# Inbox Obsidian VIVI

## Rôle

`knowledge_vault/92_inbox/` reçoit uniquement des propositions générées par VIVI à relire par l'utilisateur.

Une note créée dans cette inbox n'est pas une source de vérité. Elle sert de brouillon candidat avant correction, validation et éventuelle intégration humaine dans une note source.

## Règle de validation

Principe FEAT-26 :

> VIVI propose. L'utilisateur valide. Les notes sources restent humaines et protégées.

VIVI ne modifie pas les notes sources, ne valide pas ses propres propositions et ne promeut pas automatiquement une note inbox.

## Frontmatter

Frontmatter minimal généré :

```yaml
---
type: generated_note
status: draft
source: vivi
created_at: YYYY-MM-DD
index: false
review_required: true
---
```

Types autorisés :

- `generated_note`
- `conversation_summary`
- `decision_proposal`
- `documentation_draft`
- `backlog_proposal`
- `rag_summary`
- `clarification_note`

Statuts autorisés pour la création :

- `draft`
- `to_review`

`validated`, `rejected` et `archived` relèvent d'un workflow futur et ne sont pas créés directement.

## Nommage

Format :

```text
YYYY-MM-DD_inbox_<slug>.md
```

Le slug vient du titre, en minuscules, avec caractères Windows interdits et séparateurs de chemin neutralisés.

En cas de collision, VIVI ajoute un suffixe :

```text
_001
_002
```

## Sécurité

Le module interne d'écriture :

- écrit uniquement dans `92_inbox/` ;
- exige que le vault et `92_inbox/` existent déjà ;
- crée uniquement des fichiers Markdown ;
- refuse les titres vides ou sans caractères sûrs ;
- neutralise les chemins dangereux dans le nom de fichier ;
- refuse les statuts et types inconnus ;
- refuse une détection simple de contenu sensible explicite ;
- ne modifie jamais une note existante hors création d'un nouveau nom unique.

L'appelant ne doit jamais fournir de secret, clé API, token, mot de passe ou credential dans le titre, le corps ou les métadonnées.

## Non-indexation

Les notes inbox restent non indexées par défaut :

- par emplacement : `92_inbox/` est exclu du RAG ;
- par frontmatter : `index: false`.

La FEAT-28 ne modifie pas le RAG et n'ajoute aucune indexation automatique.

## Endpoint API

Endpoint explicite :

```text
POST /obsidian/inbox
```

Cet endpoint utilise la fonction interne `create_inbox_note(...)`. Il crée une proposition dans `92_inbox/`, sans validation, promotion ni indexation.

Payload minimal :

```json
{
  "title": "Synthèse accès LAN",
  "body": "Contenu proposé à relire."
}
```

Payload complet possible :

```json
{
  "title": "Synthèse accès LAN",
  "body": "Contenu proposé à relire.",
  "note_type": "conversation_summary",
  "status": "draft",
  "related": ["VIVI LAN"],
  "prompt_summary": "Synthèse demandée explicitement par l'utilisateur.",
  "confidence": "draft",
  "source_paths": ["docs/LAN_LOCAL_ACCESS.md"]
}
```

Réponse :

```json
{
  "created": true,
  "relative_path": "92_inbox/2026-05-07_inbox_synthese-acces-lan.md",
  "filename": "2026-05-07_inbox_synthese-acces-lan.md",
  "note_type": "conversation_summary",
  "status": "draft",
  "index": false,
  "review_required": true
}
```

La réponse ne renvoie pas le corps complet de la note.

## Auth API

L'endpoint respecte l'auth locale existante :

- si `VIVI_API_KEY` est configurée, fournir `Authorization: Bearer <clé>` ou `X-VIVI-API-Key: <clé>` ;
- si `VIVI_API_KEY` est vide, le comportement existant du projet est conservé.

Ne pas écrire de clé réelle dans la documentation, les tests ou les notes.

## Usages

Usages prévus :

- synthèse de conversation ;
- proposition de décision ;
- brouillon de documentation ;
- proposition de backlog ;
- résumé RAG ;
- clarification utilisateur.

## Limites

FEAT-28 expose uniquement une action API explicite et minimale.

Elle n'ajoute pas :

- bouton UI ;
- écriture automatique après chat ;
- promotion ou validation automatique ;
- modification de notes sources.

## Prochaine étape possible

FEAT-29 pourra discuter une action UI explicite ou un workflow de validation humaine, sans automatisme implicite.
