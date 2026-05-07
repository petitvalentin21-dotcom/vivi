# VIVI

VIVI est une IA locale d’assistance personnelle.

Objectif MVP :

- interface web dédiée simple ;
- discussion avec un modèle local via LM Studio ;
- interrogation d’un vault Obsidian ;
- affichage des sources utilisées ;
- statut runtime clair ;
- protection simple ;
- fonctionnement local-first.

## Statut

Projet recentré en phase de cadrage.
Socle backend MVP minimal initialisé (FEAT-01).

## Source de vérité

La source de vérité produit et architecture se trouve dans :

- `knowledge_vault/00_product/VIVI_MVP_CADRAGE_v0.1.md`

## Vault Obsidian

Le vault Obsidian du projet est situé dans :

- `knowledge_vault/`

## Règle principale

VIVI est d’abord un assistant local de discussion :

> Je lui parle, elle me répond.

Le MVP doit rester strict :

- interface dédiée ;
- LM Studio ;
- chat local ;
- RAG Obsidian ;
- sources visibles ;
- runtime status.

Tout le reste est post-MVP sauf décision explicite.

## Backend MVP (FEAT-01)

Configuration locale:

- Copier `.env.example` vers `.env` pour un setup local.
- Renseigner `VIVI_LMSTUDIO_MODEL` dans `.env`, puis redémarrer le backend.
- `VIVI_API_KEY` protège l'API VIVI (optionnel).
- `VIVI_LMSTUDIO_API_KEY` sert uniquement si LM Studio exige une auth.
- Ne jamais commiter `.env`.

Installation:

```bash
pip install -r requirements.txt
```

Lancer l'API:

```bash
uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Tests:

```bash
pytest -q
```

Note: LM Studio n'est pas requis pour FEAT-01. `/runtime/info` reste disponible même si LM Studio est indisponible.

## Endpoint chat MVP (FEAT-03)

Appel minimal:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour VIVI"}'
```

Notes:

- Pour un test manuel réel, LM Studio doit être lancé avec un modèle configuré via `VIVI_LMSTUDIO_MODEL`.
- Les tests automatisés (`pytest -q`) utilisent des mocks et ne nécessitent pas LM Studio réel.

## Endpoint knowledge search MVP (FEAT-04)

Recherche lexicale minimale dans le vault Obsidian:

```bash
curl "http://127.0.0.1:8000/knowledge/search?q=architecture&top_k=5"
```

Notes:

- Le RAG de FEAT-04 est lexical (pas d'embeddings, pas de vector DB).
- Le RAG n'est pas encore branché sur `POST /chat` (prévu FEAT-05).

## Chat documentaire MVP (FEAT-05)

Exemple mode document avec RAG lexical:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quels sont les objectifs du MVP ?","mode":"document","max_sources":3}'
```

Notes:

- `mode=document` (ou `use_rag=true`) active le RAG lexical Obsidian.
- Les sources utilisées sont retournées dans `sources`.
- Les tests automatisés restent mockés et ne nécessitent pas LM Studio réel.

## Smoke backend local (FEAT-06)

Prérequis:

- backend lancé (`uvicorn app.api.server:app --host 127.0.0.1 --port 8000`)
- LM Studio lancé avec un modèle chargé

Variables utiles:

```bash
export VIVI_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
export VIVI_LMSTUDIO_MODEL=google/gemma-4-e4b
```

Note base URL:

- `VIVI_LMSTUDIO_BASE_URL` accepte `http://127.0.0.1:1234` ou `http://127.0.0.1:1234/v1`.

Checks rapides:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/runtime/info
```

Smoke script (backend déjà lancé):

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --verbose
```

Si l'auth VIVI est activée:

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --api-key "<VIVI_API_KEY>"
```

Options utiles:

- `--api-key <token>`
- `--skip-chat`
- `--skip-document`
- `--message "Bonjour VIVI"`
- `--document-message "Quels sont les objectifs du MVP ?"`

Le smoke valide: `/health`, `/runtime/info`, `/knowledge/search`, `POST /chat` (mode `chat`) et `POST /chat` (mode `document`), avec résumé `ok/warn/fail` et code retour non-zéro en cas d'échec critique.

Exemple chat simple:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour VIVI","mode":"chat"}'
```

Exemple chat document:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quels sont les objectifs du MVP ?","mode":"document","max_sources":3}'
```

## Interface web locale (FEAT-07)

Lancer le backend:

```bash
uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Ouvrir l'interface:

- <http://127.0.0.1:8000/>

Rappel LM Studio:

- LM Studio doit être lancé avec un modèle configuré (`VIVI_LMSTUDIO_MODEL`).

Modes disponibles dans l'interface:

- `chat`: conversation simple.
- `document`: conversation avec RAG lexical et sources quand disponibles.
