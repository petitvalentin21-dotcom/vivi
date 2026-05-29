---
title: VIVI — Backend MVP Spec v0.1
status: archived
doc_type: architecture
scope: mvp
llm_index: false
llm_role: architecture
llm_priority: high
updated: 2026-05-12
tags:
  - vivi
  - mvp
  - backend
  - fastapi
  - lm-studio
  - rag
---

## 1. Statut du document

Ce document définit la spécification technique du backend MVP de VIVI.

Il complète le cadrage produit :

- knowledge_vault/00_product/VIVI_MVP_CADRAGE_v0.1.md

Il doit guider la première implémentation backend du nouveau repo VIVI.

Ce document prime sur les patterns du legacy VIVI_IA lorsque ceux-ci introduisent de la complexité non MVP.

---

# 2. Objectif backend MVP

Le backend MVP doit fournir un socle simple permettant à VIVI de :

- exposer une API locale ;
- communiquer avec LM Studio ;
- répondre à un message utilisateur ;
- lire le vault Obsidian ;
- récupérer un contexte documentaire simple ;
- afficher les sources utilisées ;
- exposer un runtime status ;
- gérer une mémoire de session simple ;
- appliquer une protection locale simple ;
- retourner des erreurs lisibles.

Le backend MVP ne doit pas implémenter :

- agents spécialisés ;
- orchestrateur multi-agent complexe ;
- runtime skills ;
- provider registry complexe ;
- fallback externe automatique ;
- vector DB obligatoire ;
- auto-amélioration ;
- interface cockpit avancée.

---

# 3. Principes techniques

## 3.1 Local-first

Le backend fonctionne localement par défaut.

Aucun appel externe ne doit être effectué sans configuration explicite.

## 3.2 LM Studio prioritaire

Le provider MVP est LM Studio.

LM Studio est appelé comme une API locale OpenAI-compatible.

Endpoint par défaut recommandé :

- http://localhost:1234/v1

Le backend doit permettre de configurer :

- base URL ;
- nom du modèle ;
- timeout.

## 3.3 Architecture simple

Le backend doit être découpé en modules simples.

Pas d’abstraction complexe sans besoin MVP immédiat.

## 3.4 RAG explicable

Le RAG MVP doit rester simple :

- lecture Markdown ;
- parsing frontmatter minimal ;
- chunking simple ;
- recherche lexicale ;
- score explicable ;
- sources visibles.

Pas d’embeddings obligatoires au MVP.

## 3.5 Erreurs lisibles

Toute erreur importante doit être retournée dans un format stable et compréhensible.

Exemples :

- LM Studio indisponible ;
- modèle non configuré ;
- vault introuvable ;
- aucune source pertinente ;
- requête non autorisée ;
- payload trop grand ;
- erreur interne safe.

---

# 4. Architecture backend MVP

Structure logique recommandée :

- API layer
  - endpoints HTTP ;
  - auth simple ;
  - validation requêtes ;
  - erreurs safe.

- LLM layer
  - client LM Studio ;
  - healthcheck ;
  - chat completion ;
  - timeout et erreurs lisibles.

- Knowledge layer
  - lecture du vault ;
  - parsing Markdown ;
  - chunking ;
  - recherche lexicale ;
  - sources.

- Session layer
  - mémoire courte ;
  - création session ;
  - récupération session ;
  - suppression session.

- Runtime layer
  - statut serveur ;
  - statut provider ;
  - statut vault ;
  - configuration non sensible.

---

# 5. Structure de fichiers recommandée

Structure backend initiale :

- app/
  - __init__.py
  - main.py
  - config.py
  - api/
    - __init__.py
    - server.py
    - schemas.py
    - errors.py
    - auth.py
  - llm/
    - __init__.py
    - lmstudio.py
  - knowledge/
    - __init__.py
    - markdown_loader.py
    - chunker.py
    - lexical_retriever.py
    - sources.py
  - sessions/
    - __init__.py
    - store.py
  - runtime/
    - __init__.py
    - status.py
