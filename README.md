# VIVI

VIVI est un assistant IA local personnel.

Objectif MVP : ouvrir une interface web dédiée, parler à un modèle local servi par LM Studio, interroger le vault Obsidian, voir les sources utilisées et garder un fonctionnement local-first.

## Statut MVP local

FEAT-01 à FEAT-15 stabilisent le socle MVP local :

- backend FastAPI ;
- `GET /health` ;
- `GET /runtime/info` ;
- `POST /chat` en mode `chat` et `document` ;
- RAG lexical Obsidian ;
- sources visibles ;
- interface web dédiée ;
- mémoire de session simple ;
- reset conversation ;
- auth locale par clé API si activée ;
- smoke backend local.

## Documentation de lancement

Procédure complète de lancement, configuration, validation et diagnostic :

- [docs/MVP_LOCAL_RELEASE.md](docs/MVP_LOCAL_RELEASE.md)

Trace Release Candidate MVP locale :

- [docs/MVP_RELEASE_CANDIDATE.md](docs/MVP_RELEASE_CANDIDATE.md)

Audit UX après manipulation MVP :

- [docs/MVP_UX_AUDIT.md](docs/MVP_UX_AUDIT.md)

## Installation rapide

```bash
pip install -r requirements.txt
copy .env.example .env
uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Ouvrir ensuite :

- http://127.0.0.1:8000/

## Configuration minimale recommandée

Dans `.env` :

```env
VIVI_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
VIVI_LMSTUDIO_MODEL=google/gemma-4-e4b
VIVI_API_KEY=
VIVI_LMSTUDIO_API_KEY=
VIVI_KNOWLEDGE_VAULT_PATH=knowledge_vault
```

Règles importantes :

- `VIVI_API_KEY` protège l'API VIVI.
- `VIVI_LMSTUDIO_API_KEY` sert uniquement si LM Studio exige une clé provider.
- Ne jamais utiliser `VIVI_API_KEY` comme clé provider LM Studio.
- `.env` est local et ignoré par Git.
- `.env.example` est versionné et ne doit contenir aucun secret.

## Tests

Tests automatisés :

```bash
pytest -q
```

Smoke backend avec LM Studio et le backend déjà lancés :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --verbose
```

Si l'auth VIVI est activée :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --api-key "<VIVI_API_KEY>"
```

## Sources de vérité

- Produit : `knowledge_vault/00_product/VIVI_MVP_CADRAGE_v0.1.md`
- Architecture backend : `knowledge_vault/02_architecture/VIVI — Backend MVP Spec v0.1.md`
- Règles agent : `AGENTS.md`

## Hors MVP

Ne pas ajouter au MVP : agents spécialisés, orchestrateur multi-agent, runtime skills, provider registry, fallback externe, embeddings obligatoires, vector DB, cockpit avancé, app mobile, VPN, multi-utilisateur, écriture automatique dans les notes Obsidian sources.
