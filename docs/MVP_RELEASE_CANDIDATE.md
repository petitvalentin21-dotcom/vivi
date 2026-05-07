# VIVI MVP local — Release Candidate

Statut : Release Candidate MVP locale.

Cette note verrouille l'état MVP manipulable de VIVI. Elle ne définit pas de nouvelle fonctionnalité produit. Elle sert à vérifier que le repo peut être lancé, testé, transmis et reproduit localement.

## 1. Statut actuel du MVP

VIVI MVP local est considéré Release Candidate si les validations automatisées, le smoke réel et la validation navigateur sont OK dans un environnement local avec LM Studio lancé.

État fonctionnel couvert :

- backend FastAPI local ;
- interface web dédiée simple ;
- provider LM Studio local prioritaire ;
- chat local ;
- mode document ;
- RAG Obsidian lexical ;
- sources visibles ;
- runtime status ;
- mémoire session simple ;
- reset conversation ;
- sécurité API key simple ;
- smoke backend ;
- documentation locale ;
- fonctionnement local-first.

## 2. Périmètre inclus

Le MVP inclut uniquement :

- lancement local du backend ;
- interface web principale accessible depuis le navigateur ;
- discussion simple avec un modèle servi par LM Studio ;
- mode document basé sur le vault Obsidian ;
- recherche lexicale dans les notes Markdown ;
- affichage des sources quand un contexte documentaire est trouvé ;
- endpoint `/health` ;
- endpoint `/runtime/info` ;
- endpoint `/chat` ;
- endpoint `/knowledge/search` ;
- endpoints de session simples ;
- reset conversation côté interface ;
- auth locale par `VIVI_API_KEY` si configurée ;
- smoke script local ;
- documentation de lancement et validation.

## 3. Périmètre exclu

Sont volontairement exclus de cette Release Candidate :

- agents spécialisés ;
- orchestrateur multi-agent ;
- runtime skills ;
- auto-amélioration ;
- appel Codex depuis VIVI ;
- provider registry ;
- priorité Ollama ;
- provider OpenAI ou Mammouth ;
- fallback externe ;
- vector DB ;
- embeddings obligatoires ;
- Open WebUI comme interface principale ;
- cockpit avancé ;
- app mobile ;
- VPN ;
- multi-utilisateur ;
- refonte UI ;
- nouvelle architecture ;
- écriture automatique dans Obsidian ;
- copie depuis `F:\VIVI_IA`.

## 4. Configuration locale attendue

Créer `.env` depuis `.env.example` :

```bash
copy .env.example .env
```

Configuration recommandée :

```env
VIVI_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
VIVI_LMSTUDIO_MODEL=google/gemma-4-e4b
VIVI_API_KEY=
VIVI_LMSTUDIO_API_KEY=
VIVI_KNOWLEDGE_VAULT_PATH=knowledge_vault
```

Règles :

- `VIVI_API_KEY` protège l'API VIVI.
- `VIVI_LMSTUDIO_API_KEY` sert uniquement si LM Studio exige une clé provider.
- Ne jamais utiliser `VIVI_API_KEY` comme clé provider LM Studio.
- `.env` reste local et ignoré par Git.
- `.env.example` est versionné et ne doit contenir aucun secret.

## 5. Checklist de validation finale

- Dépendances installées.
- `.env` présent localement.
- Aucun secret versionné.
- LM Studio Local Server lancé.
- Modèle configuré disponible dans LM Studio.
- Backend lancé.
- `GET /health` OK.
- `GET /runtime/info` OK.
- Provider LM Studio disponible.
- Vault Obsidian détecté.
- Notes détectées.
- IHM accessible.
- Mode chat OK.
- Mode document OK.
- Sources visibles OK.
- Reset conversation OK.
- Auth API key OK si activée.
- Smoke backend OK.
- Pytest complet OK.

## 6. Commandes de tests automatisés

Tests UI ciblés :

```bash
pytest -q tests/test_web_interface.py
```

Suite complète :

```bash
pytest -q
```

Les tests automatisés utilisent des mocks et ne doivent pas exiger LM Studio réel.

## 7. Commandes de smoke réel

Prérequis : backend lancé, LM Studio Local Server lancé, modèle chargé.

Sans auth :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --verbose
```

Avec auth VIVI activée :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --api-key "<VIVI_API_KEY>"
```

Le smoke doit valider `/health`, `/runtime/info`, le provider LM Studio, le modèle, `/knowledge/search`, le chat simple, le mode document et les sources quand disponibles.

## 8. Validation navigateur

Ouvrir :

- http://127.0.0.1:8000/

Valider manuellement :

1. Le runtime status est visible.
2. Le provider affiché est LM Studio.
3. Le modèle affiché correspond à `.env`.
4. Un message en mode chat reçoit une réponse.
5. Un message en mode document reçoit une réponse.
6. Les sources sont visibles quand le RAG trouve du contexte.
7. Le reset conversation vide la conversation et repart proprement.
8. Si `VIVI_API_KEY` est activée, l'IHM demande ou utilise correctement la clé locale.

## 9. Critères de succès

La Release Candidate est valide si :

- `pytest -q tests/test_web_interface.py` passe ;
- `pytest -q` passe ;
- le smoke réel retourne un résumé sans fail critique ;
- `/runtime/info` indique un provider LM Studio disponible ;
- le modèle configuré est chargé ;
- le vault existe et des notes sont détectées ;
- le mode chat fonctionne ;
- le mode document fonctionne ;
- les sources documentaires sont visibles quand disponibles ;
- aucune clé ou secret n'est exposé ;
- aucun appel externe ou fallback externe n'est utilisé.

## 10. Critères de non-release

Ne pas considérer la release prête si :

- la suite `pytest -q` échoue ;
- le smoke réel échoue sur `/health`, `/runtime/info`, chat ou document ;
- LM Studio n'est pas disponible alors que la release doit être validée en réel ;
- le modèle configuré n'est pas chargé ;
- le vault Obsidian n'est pas détecté ;
- les sources ne sont jamais visibles en mode document avec une requête pertinente ;
- l'auth API key bloque sans diagnostic clair ;
- `.env` ou un secret est versionné ;
- une fonctionnalité post-MVP a été introduite dans le chemin actif.

## 11. Risques connus

- Le smoke réel dépend de LM Studio Local Server et du modèle local réellement chargé.
- Les performances et la qualité des réponses dépendent du modèle local choisi.
- Le RAG est lexical : il est explicable, mais moins souple qu'une recherche vectorielle post-MVP.
- L'usage réseau reste local-first ; exposition LAN ou distante demande une validation sécurité séparée.
- L'auth API key est volontairement simple et n'est pas une gestion multi-utilisateur.

## 12. Prochaine étape recommandée

Après validation Release Candidate, créer un checkpoint Git contrôlé du MVP local, puis ouvrir une phase post-MVP séparée uniquement si une évolution est explicitement priorisée.