- tests/
  - test_health.py
  - test_runtime_info.py
  - test_auth.py
  - test_chat_contract.py
  - test_lmstudio_client.py
  - test_knowledge_loader.py
  - test_lexical_retriever.py
  - test_sessions.py
- scripts/
  - smoke_backend.py
- data/
  - runtime/
- docs/
- knowledge_vault/

Cette structure peut évoluer, mais la FEAT-01 doit rester minimale.

---

# 6. Configuration MVP

## 6.1 Variables d’environnement

Variables recommandées :

- VIVI_HOST
  - défaut : 127.0.0.1
  - rôle : interface d’écoute backend

- VIVI_PORT
  - défaut : 8000
  - rôle : port API

- VIVI_API_KEY
  - défaut : vide
  - rôle : active la protection simple si défini

- VIVI_LMSTUDIO_BASE_URL
  - défaut : http://localhost:1234/v1
  - rôle : base URL LM Studio OpenAI-compatible

- VIVI_LMSTUDIO_MODEL
  - défaut : google/gemma-4-e4b
  - rôle : modèle à utiliser

- VIVI_LLM_TIMEOUT_SECONDS
  - défaut : 60
  - rôle : timeout appels LM Studio

- VIVI_KNOWLEDGE_VAULT_PATH
  - défaut : knowledge_vault
  - rôle : chemin du vault Obsidian

- VIVI_SESSION_STORE_PATH
  - défaut : data/runtime/sessions.json
  - rôle : persistance session simple

- VIVI_MAX_REQUEST_BYTES
  - défaut : 1048576
  - rôle : protection payload

- VIVI_RAG_TOP_K
  - défaut : 5
  - rôle : nombre maximum de sources RAG

- VIVI_EXTERNAL_PROVIDERS_ENABLED
  - défaut : false
  - rôle : verrou explicite providers externes

## 6.2 Règle providers externes

Au MVP :

- OpenAI désactivé ;
- Mammouth désactivé ;
- aucun fallback externe ;
- aucune clé externe requise.

La variable VIVI_EXTERNAL_PROVIDERS_ENABLED doit rester false par défaut.

---

# 7. Endpoints API MVP

## 7.1 GET /health

Objectif :

- vérifier que le serveur répond.

Réponse 200 :

- status : ok
- service : vivi
- version : valeur simple
- local_first : true

Exemple conceptuel :

- status: ok
- service: vivi
- version: 0.1.0
- local_first: true

## 7.2 GET /runtime/info

Objectif :

- fournir à l’interface l’état du système.

Réponse attendue :

- service
- version
- local_first
- auth_enabled
- provider
  - name
  - base_url
  - model
  - available
  - error
- vault
  - path
  - exists
  - notes_count
  - indexed
  - error
- sessions
  - enabled
  - store_path
- rag
  - enabled
  - mode
  - top_k
- external_providers_enabled

Règles :

- ne jamais exposer de secret ;
- ne jamais exposer VIVI_API_KEY ;
- base_url locale autorisée ;
- erreurs lisibles.

## 7.3 POST /chat

Objectif :

- endpoint principal de chat VIVI.

Requête :

- message : texte utilisateur obligatoire
- session_id : optionnel
- mode : optionnel
  - chat
  - document
  - diagnostic
- use_rag : optionnel
- max_sources : optionnel

Comportement :

- si mode absent, défaut : chat
- si use_rag absent :
  - true pour mode document
  - false pour mode chat
- si session_id absent :
  - créer ou utiliser une session temporaire selon implémentation MVP

Réponse :

- answer
- session_id
- provider
  - name
  - model
- mode
- sources
- runtime
  - rag_used
  - sources_count
  - external_call_used
- error null si succès

Règles :

