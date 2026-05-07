# Audit RAG sur vault réel

## Statut

Audit FEAT-22 réalisé sur le vault réel `knowledge_vault/`.

Objectif : observer le comportement du RAG lexical actuel sans modifier le moteur, le scoring, la sélection des sources, le backend, l'API, l'IHM ou les prompts.

## Méthode

- Lecture du vault réel avec `load_markdown_notes`.
- Chunking avec `split_into_chunks`.
- Recherche avec `retrieve_lexical`.
- `top_k=5`.
- Aucun appel LM Studio.
- Aucune écriture dans `knowledge_vault/`.

État indexé pendant l'audit :

- Notes indexées : 5.
- Chunks générés : 148.
- Questions testées : 15.

## Commandes utilisées

```bash
python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5 --output tmp/rag_real_vault_audit_raw.md
python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5 --format json --output tmp/rag_real_vault_audit_raw.json
pytest -q tests/test_rag_validation.py
pytest -q
```

## Résumé exécutif

Le RAG lexical retrouve correctement les grandes notes produit et backend lorsque la question contient des termes proches du contenu source : MVP, endpoints, runtime, sources visibles, Obsidian.

Les principales limites observées sont :

- plusieurs résultats pertinents mais redondants dans le même document ;
- extraits parfois décalés autour du mot-clé au lieu de contenir la réponse complète ;
- rappel incomplet quand une question vise une information présente hors du vault, par exemple la release candidate ou l'audit UX réel dans `docs/` ;
- requêtes de configuration locale avec scores faibles malgré une bonne source trouvée ;
- questions ambiguës dominées par la note backend quand un terme apparaît très souvent.

Le cas hors contexte sans recouvrement lexical est correctement vide.

## Questions testées

| ID | Question | Résultat attendu | Sources retournées | Score max | Pertinence | Problème observé | Décision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Quel est l'objectif du MVP VIVI ? | Note de cadrage produit | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 25.5 | bon | Source produit présente, mais plusieurs chunks voisins et extrait partiel | Baseline OK |
| P2 | Qu'est-ce qui est hors scope du MVP VIVI ? | Exclusions MVP | `00_product/VIVI_MVP_CADRAGE_v0.1.md` | 27.0 | bon | Bon document, mais top 1 sur tests MVP avant section hors scope | Améliorer précision d'extrait plus tard |
| P3 | Quel est le statut de la release candidate locale ? | Source release candidate | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 12.0 | incomplet | `docs/MVP_RELEASE_CANDIDATE.md` n'est pas dans le vault indexé | Décider si docs doivent être indexés ou copiés manuellement dans le vault |
| B1 | Quels endpoints FastAPI existent pour health runtime chat et knowledge search ? | Spec backend endpoints | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 8.0 | acceptable | Bonne source backend présente, mais produit remonte avant backend | Prioriser pondération section/path plus tard |
| B2 | A quoi sert GET /runtime/info ? | Section runtime info | `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 16.0 | bon | Source et extrait utiles | Baseline OK |
| B3 | A quoi sert GET /knowledge/search ? | Section knowledge search | `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 18.0 | bon | Source et extrait utiles | Baseline OK |
| R1 | Quel est le role du vault Obsidian dans le mode document ? | Cadrage ou spec sur Obsidian/document | `00_product/VIVI_MVP_CADRAGE_v0.1.md` | 23.5 | acceptable | Produit trouvé, backend absent du top 5 | Améliorer rappel multi-doc plus tard |
| R2 | Quelles sont les limites du RAG lexical actuel ? | Limites lexicales, embeddings/vector DB hors MVP | `00_product/VIVI_MVP_CADRAGE_v0.1.md` | 16.5 | acceptable | Section pertinente présente mais pas en top 1 | Améliorer extraction autour section cible |
| C1 | Comment configurer VIVI_API_KEY VIVI_LMSTUDIO_API_KEY et VIVI_KNOWLEDGE_VAULT_PATH ? | Variables d'environnement | `02_architecture/VIVI — Backend MVP Spec v0.1.md`, `00_product/VIVI_MVP_CADRAGE_v0.1.md` | 4.0 | incomplet | Source correcte mais mauvais chunks et scores faibles | Prioriser exact match variables/config |
| U1 | Comment l'interface web affiche-t-elle la conversation les sources et le runtime status ? | Cadrage IHM/sources/runtime | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md`, `04_backlog/FEAT-04_backlog_item.md` | 31.0 | acceptable | Sources utiles, mais audit UX réel dans `docs/` non indexé | Clarifier périmètre indexé |
| H1 | xylophrax qztnombr wugplest | Aucune source | Aucune | 0 | hors contexte correctement vide | Aucun bruit observé | Conserver comme garde-fou |
| A1 | MVP | Sources produit/backend raisonnables | `02_architecture/VIVI — Backend MVP Spec v0.1.md` uniquement | 42.0 | bruité | Terme très fréquent, top 5 dominé par backend | Prioriser diversité documentaire |
| A2 | sources | Notes liées aux sources visibles | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 16.0 | bon | Extraits utiles sur sources visibles | Baseline OK |
| A3 | runtime | Notes backend ou produit runtime | `02_architecture/VIVI — Backend MVP Spec v0.1.md`, `00_product/VIVI_MVP_CADRAGE_v0.1.md` | 15.5 | bon | Source top 1 exacte | Baseline OK |
| A4 | document | Notes mode document/RAG/cadrage | `00_product/VIVI_MVP_CADRAGE_v0.1.md`, `02_architecture/VIVI — Backend MVP Spec v0.1.md` | 16.0 | acceptable | Sources raisonnables, extrait top 1 trop générique | Améliorer section/extrait |

