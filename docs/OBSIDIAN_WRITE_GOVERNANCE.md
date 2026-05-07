# Gouvernance d'écriture Obsidian contrôlée

## 1. Objectif

Cette gouvernance définit les règles que VIVI devra respecter avant toute écriture future dans `knowledge_vault/`.

Elle ne crée aucun flux d'écriture. Elle sert de contrat pour les prochaines FEAT, notamment FEAT-27.

## 2. Principe directeur

VIVI propose. L'utilisateur valide. Les notes sources restent humaines et protégées.

Aucune écriture automatique ne doit modifier une source de vérité, une décision validée, une architecture validée ou une note existante sans action humaine explicite.

## 3. Zones autorisées futures

### `knowledge_vault/92_inbox/`

Usage recommandé :

- propositions IA à relire ;
- brouillons ;
- synthèses temporaires ;
- captures de décisions à valider ;
- résumés de conversation ;
- notes candidates avant intégration humaine.

Règles :

- non indexé par défaut ;
- contenu à valider manuellement ;
- aucune note créée ici ne devient source de vérité par sa seule existence.

### `knowledge_vault/90_generated/`

Usage possible :

- exports IA générés ;
- états projet générés ;
- rapports non validés ;
- contenu traçable mais non source de vérité.

Règles :

- non indexé par défaut ;
- ne devient pas vérité sans promotion humaine ;
- ne doit pas remplacer `docs/` ou les sources validées.

### `knowledge_vault/91_runtime/`

Usage possible :

- index techniques ;
- caches ;
- logs runtime ;
- diagnostics non humains.

Règles :

- jamais source de vérité ;
- non indexé ;
- contenu technique supprimable ou reconstructible.

## 4. Zones interdites

Toute écriture automatique est interdite dans :

- `knowledge_vault/00_product/`
- `knowledge_vault/01_user_docs/`, sauf validation humaine explicite future ;
- `knowledge_vault/02_architecture/`
- `knowledge_vault/03_decisions/`, sauf décision humaine explicite future ;
- `knowledge_vault/04_backlog/`, sauf validation humaine explicite future ;
- `knowledge_vault/05_runs/`, sauf décision explicite future ;
- `knowledge_vault/99_archive/`
- `knowledge_vault/.obsidian/`
- toute note source existante.

Interdictions permanentes :

- suppression automatique ;
- renommage automatique ;
- remplacement automatique d'une note ;
- modification automatique de frontmatter existant ;
- écriture de secrets.

## 5. Types de notes générables

Types autorisés plus tard, uniquement dans une zone autorisée :

- synthèse de conversation ;
- proposition de décision ;
- brouillon de documentation ;
- proposition de backlog ;
- résumé de recherche RAG ;
- note de clarification utilisateur.

Types interdits :

- décision validée automatique ;
- modification de cadrage produit ;
- modification d'architecture ;
- suppression ou remplacement de note ;
- note contenant un secret ;
- note présentée comme vérité sans validation.

## 6. Frontmatter minimal obligatoire

Toute future note générée par VIVI doit commencer par un frontmatter minimal :

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

Champs obligatoires :

- `type` : type de note générée.
- `status` : statut de validation.
- `source` : origine, par défaut `vivi`.
- `created_at` : date de création.
- `index` : autorisation d'indexation RAG.
- `review_required` : indique qu'une validation humaine est requise.

Champs optionnels :

- `related`
- `prompt_summary`
- `validated_by`
- `validated_at`
- `confidence`
- `source_paths`

## 7. Statuts autorisés

Statuts simples :

- `draft`
- `to_review`
- `validated`
- `rejected`
- `archived`

Règles :

- `draft`, `to_review`, `rejected` et `archived` ne doivent pas être indexés ;
- seul `validated` peut devenir candidat à l'indexation ;
- même `validated` ne doit pas être déplacé automatiquement dans une note source ;
- une note validée doit rester traçable comme issue d'une proposition IA.

## 8. Règles d'indexation RAG

Règles actuelles à préserver :