- external_call_used doit être false au MVP ;
- si RAG utilisé, sources doit lister les notes utilisées ;
- si aucune source pertinente, le backend doit l’indiquer clairement.

## 7.4 GET /sessions

Objectif :

- lister les sessions connues.

Réponse :

- sessions
  - session_id
  - created_at
  - updated_at
  - messages_count

MVP :

- endpoint utile mais peut rester simple ;
- pas de dashboard mémoire avancé.

## 7.5 GET /sessions/{session_id}

Objectif :

- inspecter une session.

Réponse :

- session_id
- created_at
- updated_at
- messages

Règle :

- ne pas exposer de secrets ;
- messages limités si nécessaire.

## 7.6 DELETE /sessions/{session_id}

Objectif :

- supprimer une session.

Réponse :

- deleted : true
- session_id

## 7.7 GET /knowledge/search

Objectif :

- endpoint de debug contrôlé pour tester le RAG.

Paramètres :

- q : requête
- top_k : optionnel

Réponse :

- query
- results
  - source_id
  - path
  - title
  - section
  - score
  - excerpt

Règles :

- endpoint utile pour validation MVP ;
- pas destiné à être une API publique avancée.

---

# 8. Contrat LM Studio

## 8.1 Type d’intégration

Le backend VIVI appelle LM Studio via l’API locale OpenAI-compatible.

Endpoint cible :

- VIVI_LMSTUDIO_BASE_URL + /chat/completions

Avec base URL par défaut :

- http://localhost:1234/v1

## 8.2 Requête minimale vers LM Studio

Le client LM Studio doit envoyer :

- model
- messages
- temperature optionnel
- max_tokens optionnel

Messages :

- system message VIVI minimal ;
- contexte Obsidian si RAG utilisé ;
- historique session limité ;
- message utilisateur.

## 8.3 Healthcheck LM Studio

Le healthcheck doit vérifier au minimum :

- le serveur LM Studio répond ;
- si possible, /models retourne une réponse ;
- le modèle configuré est présent si la liste est disponible.

Si la vérification modèle n’est pas fiable, indiquer :

- available: unknown
- error: message lisible

## 8.4 Erreurs LM Studio

Cas à gérer :

- serveur indisponible ;
- timeout ;
- modèle absent ;
- réponse invalide ;
- réponse vide ;
- erreur HTTP.

Ces erreurs doivent être converties en erreurs VIVI lisibles.

---

# 9. RAG Obsidian MVP

## 9.1 Objectif

Permettre à VIVI d’interroger le vault Obsidian du nouveau repo.

## 9.2 Chemin du vault

Chemin par défaut :

- knowledge_vault

Variable :

- VIVI_KNOWLEDGE_VAULT_PATH

## 9.3 Fichiers inclus

Inclure :

- fichiers .md ;
- notes dans 00_product ;
- notes dans 01_user_docs ;
- notes dans 02_architecture ;
- notes dans 03_decisions ;
- notes dans 04_backlog si utile ;
- notes dans 05_runs si utile.

Exclure par défaut :

- 90_generated si non validé ;
- 91_runtime ;
- 92_inbox sauf mode debug ;
- 99_archive sauf demande explicite ;
- .obsidian ;
- fichiers non Markdown.

## 9.4 Parsing Markdown

Extraire si possible :

- path ;
- title ;
- headings ;
- frontmatter simple ;
- tags ;
- content text ;
- modified time.

Frontmatter supporté minimalement :

- title
- tags
- status
- type
- index

Si index: false, exclure la note du RAG.

## 9.5 Chunking

Chunking simple :

- par sections Markdown si possible ;
- fallback par blocs de longueur limitée ;
- conserver le chemin et le titre ;
- conserver la section.

Un chunk doit contenir :

- chunk_id
- path
- title
- section
- content
- metadata

## 9.6 Recherche lexicale

Le retriever MVP doit utiliser une recherche simple :

