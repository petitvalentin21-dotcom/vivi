# AGENTS.md — Règles de travail pour VIVI

## 1. Objectif du projet

VIVI est une IA locale d’assistance personnelle.

Sa fonction première est simple :

> Je lui parle, elle me répond.

Le MVP strict doit permettre :

- une interface web dédiée simple ;
- une discussion avec un modèle local via LM Studio ;
- l’interrogation d’un vault Obsidian ;
- l’affichage des sources utilisées ;
- un statut runtime clair ;
- une protection simple ;
- un fonctionnement local-first.

Tout ce qui ne sert pas directement ce MVP est considéré comme post-MVP, sauf validation explicite.

---

## 2. Source de vérité

La source de vérité produit et architecture est :

- knowledge_vault/00_product/VIVI_MVP_CADRAGE_v0.1.md

Avant toute tâche, lire ce document.

Si une demande contredit le cadrage MVP, signaler la contradiction avant de modifier le projet.

---

## 3. Statut du repo

Ce repo est un nouveau départ propre pour VIVI.

L’ancien projet VIVI_IA est considéré comme :

- laboratoire ;
- archive ;
- source d’inspiration ;
- source d’import sélectif.

L’ancien projet ne doit pas être copié intégralement.

Tout import depuis l’ancien projet doit être justifié selon les catégories :

- KEEP_MVP ;
- KEEP_POST_MVP ;
- ARCHIVE ;
- DELETE ;
- REWRITE.

---

## 4. Priorités MVP

Priorité absolue :

1. assistant local de discussion ;
2. interface dédiée simple ;
3. LM Studio comme provider local prioritaire ;
4. chat local ;
5. RAG Obsidian simple ;
6. sources visibles ;
7. runtime status ;
8. sécurité simple.

Question de contrôle avant toute fonctionnalité :

> Est-ce nécessaire pour ouvrir VIVI, parler à LM Studio, interroger Obsidian, voir les sources et obtenir une réponse fiable ?

Si la réponse est non, classer en post-MVP, backlog ou archive.

---

## 5. Hors périmètre MVP

Ne pas implémenter au MVP :

- agents spécialisés ;
- agent DEV ;
- agent PM ;
- agent ARCH ;
- agent QA ;
- agent nutrition ;
- agent finance ;
- agent maison ;
- agent auto-amélioration ;
- création automatique de skills ;
- appel Codex depuis VIVI ;
- fallback externe automatique ;
- provider registry complexe ;
- routage intelligent multi-modèles ;
- cockpit avancé ;
- app mobile ;
- VPN ;
- multi-utilisateur ;
- vector DB obligatoire ;
- écriture libre dans Obsidian.

Ces sujets peuvent être documentés en post-MVP, mais ne doivent pas complexifier le MVP.

---

## 6. Règles Obsidian

Le vault Obsidian est situé dans :

- knowledge_vault/

Règle centrale :

> Toute écriture IA va dans une zone generated/, runtime/ ou inbox/, jamais directement dans les notes sources.

Zones recommandées :

- 00_product/ : cadrage produit
- 01_user_docs/ : documentation utilisateur
- 02_architecture/ : architecture validée
- 03_decisions/ : décisions projet
- 04_backlog/ : backlog et idées
- 05_runs/ : comptes rendus
- 90_generated/ : contenus générés par IA
- 91_runtime/ : données runtime, index, logs
- 92_inbox/ : propositions à valider
- 99_archive/ : archives

Au MVP, ne jamais modifier automatiquement :

- les notes de cadrage produit ;
- les décisions validées ;
- l’architecture validée ;
- la documentation source humaine ;
- le README ;
- les fichiers de code sans demande explicite.

Les propositions doivent être écrites dans :

- knowledge_vault/92_inbox/
- ou tmp/ pour les rapports temporaires.

---

## 7. Règles de développement

Chaque tâche doit être courte, ciblée et validable.

Règles :

- une tâche = une intention claire ;
- une branche = une FEAT courte ;
- une PR = un changement cohérent ;
- pas de refonte opportuniste ;
- pas de nouvelle abstraction sans usage MVP immédiat ;
- pas de dépendance inutile ;
- pas de provider supplémentaire sans demande explicite ;
- pas de workflow agent complexe au MVP ;
- pas de modification massive non demandée ;
- pas de suppression sans justification ;
- pas de doublon documentaire.

Si une tâche semble trop large, produire un plan de découpage avant modification.

---

## 8. Règles Codex

Codex doit respecter ces règles :

- lire le cadrage MVP avant toute action ;
- ne pas commencer à coder si la tâche demandée est un audit ;
- ne pas modifier de fichiers pendant un audit en lecture seule ;
- produire les rapports dans tmp/ ;
- ne jamais écrire dans les notes sources Obsidian sans demande explicite ;
- ne jamais importer massivement l’ancien projet ;
- ne jamais ajouter de complexité post-MVP au MVP ;
- signaler les risques et ambiguïtés ;
- privilégier le code simple, lisible et testable.

---

## 9. Format de rapport Codex

Chaque tâche Codex doit produire un rapport dans :

- tmp/codex_last_report.md
- et si utile : tmp/codex_report_YYYY-MM-DD_HH-mm-ss.md

Format attendu :

# Rapport Codex

## Résumé

Résumé court de la tâche.

## Fichiers analysés

Liste des fichiers analysés.

## Fichiers modifiés

Liste des fichiers modifiés, ou Aucun si audit en lecture seule.

## Comportement ajouté

Ce qui a été ajouté.

## Comportement supprimé

Ce qui a été supprimé.

## Classement MVP

Si pertinent :

