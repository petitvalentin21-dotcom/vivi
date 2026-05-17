# CLAUDE.md — VIVI

Instructions de travail pour Claude Code. Lire avant toute implémentation.

---

## Identité du projet

**VIVI** est un assistant IA local, personnel, local-first. Il tourne via LM Studio (Gemma ou autre) et consulte un vault Obsidian via RAG lexical.

VIVI_IA = dépôt legacy, archive, ne pas y toucher ni en copier du code sans instruction explicite.

---

## État MVP actuel (2026-05-17)

Tout ceci est **construit et fonctionnel** — ne pas ré-implémenter :

- Chat POST `/chat` avec session mémoire, RAG toujours actif (`use_rag: true`)
- Retrieval lexical Obsidian (`/knowledge/search`) avec `llm_priority` ranking
- Exposition `confidence_label` + badge "faible" dans l'UI
- Inbox Obsidian POST `/obsidian/inbox` (draft, relecture humaine)
- Auth locale : bypass automatique pour `127.0.0.1` / `::1`, clé requise en LAN
- Web interface : chat, sources collapsibles, mémoire VIVI, help, runtime
- Markdown : headings, listes, hr, gras, code inline, blocs de code, tableaux
- 153 tests passent (`pytest tests/ -q`)

---

## Architecture

```
app/
  api/        # FastAPI — server.py, auth.py, schemas.py, errors.py
  llm/        # LMStudioClient
  knowledge/  # markdown_loader, chunker, lexical_retriever, obsidian_inbox, sources
  sessions/   # SessionStore
  runtime/    # build_runtime_info
  web/        # index.html, app.js, style.css
  config.py   # Settings (frozen dataclass), load_settings()
tests/
knowledge_vault/
```

Endpoints existants : `GET /health`, `GET /runtime/info`, `POST /chat`, `GET /knowledge/search`, `POST /obsidian/inbox`, `POST /conversation/export`.

---

## Vault Obsidian — zones

| Dossier | Rôle | RAG indexé |
|---------|------|-----------|
| `00_product/` | Cadrage produit | oui |
| `01_user_docs/` | Docs utilisateur | oui |
| `02_architecture/` | Architecture | oui |
| `03_decisions/` | Décisions | oui |
| `04_backlog/` | Backlog | oui |
| `05_runs/` | Run logs | oui (`llm_priority: low`) |
| `10_nutrition/` | Profil nutrition perso | oui |
| `90_generated/` | Contenu généré | non |
| `91_runtime/` | Data runtime | non |
| `92_inbox/` | Proposals à valider | non |
| `99_archive/` | Archives | non |

Nouveaux dossiers domaine perso : `1X_<domaine>/` — ajouter à `_INCLUDED_PREFIXES` dans `markdown_loader.py`.

**Règle vault** : l'IA n'écrit que dans `90_generated/`, `91_runtime/`, `92_inbox/`. Jamais dans les notes sources.

---

## Conventions de développement

### Commits git

Format : `FEAT — Description courte` (exemples du repo : `FEAT — Alignement léger du loader RAG`, `FEAT-29 — Inbox Capture V1`).

Un commit par FEAT. Le user contrôle les commits sauf instruction explicite.

### Run logs

Après chaque FEAT significatif, créer `knowledge_vault/05_runs/YYYY-MM-DD_FEAT-slug.md` et le stager **avant** le commit. Le hook `commit-msg` bloque tout commit `FEAT*` sans run log stagé.

```yaml
---
title: Run Log — FEAT-XXX
doc_type: run
llm_index: false
llm_priority: low
updated: YYYY-MM-DD
---
```

### Git hooks

Le hook `hooks/commit-msg` est versionné dans le repo. À installer une fois :

```bash
cp hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

Ce hook bloque les commits `FEAT*` si aucun fichier `knowledge_vault/05_runs/` n'est stagé.

### Frontmatter standard vault

```yaml
---
title: Titre explicite
status: active        # draft | active | validated | archived
doc_type: architecture  # product | architecture | developer-guide | decision | backlog | run | personal_profile
scope: mvp            # mvp | post-mvp | nutrition | ...
llm_index: true
llm_priority: high    # high | medium | low
updated: YYYY-MM-DD
tags: [vivi, mvp, rag]
---
```

---

## Tests

```bash
pytest tests/ -q        # suite complète
pytest tests/ -x -q     # arrêt au premier échec
```

Ne jamais affirmer que les tests passent sans les avoir lancés. Les tests ne requièrent pas LM Studio (mocks).

---

## Ce qui est hors MVP — ne pas implémenter

- Agents spécialisés (nutrition, finance, DEV, PM...)
- Tool calling / function calling automatique
- Vector DB, embeddings, reranker
- Multi-provider, provider registry
- Écriture automatique dans les notes sources Obsidian
- Support multi-utilisateur
- App mobile

Le vault peut contenir du contenu domaine (nutrition, finance) — ce n'est pas un agent, c'est du contenu RAG.

---

## Style de travail avec Claude Code

- Agir directement sans demander confirmation pour les actions locales réversibles
- Demander confirmation avant : git push, force-push, suppression irréversible
- Ne pas committer automatiquement sauf instruction explicite
- Réponses courtes — pas de résumé narratif post-tâche sauf si utile
- Pour les tâches multi-fichiers : `TodoWrite` pour suivre l'avancement
- Lire AGENTS.md pour les règles détaillées (politique legacy, erreurs, sessions...)

---

## Référence Obsidian

`.codex/skills/obsidian-markdown/SKILL.md` — syntaxe Obsidian Flavored Markdown (wikilinks, callouts, properties, embeds). À consulter quand on crée des notes vault.