- normalisation lowercase ;
- découpage mots ;
- match sur titre ;
- match sur path ;
- match sur tags ;
- match sur headings ;
- match sur contenu ;
- score explicable.

Pondération indicative :

- title match : fort
- path match : fort
- tag match : fort
- heading match : moyen
- content match : moyen
- exact phrase : bonus

Pas d’embeddings obligatoires.

## 9.7 Sources visibles

Chaque source retournée doit contenir :

- source_id
- path
- title
- section
- score
- excerpt

La réponse chat doit inclure les sources utilisées.

Le modèle ne doit pas inventer de sources.

## 9.8 Absence de source

Si aucune source pertinente n’est trouvée :

- VIVI doit répondre clairement ;
- sources doit être vide ;
- rag_used peut être true ;
- sources_count vaut 0 ;
- la réponse doit indiquer qu’aucun contexte documentaire pertinent n’a été trouvé.

---

# 10. Session memory MVP

## 10.1 Objectif

Permettre une conversation courte et inspectable.

## 10.2 Stockage

Stockage recommandé :

- data/runtime/sessions.json

Format simple :

- session_id
- created_at
- updated_at
- messages

Message :

- role
- content
- created_at
- metadata optionnelle

## 10.3 Limites

Limiter :

- nombre de messages par session ;
- taille totale du contexte envoyé au modèle ;
- taille des messages stockés.

## 10.4 Suppression

L’utilisateur doit pouvoir supprimer une session via API.

## 10.5 Non MVP

Ne pas implémenter :

- mémoire agent ;
- mémoire vectorielle ;
- mémoire long terme autonome ;
- résumé automatique persistant ;
- profil utilisateur complexe.

---

# 11. Erreurs API

## 11.1 Format d’erreur

Format stable recommandé :

- error
  - code
  - message
  - recovery_hint
  - details optional
- request_id
- status_code

Codes MVP :

- auth_required
- invalid_request
- payload_too_large
- lmstudio_unavailable
- lmstudio_timeout
- lmstudio_model_missing
- vault_not_found
- no_relevant_sources
- session_not_found
- internal_error

## 11.2 Règles

- message lisible ;
- recovery_hint utile ;
- pas de stack trace en réponse ;
- pas de secret ;
- request_id si possible.

---

# 12. Sécurité MVP

## 12.1 Auth simple

Si VIVI_API_KEY est défini :

- exiger Authorization: Bearer <token>
- ou X-VIVI-API-Key: <token>

Si VIVI_API_KEY est vide :

- auth désactivée ;
- runtime/info doit indiquer auth_enabled: false ;
- le README devra signaler que ce mode est réservé au dev local.

## 12.2 Payload limit

Limiter la taille des requêtes.

Variable :

- VIVI_MAX_REQUEST_BYTES

## 12.3 Réseau local

Le host par défaut doit être :

- 127.0.0.1

Pour exposition LAN, l’utilisateur devra configurer :

- VIVI_HOST=0.0.0.0

## 12.4 Appels externes

Au MVP :

- aucun appel externe ;
- aucun fallback externe ;
- external_call_used doit toujours être false.

---

# 13. Runtime status MVP

Le runtime status doit être conçu pour l’interface VIVI.

Informations utiles :

- serveur OK ;
- auth activée ou non ;
- provider LM Studio disponible ou non ;
- modèle configuré ;
- vault trouvé ou non ;
- nombre de notes détectées ;
- RAG activé ;
- session store disponible ;
- providers externes désactivés.

Informations à éviter :

- secrets ;
- stack traces ;
- prompts complets ;
- diagnostics trop internes ;
- détails post-MVP.

---

# 14. Tests MVP

## 14.1 Tests backend prioritaires

Créer des tests pour :

- GET /health retourne 200 ;
- GET /runtime/info ne fuite pas de secret ;
- auth activée bloque les requêtes sans clé ;
- POST /chat valide le contrat de réponse ;
- POST /chat gère LM Studio indisponible proprement ;
- loader Markdown trouve les notes ;
- retriever lexical retourne des sources ;
- retriever respecte index: false ;
- GET /knowledge/search retourne sources ;
- session créée et récupérable ;
- session supprimable.

