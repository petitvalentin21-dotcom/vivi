# Audit structure Obsidian — Vault VIVI

## 1. Statut de l'audit

Statut : audit documentaire FEAT-25, lecture seule.

Cet audit décrit l'état actuel de `knowledge_vault/` avant toute évolution d'écriture IA ou de mémoire projet. Aucune note du vault, aucun dossier Obsidian, aucun frontmatter et aucune configuration Obsidian n'ont été modifiés.

Gouvernance associée : [OBSIDIAN_WRITE_GOVERNANCE.md](OBSIDIAN_WRITE_GOVERNANCE.md).

## 2. Méthode utilisée

Méthode :

- lecture de `AGENTS.md`, `README.md`, cadrage produit et spec backend ;
- inventaire PowerShell de `knowledge_vault/` ;
- comptage des fichiers Markdown hors `.obsidian/` ;
- inspection des titres, liens, signaux frontmatter et tags ;
- comparaison avec les règles actuelles du loader RAG dans `app/knowledge/markdown_loader.py`.

Aucun script d'audit n'a été ajouté : le vault contient peu de notes et l'audit reste documentaire.

## 3. Structure actuelle du vault

Racine observée :

- `.obsidian/`
- `00_product/`
- `01_user_docs/`
- `02_architecture/`
- `03_decisions/`
- `04_backlog/`
- `05_runs/`
- `90_generated/`
- `91_runtime/`
- `92_inbox/`
- `99_archive/`
- `VIVI HOME.md`

Profondeur actuelle : faible. Les dossiers racine ne contiennent pas de sous-dossiers observés.

Fichiers non Markdown :

- uniquement des fichiers JSON de configuration Obsidian dans `.obsidian/`.
- aucun fichier non Markdown métier observé hors `.obsidian/`.

## 4. Dossiers principaux

| Dossier | Rôle observé | Notes Markdown |
| --- | --- | ---: |
| racine | note d'accueil `VIVI HOME.md` | 1 |
| `00_product/` | cadrage produit source | 1 |
| `01_user_docs/` | documentation utilisateur prévue | 0 |
| `02_architecture/` | architecture backend MVP | 1 |
| `03_decisions/` | décisions projet prévues | 0 |
| `04_backlog/` | backlog/tâches | 1 |
| `05_runs/` | run logs | 1 |
| `90_generated/` | contenu généré IA | 1 |
| `91_runtime/` | données runtime/index/logs prévues | 0 |
| `92_inbox/` | propositions à valider prévues | 0 |
| `99_archive/` | archives prévues | 0 |

Total hors `.obsidian/` : 6 notes Markdown.

## 5. Notes importantes repérées

Sources de vérité fortes :

- `00_product/VIVI_MVP_CADRAGE_v0.1.md` : cadrage produit principal.
- `02_architecture/VIVI — Backend MVP Spec v0.1.md` : spécification backend/API/RAG/sécurité MVP.
- `VIVI HOME.md` : page d'accueil et cartographie courte du vault.

Notes de pilotage ou historiques :

- `04_backlog/FEAT-04_backlog_item.md` : backlog historique FEAT-04.
- `05_runs/2026-05-06_FEAT-03_run_log.md` : run log historique FEAT-03.
- `90_generated/FEAT-03_PROJECT_STATE_2026-05-06.md` : état généré FEAT-03, non source de vérité tant que non validé.

Notes absentes du vault :

- aucune note décision validée dans `03_decisions/` ;
- aucune note utilisateur dans `01_user_docs/` ;
- pas de note LAN ou Release Candidate dans le vault : ces documents sont actuellement dans `docs/`.

## 6. Conventions observées

Conventions présentes :

- préfixes numériques pour les dossiers de gouvernance ;
- séparation claire entre sources validées (`00_product`, `02_architecture`) et zones générées/runtime/inbox/archive ;
- note d'accueil racine avec lien wiki Obsidian vers le cadrage produit ;
- titres Markdown H1 dans la plupart des notes ;
- structure par sections Markdown numérotées dans les notes longues.

Conventions peu ou pas utilisées :

- pas de frontmatter observé ;
- pas de tags Markdown ou frontmatter observés ;
- pas de champ `status`, `type` ou `index` observé ;
- pas de note index par dossier hors `VIVI HOME.md` ;
- pas de convention explicite de statut validé/brouillon dans les notes elles-mêmes.

## 7. Fichiers ou dossiers à ignorer

À ignorer systématiquement pour le RAG et les futures écritures automatiques :

- `.obsidian/` : configuration locale Obsidian ;
- `91_runtime/` : données techniques, index, logs runtime ;
- fichiers non Markdown ;
- fichiers temporaires ou générés hors zones validées.

