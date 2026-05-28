# Vivi — Phase 3 : Stack backend

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique
**Casquette :** CTO + Architect + DevLead

---

## Décisions actées

| # | Décision |
|---|----------|
| BE1 | Langage backend = **Python 3.12+** |
| BE2 | Framework HTTP = **FastAPI** |
| BE3 | Architecture = **monorepo, un seul process, modules Python internes** |
| BE4 | Pas de microservices à ce stade |
| BE5 | Package manager = **uv** (ou Poetry en repli) |
| BE6 | Linting/formatting = **ruff** |
| BE7 | Type checking = **pyright** (strict mode) |
| BE8 | Tests = **pytest**, cible couverture ≥ 70% modules métier |

---

## Justification du choix Python + FastAPI

### Pourquoi Python

1. **Continuité avec Vivi v1** — déjà utilisé, l'équipe (toi) est à l'aise.
2. **Écosystème IA/LLM dominant** — Ollama Python client, LangChain, LlamaIndex, sentence-transformers, etc.
3. **Vélocité de prototypage** — itération rapide, code court, refactoring facile.
4. **Maturité 2026** — Python 3.12+ avec async, typage, performance améliorée. Plus le Python de 2015.

### Pourquoi FastAPI

1. **Async natif** — pendant qu'on attend Ollama (1-3 sec), on peut traiter d'autres requêtes (notif scheduler, etc.).
2. **Typage Pydantic intégré** — schémas explicites pour les outils LLM, validation auto des requêtes/réponses, contrats clairs.
3. **OpenAPI auto-généré** — doc API pour le client iPhone, et pour soi-même.
4. **Standard de facto en 2026** pour le backend Python orienté API. Écosystème riche, communauté active.

### Pourquoi pas Flask, Litestar, Django

- **Flask** : trop minimaliste, pas d'async natif propre, pas de typage intégré. Mature mais en perte de vitesse.
- **Litestar** : prometteur, mais écosystème plus petit et moins de ressources/exemples disponibles.
- **Django** : trop lourd pour notre cas (admin, ORM imposé, batteries-included orienté web traditionnel).

---

## Structure du projet (proposée)

```
vivi/
├── pyproject.toml         # Configuration uv/Poetry, ruff, pyright, pytest
├── README.md
├── .env.example           # Variables d'environnement (Ollama URL, paths, secrets)
├── .gitignore
│
├── backend/
│   ├── __init__.py
│   ├── main.py            # Point d'entrée FastAPI
│   ├── config.py          # Settings Pydantic
│   │
│   ├── core/              # Cœur LLM + orchestration
│   │   ├── llm_client.py  # Client Ollama
│   │   ├── tool_registry.py  # Catalogue des outils exposés
│   │   ├── conversation.py   # Logique de tour conversationnel
│   │   └── prompts.py     # Prompt système + templates
│   │
│   ├── modules/           # Modules métier (chaque module = package)
│   │   ├── recettes/
│   │   │   ├── models.py      # Schémas Pydantic
│   │   │   ├── repository.py  # Accès BDD
│   │   │   ├── service.py     # Logique métier
│   │   │   └── tools.py       # Outils exposés au LLM
│   │   ├── stock/
│   │   ├── courses/
│   │   ├── preferences/
│   │   ├── scheduler/
│   │   └── notifications/
│   │
│   ├── db/                # Accès BDD partagé (connexion, migrations)
│   │   ├── connection.py
│   │   └── migrations/
│   │
│   ├── api/               # Endpoints HTTP
│   │   ├── chat.py        # POST /chat — interactions conversation
│   │   ├── health.py      # GET /health
│   │   └── webhooks.py    # callbacks Ntfy etc.
│   │
│   └── shared/            # Utilitaires partagés
│       ├── logging.py
│       ├── errors.py
│       └── crypto.py
│
└── tests/
    ├── unit/              # Tests par module
    │   ├── recettes/
    │   ├── stock/
    │   └── ...
    ├── integration/       # Tests inter-modules
    └── scenarios/         # Tests bout-en-bout (conversations type)
```

### Règles d'organisation

1. **Un module = un package, et un seul.** Pas de "module" qui s'étale sur 3 endroits du code.
2. **Imports unidirectionnels.** `core/` peut importer de `modules/`, mais aucun module n'importe d'un autre module directement (passage par `core/` ou interface partagée si besoin).
3. **Chaque module expose sa surface dans `tools.py`.** Fonctions destinées au LLM, signatures Pydantic typées.
4. **Tests par module.** Chaque package a son dossier de tests. Pas de tests dispersés.