## Extraits représentatifs

- P1 : l'objectif MVP retourne bien le cadrage produit, mais l'extrait commence au milieu d'une liste : "comprendre quelles sources ont été utilisées ; voir l'état du système...".
- B2 : `/runtime/info` retourne un extrait directement exploitable : "fournir à l'interface l'état du système" puis les champs attendus.
- B3 : `/knowledge/search` retourne la section exacte avec `query`, `results`, `source_id`, `path`, `title`, `section`, `score`, `excerpt`.
- C1 : la configuration locale retourne la spec backend mais pas la section variables d'environnement en tête ; les scores restent bas entre 2.5 et 4.0.
- H1 : la requête hors contexte ne retourne aucune source.
- A1 : la requête `MVP` retourne cinq chunks backend, ce qui est borné mais peu diversifié.

## Observations

### Résultats bons

- Les questions explicites sur `/runtime/info`, `/knowledge/search`, `sources` et `runtime` sont bien ancrées.
- Les sources retournées contiennent les chemins, sections, scores et extraits attendus.
- Le cas hors contexte sans recouvrement lexical est stable et vide.

### Résultats bruités

- `MVP` est trop générique et favorise plusieurs chunks du même document backend.
- Les questions UX remontent des sources utiles mais aussi une note backlog, faute de document UX dans le vault indexé.
- Les résultats peuvent être redondants : plusieurs chunks du même document occupent le top 5.

### Résultats incomplets

- La release candidate locale est documentée dans `docs/MVP_RELEASE_CANDIDATE.md`, hors `knowledge_vault/`, donc le RAG réel ne la retrouve pas.
- L'audit UX réel est dans `docs/MVP_UX_AUDIT.md`, hors vault, donc les questions UX ne peuvent pas s'appuyer dessus.
- La configuration `.env` est mieux documentée dans `README.md` et `docs/`, mais ces fichiers ne sont pas dans le vault.

### Titres et sections

- Les sections sont bien conservées et utiles dans les résultats.
- La sélection ne favorise pas toujours la section la plus précise : une section générale peut dépasser une section dédiée si elle contient davantage de tokens de la requête.
- Les titres extraits depuis le premier H1 restent parfois trop génériques pour représenter chaque section.

## Limites du RAG actuel

- Pas de seuil minimal de score : toute source avec score positif peut être retournée.
- Pas de diversité documentaire : un même fichier peut saturer le top 5.
- Pas de normalisation sémantique : "release candidate" ne trouve pas un document absent du vault, et les synonymes restent limités.
- Pas de priorité explicite aux sections exactes par rapport aux chunks riches en tokens.
- Extraits courts parfois coupés au mauvais endroit.
- Les documents utiles hors vault ne sont pas consultables par le RAG.

## Améliorations candidates

1. Ajouter une règle de diversité documentaire dans le top K pour éviter cinq chunks du même fichier.
2. Ajouter un seuil minimal de score ou un indicateur de confiance faible pour limiter les fausses sources faibles.
3. Améliorer la construction d'extraits autour des headings et phrases complètes.
4. Renforcer les exact matches sur variables techniques, endpoints et chemins.
5. Ajouter une option contrôlée d'indexation de certains documents `docs/` ou créer une copie validée dans le vault si le produit doit les interroger.
6. Ajouter une pondération plus forte pour la section exacte et le chemin attendu.
7. Ajouter des stopwords français/anglais pour réduire le bruit des requêtes longues.

## Priorités recommandées

1. Diversité documentaire du top K.
2. Seuil de confiance ou marquage `faible confiance`.
3. Extraits par phrase/section plus lisibles.
4. Exact match technique pour endpoints, variables `.env` et chemins.
5. Décision documentaire sur l'indexation des fichiers `docs/`.

## Non-modifications confirmées

- Aucun changement de l'algorithme RAG.
- Aucun changement du scoring.
- Aucun changement de sélection des sources.
- Aucun changement backend, API, IHM, auth, sessions, provider LM Studio ou prompts système.
- Aucun embedding ajouté.
- Aucune vector DB ajoutée.
- Aucun appel LM Studio.
- Aucune écriture dans `knowledge_vault/`.
- Aucun agent, orchestrateur, provider externe, fallback externe, runtime skill, cockpit, app mobile, VPN ou multi-utilisateur ajouté.

## Script

Script reproductible :

```bash
python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5
```

Sortie Markdown vers `tmp/` :

```bash
python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5 --output tmp/rag_real_vault_audit_raw.md
```

Sortie JSON vers `tmp/` :

```bash
python scripts/audit_rag_real_vault.py --vault knowledge_vault --top-k 5 --format json --output tmp/rag_real_vault_audit_raw.json
```
