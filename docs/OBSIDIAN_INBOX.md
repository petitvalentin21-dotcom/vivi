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

La FEAT-27 ne modifie pas le RAG et n'ajoute aucune indexation automatique.

## Usages

Usages prévus :

- synthèse de conversation ;
- proposition de décision ;
- brouillon de documentation ;
- proposition de backlog ;
- résumé RAG ;
- clarification utilisateur.

## Limites

FEAT-27 expose uniquement une fonction interne testable.

Elle n'ajoute pas :

- endpoint API ;
- bouton UI ;
- écriture automatique après chat ;
- promotion ou validation automatique ;
- modification de notes sources.

## Prochaine étape possible

FEAT-28 pourra définir une indexation sélective de notes validées, sous validation humaine explicite.
