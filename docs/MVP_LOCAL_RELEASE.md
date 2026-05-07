# VIVI MVP local — lancement et validation

Ce guide permet de lancer et valider VIVI MVP localement sans dépendre de l'historique de conversation.

VIVI MVP sert un objectif strict : ouvrir une interface locale, discuter avec un modèle LM Studio, interroger le vault Obsidian en mode document, afficher les sources et garder un statut runtime lisible.

## 1. Prérequis

- Python installé.
- Dépendances installées avec `pip install -r requirements.txt`.
- LM Studio installé.
- Un modèle chargé dans LM Studio, par exemple `google/gemma-4-e4b`.
- Le vault Obsidian présent dans `knowledge_vault/`.

## 2. Configurer `.env`

Créer le fichier local :

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

Variables importantes :

- `VIVI_LMSTUDIO_BASE_URL` : URL du serveur local LM Studio. `http://127.0.0.1:1234` et `http://127.0.0.1:1234/v1` sont acceptés.
- `VIVI_LMSTUDIO_MODEL` : nom exact du modèle chargé dans LM Studio.
- `VIVI_API_KEY` : clé locale optionnelle qui protège l'API VIVI.
- `VIVI_LMSTUDIO_API_KEY` : clé éventuelle du provider LM Studio si LM Studio demande une authentification.
- `VIVI_KNOWLEDGE_VAULT_PATH` : chemin du vault Obsidian utilisé par le RAG lexical.

Règles de sécurité :

- Ne jamais utiliser `VIVI_API_KEY` comme clé provider LM Studio.
- Ne renseigner `VIVI_LMSTUDIO_API_KEY` que si LM Studio l'exige.
- Ne jamais commiter `.env`.
- Ne jamais mettre de secret dans `.env.example`.

## 3. Lancer LM Studio Local Server

1. Ouvrir LM Studio.
2. Charger le modèle configuré dans `VIVI_LMSTUDIO_MODEL`.
3. Démarrer le Local Server.
4. Vérifier que le serveur écoute sur `http://127.0.0.1:1234`.

Le backend VIVI ajoute automatiquement `/v1` si nécessaire pour les appels OpenAI-compatible.

## 4. Lancer le backend

```bash
uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Ouvrir l'interface :

- http://127.0.0.1:8000/

Endpoints de contrôle :

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/runtime/info

Si `VIVI_API_KEY` est renseignée, les appels protégés doivent envoyer :

```text
Authorization: Bearer <VIVI_API_KEY>
```

ou :

```text
X-VIVI-API-Key: <VIVI_API_KEY>
```

## 5. Tester l'IHM locale

Dans l'interface web :

1. Vérifier que le runtime est visible.
2. Vérifier que le provider est `lmstudio`.
3. Vérifier que le modèle affiché correspond à `.env`.
4. Envoyer un message en mode chat.
5. Passer en mode document.
6. Poser une question sur le projet ou l'architecture.
7. Vérifier que des sources sont visibles quand le RAG trouve du contexte.
8. Utiliser le reset conversation.
9. Vérifier que la conversation repart proprement.

## 6. Tester en ligne de commande

Chat simple :

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour VIVI","mode":"chat"}'
```

Mode document avec sources :

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quels sont les objectifs du MVP ?","mode":"document","max_sources":3}'
```

Recherche Obsidian directe :

```bash
curl "http://127.0.0.1:8000/knowledge/search?q=architecture&top_k=5"
```

Avec auth VIVI activée, ajouter l'en-tête `Authorization: Bearer <VIVI_API_KEY>`.

## 7. Smoke backend

Backend et LM Studio doivent être lancés avant le smoke réel.

Sans auth :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --verbose
```

Avec auth VIVI :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --api-key "<VIVI_API_KEY>"
```

Le smoke vérifie :

- `/health` ;
- `/runtime/info` ;
- disponibilité provider LM Studio ;
- modèle configuré ;
- recherche knowledge ;
- chat simple ;
- mode document ;
- sources documentaires quand disponibles.

## 8. Checklist release MVP locale

- Serveur VIVI lancé.
- `/health` OK.
- `/runtime/info` OK.
- LM Studio provider disponible.
- Modèle configuré et chargé.
- Vault Obsidian détecté.
- Notes Obsidian détectées.
- IHM accessible.
- Chat simple OK.
- Mode document OK.
- Sources visibles OK.
- Reset conversation OK.
- Auth API key OK si activée.
- Smoke backend OK.
- `pytest -q` OK.

## 9. Diagnostics rapides

### Backend inaccessible

Vérifier que `uvicorn app.api.server:app --host 127.0.0.1 --port 8000` est lancé et que l'URL utilisée est `http://127.0.0.1:8000`.

### Auth refusée

Si `runtime/info` indique `auth_enabled=true`, fournir `Authorization: Bearer <VIVI_API_KEY>` ou `X-VIVI-API-Key: <VIVI_API_KEY>`.

### Modèle non configuré

Renseigner `VIVI_LMSTUDIO_MODEL` dans `.env`, avec le nom exact du modèle chargé dans LM Studio, puis redémarrer le backend.

### Provider LM Studio indisponible

Vérifier que LM Studio Local Server est lancé, que `VIVI_LMSTUDIO_BASE_URL` pointe vers le bon port et que le modèle est chargé.

### Aucune source visible

Vérifier `VIVI_KNOWLEDGE_VAULT_PATH`, le nombre de notes dans `/runtime/info`, puis tester `/knowledge/search?q=architecture&top_k=5`.

### Erreur de clé LM Studio

Si LM Studio demande une clé provider, utiliser `VIVI_LMSTUDIO_API_KEY`. Ne pas réutiliser `VIVI_API_KEY` pour LM Studio.

### Smoke échoue mais pytest passe

`pytest -q` utilise des mocks et ne nécessite pas LM Studio réel. Le smoke réel exige que le backend, LM Studio Local Server et le modèle soient lancés.

## 10. Limites MVP conservées

Cette release ne contient pas : agents spécialisés, orchestrateur multi-agent, runtime skills, provider registry, fallback externe, provider OpenAI/Mammouth, priorité Ollama, vector DB, embeddings obligatoires, cockpit avancé, app mobile, VPN, multi-utilisateur, auto-amélioration ou écriture automatique dans les notes Obsidian sources.