## 14.2 Tests sans LM Studio réel

Les tests automatisés ne doivent pas dépendre d’un LM Studio réel.

Utiliser :

- mock client ;
- fake transport ;
- injection de dépendance simple.

## 14.3 Smoke test manuel

Le smoke test manuel peut vérifier un vrai LM Studio local.

Scénario :

1. lancer LM Studio ;
2. démarrer le serveur VIVI ;
3. appeler /runtime/info ;
4. appeler /chat avec une question simple ;
5. appeler /chat en mode document ;
6. vérifier les sources.

---

# 15. Ce qui peut être inspiré du legacy

Le legacy peut inspirer :

- endpoints FastAPI ;
- schémas de réponses ;
- erreurs safe ;
- auth API key ;
- session memory ;
- request limits ;
- runtime status ;
- chunking Markdown ;
- tests API/safety/session/vault.

Mais le code ne doit pas être importé directement sans décision explicite.

---

# 16. Ce qui ne doit pas être importé en FEAT-01

Ne pas importer :

- app/orchestrator ;
- app/agents ;
- app/skills ;
- app/rag/vector* ;
- app/rag/embeddings.py ;
- gateway multi-provider complète ;
- Open WebUI comme interface principale ;
- ancien knowledge_vault ;
- anciens index runtime ;
- anciens logs ;
- anciens changelogs massifs.

---

# 17. Critères d’acceptation FEAT-01 backend skeleton

La première FEAT de backend minimal doit produire uniquement un squelette testable.

Critères :

- structure app/ créée ;
- FastAPI installé ou déclaré ;
- endpoint GET /health fonctionnel ;
- endpoint GET /runtime/info fonctionnel ;
- schémas de base créés ;
- settings MVP créés ;
- client LM Studio stub ou minimal créé ;
- modules knowledge créés mais simples ;
- tests health/runtime passent ;
- aucun code legacy copié ;
- aucun agent ;
- aucun orchestrateur complexe ;
- aucun vectoriel ;
- aucun provider externe ;
- rapport Codex écrit dans tmp/.

FEAT-01 ne doit pas forcément connecter entièrement LM Studio ni finaliser le RAG.

Elle doit créer une base saine pour les FEAT suivantes.

---

# 18. Découpage recommandé après FEAT-01

## FEAT-01 — Squelette backend minimal

- structure app ;
- config ;
- health ;
- runtime info ;
- erreurs ;
- tests de base.

## FEAT-02 — Provider LM Studio

- client LM Studio ;
- healthcheck ;
- chat completion ;
- erreurs provider ;
- tests avec mock.

## FEAT-03 — Chat endpoint

- POST /chat ;
- session minimale ;
- appel LM Studio ;
- réponse contractuelle ;
- tests.

## FEAT-04 — RAG Obsidian lexical

- loader Markdown ;
- chunker ;
- retriever lexical ;
- sources ;
- /knowledge/search ;
- tests.

## FEAT-05 — Chat + RAG

- mode document ;
- injection contexte ;
- sources dans réponse ;
- no source handling ;
- tests.

## FEAT-06 — Sécurité simple

- auth API key ;
- payload limit ;
- erreurs safe ;
- tests.

## FEAT-07 — Smoke local

- script smoke ;
- README lancement ;
- validation LM Studio réelle.

---

# 19. Principe final

Le backend MVP VIVI doit rester un socle local simple :

- API locale ;
- LM Studio ;
- chat ;
- Obsidian RAG lexical ;
- sources visibles ;
- runtime status ;
- session simple ;
- sécurité simple.

Tout ce qui ressemble à un orchestrateur multi-agent, une plateforme provider, un runtime skills ou un système auto-améliorant est post-MVP.