- KEEP_MVP
- KEEP_POST_MVP
- ARCHIVE
- DELETE
- REWRITE

## Tests lancés

Commandes ou validations réalisées.

## Résultat

Succès, échec ou partiel.

## Risques

Risques identifiés.

## Prochaine étape recommandée

Une seule prochaine étape recommandée.

---

## 10. Audit de l’ancien projet

Lorsqu’une tâche demande d’analyser l’ancien projet VIVI_IA :

- ne modifier aucun fichier ;
- ne copier aucun fichier ;
- ne créer aucun code ;
- produire uniquement un rapport d’audit ;
- classer chaque élément utile ;
- expliquer pourquoi il doit être gardé, réécrit, archivé, supprimé ou repoussé.

Catégories obligatoires :

### KEEP_MVP

Élément nécessaire au MVP strict.

### KEEP_POST_MVP

Élément utile plus tard, mais hors MVP.

### ARCHIVE

Élément historique utile, mais non actif.

### DELETE

Élément inutile, obsolète, redondant ou dangereux.

### REWRITE

Élément dont l’idée est utile mais dont l’implémentation doit être refaite.

---

## 11. Règles provider LLM

Provider MVP prioritaire :

- LM Studio.

Le provider doit rester simple :

- endpoint configurable ;
- modèle configurable ;
- healthcheck minimal ;
- chat completion ;
- erreurs lisibles.

Ne pas implémenter au MVP :

- registry provider complexe ;
- fallback automatique ;
- benchmark de modèles ;
- sélection intelligente de modèle ;
- routage multi-provider.

Le code peut être pensé pour ne pas bloquer Ollama plus tard, mais Ollama n’est pas prioritaire MVP.

---

## 12. Règles RAG Obsidian

Le RAG MVP doit être simple, fiable et explicable.

Priorité :

- recherche lexicale ;
- métadonnées ;
- titres ;
- chemins ;
- tags ;
- sections ;
- sources visibles.

Ne pas imposer au MVP :

- embeddings obligatoires ;
- vector DB complexe ;
- reranking avancé ;
- pipeline RAG multi-étapes lourd.

Chaque réponse documentaire doit afficher les sources Obsidian utilisées.

Si aucune source pertinente n’est trouvée, VIVI doit le dire clairement.

---

## 13. Règles mémoire

Mémoire MVP autorisée :

- mémoire de session courte ;
- mémoire projet via Obsidian ;
- préférences minimales visibles.

Mémoire non MVP :

- mémoire agent ;
- mémoire vectorielle autonome ;
- mémoire long terme opaque ;
- mémorisation automatique incontrôlée.

La mémoire doit être :

- explicite ;
- inspectable ;
- limitée ;
- supprimable ;
- séparée de la documentation source.

---

## 14. Règles sécurité

Le MVP doit inclure une protection simple.

Principes :

- local-first ;
- réseau privé uniquement ;
- aucun appel externe par défaut ;
- aucun secret dans les logs ;
- erreurs safe ;
- écriture limitée ;
- actions critiques supervisées.

Appels externes :

- OpenAI désactivé par défaut ;
- Mammouth désactivé par défaut ;
- aucun fallback externe automatique ;
- tout appel externe futur doit être visible et explicitement activé.

---

## 15. Règles interface

Interface MVP :

- web ;
- dédiée à VIVI ;
- simple ;
- une page principale ;
- design fonctionnel ;
- pas de cockpit avancé.

Elle doit afficher :

- conversation ;
- provider actif ;
- modèle actif ;
- mode actif ;
- runtime status ;
- sources utilisées ;
- erreurs lisibles.

Ne pas implémenter au MVP :

- dashboard agents ;
- éditeur de workflows ;
- gestion mémoire avancée ;
- interface multi-utilisateur ;
- cockpit admin complet.

---

## 16. Règles tests

Toute modification applicative doit être accompagnée d’une validation adaptée.

Tests MVP attendus à terme :

- serveur démarre ;
- interface accessible ;
- LM Studio détecté ;
- modèle actif affiché ;
- chat simple fonctionnel ;
- vault Obsidian détecté ;
- question documentaire fonctionnelle ;
- sources affichées ;
- erreur LM Studio indisponible lisible ;
- erreur vault absent lisible ;
- protection simple active ;
- aucun appel externe par défaut.

Si les tests ne sont pas possibles, expliquer pourquoi dans le rapport.

---

## 17. Documentation

La documentation doit rester sobre.

README.md :

- installation ;
- lancement ;
- usage rapide ;
- état du projet.

knowledge_vault/ :

- cadrage ;
- architecture ;
- décisions ;
- backlog ;
- runs ;
- propositions.

Éviter les doublons.

Si une information existe déjà dans le vault, ne pas la recopier ailleurs sans raison.

---

## 18. Interdictions générales

Ne jamais :

- importer l’ancien projet entier ;
- coder avant cadrage si la tâche est documentaire ;
- mélanger documentation humaine et données générées ;
- modifier directement les notes sources Obsidian ;
- ajouter des agents spécialisés au MVP ;
- ajouter un fallback externe automatique ;
- créer une architecture trop abstraite ;
- générer un cockpit avancé avant validation du chat + RAG ;
- ignorer le cadrage MVP ;
- supprimer des fichiers sans justification ;
- cacher une erreur bloquante.

---

## 19. Principe final

VIVI MVP doit rester simple :

- je lance VIVI ;
- j’ouvre l’interface ;
- je parle à un modèle local LM Studio ;
- VIVI peut interroger Obsidian ;
- VIVI affiche ses sources ;
- VIVI répond clairement ;
- VIVI reste local-first.

Tout le reste vient après.