À ignorer par défaut pour le RAG tant qu'ils ne sont pas validés :

- `90_generated/` ;
- `92_inbox/` ;
- `99_archive/`.

## 8. Zones actuellement adaptées au RAG

Très adaptées :

- `00_product/` : source produit stable et utile pour le cadrage ;
- `02_architecture/` : source technique/API/RAG/sécurité stable ;
- `VIVI HOME.md` : utile comme carte courte du projet, mais elle gagnerait à avoir un H1 explicite.

Adaptées quand elles seront peuplées avec du contenu validé :

- `01_user_docs/` ;
- `03_decisions/`.

À utiliser avec prudence :

- `04_backlog/` : utile pour planifier, mais peut contenir des intentions non réalisées ;
- `05_runs/` : utile pour l'historique, mais peut vieillir vite et polluer les réponses.

## 9. Zones risquées pour le RAG

Risques de pollution :

- `04_backlog/` : tâches anciennes ou non exécutées pouvant être confondues avec l'état réel ;
- `05_runs/` : logs ponctuels pouvant contredire l'état actuel ;
- `90_generated/` : contenu IA non validé ;
- `92_inbox/` : futures propositions non validées ;
- `99_archive/` : contenu obsolète ou historique.

État runtime actuel :

- le loader RAG inclut `00_product`, `01_user_docs`, `02_architecture`, `03_decisions`, `04_backlog`, `05_runs` et les notes Markdown de racine ;
- il exclut déjà `.obsidian`, `90_generated`, `91_runtime`, `92_inbox`, `99_archive`, `tmp` et `data`.

## 10. Zones candidates pour futures écritures IA contrôlées

Candidate principale :

- `92_inbox/` existe déjà et est vide.

Contenus futurs possibles :

- brouillons IA ;
- synthèses proposées ;
- notes à valider ;
- captures de décisions à relire ;
- résumés de conversations ;
- propositions de backlog avant intégration humaine.

Autres zones possibles avec contrôle strict :

- `90_generated/` pour exports générés non validés ;
- `91_runtime/` pour index ou journaux techniques non destinés au RAG.

Ne jamais écrire automatiquement dans :

- `00_product/` ;
- `02_architecture/` ;
- `03_decisions/` validé ;
- backlog principal validé ;
- release candidate ou documents de statut validés ;
- notes sources humaines ;
- `.obsidian/`.

## 11. Risques identifiés

- Le vault est petit : quelques notes longues dominent fortement le RAG.
- Les notes `04_backlog` et `05_runs` sont actuellement indexables et peuvent introduire de l'historique ancien.
- Absence de frontmatter `index`, `status` ou `type` : l'indexation dépend surtout du dossier.
- `90_generated` contient déjà une note générée, heureusement exclue du RAG actuel.
- `92_inbox` existe mais n'a pas encore de règle écrite de gouvernance.
- Les documents récents LAN/Release Candidate vivent dans `docs/`, pas dans Obsidian ; le RAG vault ne les voit donc pas.

## 12. Recommandations de gouvernance

Recommandations avant toute écriture IA :

- formaliser une règle unique : toute proposition IA va dans `92_inbox/` ou `90_generated/`, jamais dans les sources validées ;
- ajouter plus tard une convention de frontmatter minimale pour les nouvelles notes IA : `type`, `status`, `source`, `index`;
- garder `index: false` par défaut pour `92_inbox/`, `90_generated/`, `91_runtime/` et `99_archive/` ;
- réserver `03_decisions/` aux décisions validées manuellement ;
- traiter `04_backlog/` comme intentionnel, pas comme vérité runtime ;
- limiter l'indexation de `05_runs/` ou la rendre sélective si les logs se multiplient ;
- garder `docs/` comme documentation repo, et décider explicitement si certaines docs doivent être recopiées ou référencées dans le vault.

## 13. Décisions à prendre plus tard

Décisions ouvertes :

- faut-il indexer `04_backlog/` par défaut ou seulement certains items validés ?
- faut-il indexer `05_runs/` en permanence ou seulement en mode audit ?
- faut-il créer une note de gouvernance dans `03_decisions/` ou dans `01_user_docs/` ?
- faut-il importer une synthèse validée des docs LAN/Release Candidate dans le vault ?
- faut-il imposer `index: false` sur toutes les notes inbox/generated futures ?

## 14. Prochaines étapes proposées

- FEAT-26 — Gouvernance d'écriture Obsidian contrôlée.
- FEAT-27 — Inbox Obsidian explicite.
- FEAT-28 — Indexation sélective des notes validées.

Ces étapes ne sont pas implémentées par cet audit.
