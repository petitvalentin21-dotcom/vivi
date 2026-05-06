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