- `92_inbox/`, `90_generated/`, `91_runtime/` et `99_archive/` sont exclus par défaut ;
- `.obsidian/` reste ignoré ;
- les notes générées ne sont pas source de vérité par défaut.

Règles futures :

- `index: false` par défaut pour toute note générée ;
- `index: true` uniquement après validation humaine explicite ;
- ne jamais indexer les brouillons ;
- ne jamais indexer `91_runtime/` ;
- éviter les boucles où VIVI réutilise immédiatement une note qu'elle vient de générer ;
- une note promue vers l'index doit garder son origine et son statut visibles.

## 9. Validation humaine

L'utilisateur doit rester responsable de :

- relire les propositions IA ;
- corriger les erreurs ;
- accepter ou rejeter les brouillons ;
- décider si une proposition devient source documentaire ;
- décider si une note peut être indexée ;
- promouvoir manuellement le contenu vers une zone source si nécessaire.

VIVI ne doit pas :

- valider ses propres notes ;
- déclarer une proposition comme décision ;
- déplacer une note vers `00_product/`, `02_architecture/`, `03_decisions/` ou `04_backlog/` ;
- modifier une note validée pour "l'améliorer" sans demande explicite.

## 10. Règles de nommage

Nommage recommandé pour `92_inbox/` :

- `YYYY-MM-DD_inbox_<slug>.md`
- `YYYY-MM-DD_vivi_proposal_<slug>.md`

Règles :

- nom stable ;
- nom lisible ;
- aucun secret dans le nom ;
- pas de caractères Windows problématiques : `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*` ;
- suffixe unique si plusieurs notes sont créées le même jour, par exemple `_001`.

## 11. Sécurité

Règles obligatoires :

- ne jamais écrire de secret dans Obsidian ;
- ne jamais écrire de clé API, token, mot de passe ou credential ;
- ne jamais écrire de contenu sensible sans validation ;
- ne jamais modifier `.obsidian/` ;
- ne jamais supprimer ou renommer automatiquement ;
- journaliser clairement l'origine d'une note générée ;
- garder l'utilisateur responsable de la promotion vers les sources ;
- refuser toute tentative de chemin sortant de la zone autorisée.

## 12. Exemples de notes futures

Exemple de synthèse de conversation :

```markdown
---
type: conversation_summary
status: draft
source: vivi
created_at: 2026-05-07
index: false
review_required: true
related:
  - VIVI MVP
---

# Synthèse proposée — accès LAN

Résumé à relire par l'utilisateur avant toute intégration dans une note source.
```

Exemple de proposition de décision :

```markdown
---
type: decision_proposal
status: to_review
source: vivi
created_at: 2026-05-07
index: false
review_required: true
source_paths:
  - docs/OBSIDIAN_VAULT_AUDIT.md
---

# Proposition de décision — inbox IA

Proposition non validée. L'utilisateur doit décider si elle devient une vraie décision projet.
```

Ces exemples restent dans la documentation. Ils ne doivent pas être créés automatiquement dans `knowledge_vault/` par cette FEAT.

## 13. Critères d'acceptation pour FEAT-27

Si FEAT-27 ajoute une inbox Obsidian fonctionnelle, elle devra respecter :

- écriture uniquement sur action explicite ;
- écriture uniquement dans `knowledge_vault/92_inbox/` ;
- frontmatter conforme ;
- `index: false` par défaut ;
- `review_required: true` par défaut ;
- pas de modification de notes existantes ;
- pas de suppression ;
- pas de renommage ;
- tests de sécurité chemin ;
- tests anti path traversal ;
- tests de non-écriture hors inbox ;
- tests confirmant l'absence d'écriture dans `.obsidian/` ;
- aucun changement RAG implicite ;
- rapport Codex dans `tmp/`.

## 14. Prochaines étapes

- FEAT-27 — Inbox Obsidian explicite.
- FEAT-28 — Indexation sélective des notes validées.
- FEAT-29 — Promotion humaine contrôlée des propositions validées.

Ces étapes ne sont pas implémentées par ce document.