---

## Discipline d'architecture (pour rester sain dans un monorepo)

C'est ce qui permet à l'Option 1 de ne pas dégénérer en plat de spaghetti.

### Règles

| # | Règle | Pourquoi |
|---|-------|----------|
| R1 | Chaque module a une **interface publique** dans `tools.py` (fonctions, schémas Pydantic). Le reste est privé au package. | Empêche le couplage caché |
| R2 | **Pas d'import direct entre modules.** Si `recettes` a besoin de `stock`, ça passe par une interface dans `core/` ou par injection de dépendance | Empêche les boucles d'import et les couplages serrés |
| R3 | Chaque module a sa propre **table BDD** (ou son namespace), pas de tables partagées. | Module = unité d'évolution |
| R4 | Chaque module est **testable isolément** sans dépendre d'un autre. | Permet TDD, refactoring confiant |
| R5 | Les **schémas Pydantic** sont la frontière entre modules. Pas de dict génériques qui transitent. | Typage strict, erreurs détectées tôt |

### Conséquence pratique

Si un jour on veut extraire un module en service séparé (par exemple le Scheduler pour qu'il continue à tourner si le backend principal redémarre), c'est faisable sans refondre :
- L'interface du module reste la même (les `tools.py`).
- Il suffit de remplacer l'appel de fonction par un appel HTTP.
- Les autres modules continuent d'utiliser le module de la même façon.

C'est ce qu'on appelle le **principe de réversibilité architecturale** : tu démarres simple, tu peux distribuer plus tard sans tout casser.

---

## Outillage de dev (DevLead)

### Stack outillage

| Outil | Rôle | Pourquoi |
|-------|------|----------|
| **uv** | Package manager + venv | 10-100× plus rapide que pip/poetry, standard 2026 |
| **ruff** | Linter + formatter | Remplace flake8 + black + isort, ultra-rapide |
| **pyright** | Type checker | Plus rapide et complet que mypy, mode strict |
| **pytest** | Tests | Standard de facto Python |
| **coverage.py** | Couverture | Intégration pytest, rapports HTML |
| **pre-commit** | Hooks Git | Ruff + Pyright avant chaque commit |

### Configuration de base recommandée

`pyproject.toml` (extrait) :
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM", "RUF"]

[tool.pyright]
typeCheckingMode = "strict"
pythonVersion = "3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=backend --cov-report=html --cov-report=term-missing"
```

### Cible de couverture

- **Modules métier** (recettes, stock, courses…) : **≥ 70%** des lignes. Ces modules contiennent la logique pure.
- **Couche API** : test des endpoints en intégration. Pas de cible de couverture stricte, mais tous les endpoints doivent avoir au moins un test.
- **Code conversationnel** (prompts, orchestration LLM) : **tests par scénarios**, pas par lignes. On rédige des conversations type ("ce soir on mange quoi ?") et on valide la séquence d'outils appelés.

---

## Communication interne entre modules

Décision **BE3** validée : **appels directs de fonctions Python**, pas de bus de messages, pas de HTTP interne.

Conséquences pratiques :

- Le LLM (via le core) appelle `modules.stock.tools.marquer_portion_consommee(batch_id="...")` comme une fonction Python normale.
- Latence : zéro.
- Erreurs : remontent comme des exceptions Python classiques, faciles à logger et débugger.
- Transactions BDD : peuvent englober plusieurs modules naturellement.

---

## Points encore ouverts (Bloc C suivant)

- **Modèle de données** : SQLite vs Postgres
- **ORM** : SQLAlchemy 2.0 / SQLModel / Peewee / direct SQL
- **Migrations** : Alembic ou alternatif
- **Chiffrement at-rest** : SQLCipher si SQLite ; pgcrypto si Postgres

---

## Évolution possible (rappel)

Cette archi est **explicitement réversible** :

- ✅ **Si on veut sortir un module en service séparé** (ex. Scheduler) → faisable sans refondre, on remplace appel fonction par appel HTTP.
- ✅ **Si on veut ajouter un routeur multi-modèles** (cf. Phase 3 / 02 — trajectoire évolution) → le `core/llm_client.py` devient un router, le reste ne bouge pas.
- ✅ **Si on veut migrer la BDD** (SQLite → Postgres) → la couche `db/` et `repository.py` isolent le changement.

C'est l'avantage de l'archi modulaire bien disciplinée : tu démarres simple, tu peux évoluer sans refondre.
