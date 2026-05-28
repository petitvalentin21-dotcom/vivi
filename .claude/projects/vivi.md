# VIVI

> Fichier projet. Chargé après `CLAUDE.md`, `conventions.md`, `boundaries.md`, `agents.md`.
> Ne contient que ce qui est **spécifique à ce projet**.

---

## Identité

VIVI est un assistant IA local, personnel, local-first, orienté gestion des repas. Il tourne via Ollama (remplace LM Studio depuis FEAT-16) et consulte un vault Obsidian via RAG lexical. Il embarque une base SQLite (depuis FEAT-17) pour les données structurées : recettes, stock, courses, préférences.

VIVI_IA = dépôt legacy, archive, ne pas y toucher.

---

## État MVP actuel (2026-05-28)

Tout ceci est construit et fonctionnel — ne pas ré-implémenter :

### Socle v1 (hérité)

- Chat `POST /chat` avec session mémoire, RAG toujours actif
- Retrieval lexical Obsidian (`/knowledge/search`) avec `llm_priority` ranking
- Confidence label + badge "faible" dans l'UI
- Inbox Obsidian `POST /obsidian/inbox`
- Auth locale : bypass 127.0.0.1/::1, clé requise en LAN
- Web interface : chat, sources collapsibles, mémoire VIVI, help, runtime
- Markdown rendu : headings, listes, gras, code, tableaux

### Extension Repas (FEAT-16 à FEAT-19)

- Ollama comme provider LLM (remplace LM Studio)
- SQLite + Alembic (`app/db/`, migrations versionnées)
- Module Recettes : `app/meals/recettes/` — CRUD complet, 6 endpoints
- Module Stock : `app/meals/stock/` — Batch + IngredientBase, 13 endpoints

**329 tests passent** (`pytest tests/ -q`)

---

## Stack choisie

| Couche | Technologie | Pourquoi ce choix |
|---|---|---|
| Back | Python / FastAPI | Typing strict, ecosystem IA, async natif |
| LLM | LM Studio (local) | Local-first, zéro dépendance cloud, swap de modèle trivial |
| Connaissance | Vault Obsidian + RAG lexical | Markdown natif, pas de vector DB, explicable |
| Sessions | JSON file-based (`data/runtime/`) | Local-first, pas de BDD, simple à déboguer |
| Web | HTML / CSS / JS vanilla | Pas de build step, zéro dépendance front |
| Tests | pytest | Standard Python, mocks LM Studio inclus |

---

## Conventions spécifiques

> Ce qui **diffère** de `conventions.md`.

### Format de commit

Format projet : `FEAT — Description courte` (pas `type(scope): desc`).

**Raison** : le hook `commit-msg` (versionné dans `hooks/`) bloque tout commit `FEAT*` sans run log stagé dans `knowledge_vault/05_runs/`. Migrer le format casserait ce hook sans gain réel en solo.

Ne pas migrer vers le format conventionnel sans décision explicite et mise à jour du hook.

### Run logs

Claude Code crée le run log automatiquement après chaque FEAT, sans attendre qu'on le demande.
Chemin : `knowledge_vault/05_runs/YYYY-MM-DD_FEAT-NN-slug.md`

Claude Code doit :

- Créer le fichier run log avec le frontmatter standard et le contenu (résumé, fichiers créés/modifiés, validation, résultat)
- Le stager : `git add knowledge_vault/05_runs/...`
- Signaler : "Run log créé et stagé : `knowledge_vault/05_runs/...`"

Le hook commit-msg bloque tout commit `FEAT*` sans run log stagé.

### Hook commit-msg

Versionné dans `hooks/commit-msg`. À installer une fois par clone :

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg   # inutile sur Windows
```

### Frontmatter standard vault

```yaml
---
title: Titre explicite
status: active        # draft | active | validated | archived
doc_type: architecture  # product | architecture | developer-guide | decision | backlog | run | personal_profile
scope: mvp
llm_index: true
llm_priority: high    # high | medium | low
updated: YYYY-MM-DD
tags: [vivi, mvp]
---
```

---

## Domaines fonctionnels

| Terme | Définition |
|---|---|
| VIVI | L'assistant IA lui-même (le projet et le nom affiché dans l'UI) |
| vault | Le vault Obsidian local (`knowledge_vault/`) — source de vérité documentaire |
| RAG lexical | Retrieval par correspondance lexicale (tokens + sous-chaînes) sur les chunks du vault |
| `llm_priority` | Champ frontmatter (`high` / `medium` / `low`) qui booste le score RAG d'un chunk |
| run log | Note créée après chaque FEAT, stockée dans `05_runs/`, indexée par le RAG (`llm_priority: low`) |
| session | Conversation en cours — stockée en JSON dans `data/runtime/sessions.json` |
| inbox | `92_inbox/` — zone de dépôt pour validation humaine, **non indexée** par le RAG |
| chunk | Fragment d'une note vault après découpage par section et taille max |
| confidence label | `normal` ou `low` — calculé par rapport au score max des résultats RAG |

---

## Architecture conceptuelle

```
app/
  api/        # FastAPI — server.py, auth.py, schemas.py, errors.py, recettes.py, stock.py
  llm/        # OllamaClient (ex-LMStudioClient)
  knowledge/  # markdown_loader, chunker, lexical_retriever, obsidian_inbox, sources
  meals/
    recettes/ # models, repository, service, schemas
    stock/    # models, repository, service, schemas
  db/         # engine, session, base
  sessions/   # SessionStore
  runtime/    # build_runtime_info
  web/        # index.html, app.js, style.css
  config.py
tests/
knowledge_vault/
migrations/
```

### Zones vault et indexation RAG

| Dossier | Rôle | RAG indexé |
|---|---|---|
| `00_product/` | Cadrage produit | oui |
| `01_user_docs/` | Docs utilisateur | oui |
| `02_architecture/` | Architecture technique | oui |
| `03_decisions/` | Décisions | oui |
| `04_backlog/` | Backlog | oui |
| `05_runs/` | Run logs FEAT | oui (`llm_priority: low`) |
| `1X_<domaine>/` | Contenu domaine perso (ex: `10_nutrition/`) | oui |
| `90_generated/` | Contenu généré par IA | **non** |
| `91_runtime/` | Data runtime | **non** |
| `92_inbox/` | Proposals à valider | **non** |
| `99_archive/` | Archives | **non** |

**Règle vault** : l'IA n'écrit que dans `90_generated/`, `91_runtime/`, `92_inbox/`. Jamais dans les notes sources.

### Endpoints actifs

`GET /health` · `GET /runtime/info` · `POST /chat` · `GET /knowledge/search` · `POST /obsidian/inbox` · `POST /conversation/export` · `/recettes` (6 endpoints) · `/stock` (13 endpoints)

---

## Quirks et gotchas

- **VIVI_IA** = dépôt legacy archivé. Ne pas copier de code sans instruction explicite.
- **RAG toujours actif** — `use_rag: true` hardcodé dans le frontend. Pas de mode "sans RAG" dans l'UI.
- **`92_inbox/` non indexé** — les exports de conversation n'alimentent pas la mémoire RAG automatiquement. Validation humaine requise pour promouvoir une note vers une zone indexée.
- **Nouveaux dossiers domaine** → pattern `1X_<domaine>/` → ajouter le préfixe à `_INCLUDED_PREFIXES` dans `app/knowledge/markdown_loader.py`.
- **Tests sans LM Studio** — tous les appels LM Studio sont mockés. `pytest tests/ -q` ne requiert pas de serveur LM Studio actif.
- **`cfg`** est le nom de convention pour l'objet `Settings` dans `server.py` (pas `config`, pas `settings`).
- **`commit-msg` hook** — doit être installé manuellement après chaque `git clone`. Non automatique sur Windows.
- **`conversationLog` frontend** — le log de conversation JS est distinct du `SessionStore` backend. En cas de rechargement de page, le log JS est perdu mais la session backend reste.

---

## Hors-scope MVP

Ne pas implémenter sans décision explicite :

- Agents spécialisés (nutrition, finance, DEV, PM…)
- Tool calling / function calling automatique
- Vector DB, embeddings, reranker sémantique
- Multi-provider / provider registry
- Écriture automatique dans les notes sources Obsidian
- Support multi-utilisateur
- Application mobile

Le vault peut contenir du contenu domaine (nutrition, finance…) — ce n'est pas un agent, c'est du contenu RAG.

---

## Liens utiles

- Vault : `knowledge_vault/`
- Sessions (runtime) : `data/runtime/sessions.json`
- Hook commit-msg : `hooks/commit-msg`
- Skill Obsidian Markdown : `.codex/skills/obsidian-markdown/SKILL.md`

---

## Historique des décisions majeures

### 2026-05 — Commit direct sur `main` accepté

**Contexte** : projet solo, MVP en développement rapide. Pas de dev agent orchestré qui pousse sur ce repo. Pas de CI/CD critique déclenchée sur PR. Le risque de régression est couvert par les tests locaux.

**Décision** : les commits directs sur `main` sont acceptés. Le workflow branche + PR défini dans `conventions.md` est suspendu pour ce repo.

**Conséquences** : à revoir si (a) un dev agent orchestré commence à pousser des commits sur ce repo, (b) un second développeur rejoint, ou (c) une CI/CD critique est ajoutée. Dans ces cas, revenir au workflow branche + PR.
