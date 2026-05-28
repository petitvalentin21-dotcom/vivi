# Vivi — Phase 4 : Audit Vivi v1 et plan d'extension

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 4 — Audit code existant
**Source auditée :** [github.com/petitvalentin21-dotcom/vivi](https://github.com/petitvalentin21-dotcom/vivi) — branche `main`, commit `ce02600`
**Casquette :** CTO + Architect + Historien

---

## Constat d'ensemble

Vivi v1 (le repo `petitvalentin21-dotcom/vivi`) **n'est pas un projet de débutant à refactorer**. C'est déjà un fork recadré et simplifié d'un projet plus ancien (VIVI_IA), avec :

- Une **philosophie produit mûre et documentée** (AGENTS.md de 658 lignes, CLAUDE.md, AGENTS.md, docs/MVP_LOCAL_RELEASE.md).
- Une **stack minimaliste et saine** (6 dépendances dans requirements.txt).
- Une **architecture modulaire** déjà en place (`app/api/`, `app/llm/`, `app/knowledge/`, `app/sessions/`, `app/runtime/`).
- Une **politique stricte** de hors-scope MVP.
- Un **vault Obsidian** (`knowledge_vault/`) comme source de vérité documentaire.
- Des **conventions claires** (workflow Git, tests, sécurité).

**Notre Phase 3 (architecture cible) recoupe à environ 80% l'archi v1.** Le travail de conception qu'on a fait n'a pas été perdu — il a *validé* les choix existants, ce qui est précieux. Mais il faut maintenant l'expliciter.

---

## Décision : Option A — Continuité avec extension

On garde le repo v1 comme base. On l'étend pour atteindre la cible Phase 3, par évolutions ciblées :

| # | Évolution | Effort estimé |
|---|----------|---------------|
| EXT1 | Remplacer LM Studio par Ollama dans `app/llm/` | Faible (interface compatible) |
| EXT2 | Ajouter SQLite + SQLModel pour la persistance structurée | Moyen (nouveau module `app/db/`) |
| EXT3 | Ajouter les modules métier Repas (recettes, stock, courses, préférences) | Élevé (gros morceau du build) |
| EXT4 | Transformer l'IHM web localhost en PWA SvelteKit | Élevé (réécriture front complète) |
| EXT5 | Ajouter le scheduler proactif (sollicitations 18h30, 19h, weekend) | Moyen |
| EXT6 | Ajouter le service Notifications (Web Push) | Moyen |
| EXT7 | Mettre à jour AGENTS.md, CLAUDE.md, vault Obsidian pour refléter la nouvelle vision | Faible mais indispensable |
| EXT8 | Migrer Tailscale (mobilité depuis iPhone) | Faible (config externe au code) |

---

## Audit détaillé — à garder / adapter / jeter

### Catégorie 1 : À GARDER tel quel

| Élément | Pourquoi |
|---------|----------|
| **Stack `requirements.txt`** (FastAPI, Uvicorn, Pydantic, httpx, cryptography, pytest) | Exactement la stack Phase 3, rien à changer |
| **Structure `app/`** (`app/api/`, `app/llm/`, `app/knowledge/`, `app/sessions/`, `app/runtime/`) | Conforme aux principes Phase 3, juste à étendre |
| **Endpoints existants** (`GET /health`, `GET /runtime/info`, `POST /chat`) | Resteront les fondations de l'API |
| **Auth locale par clé API** (`VIVI_API_KEY` optionnelle) | Conforme à AU2 (middleware pré-équipé permissif au MVP) |
| **Politique `.env` / `.env.example`** | Hygiène propre, à conserver |
| **CLAUDE.md** (règles immuables, style de communication) | Excellent cadre méthodo, à enrichir |
| **Vault Obsidian** (`knowledge_vault/`) comme source de vérité documentaire | Le système de docs maison vaut largement nos `phase-N/*.md` une fois intégré |
| **Politique "AI-generated writes → generated/ runtime/ inbox/, jamais en source"** | Discipline saine, à conserver |
| **Politique Git** (pas d'auto-commit, branches sur demande, pas de PR auto) | Garde-fous utiles, à conserver |
| **Convention des "FEAT-NN"** pour les fonctionnalités | Bonne granularité, à conserver |
| **Doc de release MVP** (`docs/MVP_LOCAL_RELEASE.md`) | Format à conserver, à enrichir pour MVP Repas |

### Catégorie 2 : À ADAPTER

| Élément | Adaptation requise |
|---------|---------------------|
| **`app/llm/`** | Remplacer le client LM Studio par un client Ollama. L'interface reste OpenAI-compatible, donc l'impact est minimal. À renommer ou wrapper pour permettre l'évolution future vers un routeur multi-modèles. |
| **`AGENTS.md`** | Plusieurs interdits à lever :<br>• "Ollama as primary provider" → autoriser (notre décision LLM2)<br>• "mobile app" → reformuler (notre PWA n'est pas une "app mobile native", c'est une PWA)<br>• "nutrition agent" → reformuler (notre module Repas n'est pas un agent, c'est un module de code)<br>• "automatic modification of source Obsidian notes" → garder strict<br>Réécriture complète recommandée pour clarté. |
| **`CLAUDE.md`** | Enrichir le tableau de l'équipe (cf. Phase 2 — "L'équipe Vivi" avec 13 rôles). Mentionner explicitement le pivot personnel (cf. Phase 0 doc 06). |
| **README.md** | Mettre à jour pour refléter la vision MVP Repas. Pas de mention de Repas pour l'instant — à ajouter au moment du build. |
| **RAG Obsidian (`app/knowledge/`)** | Reste utile pour les recettes (catalogue Markdown dans le vault). Mais on ajoute une persistance SQLite *à côté* pour les données structurées (stock, batchs, listes de courses). |
| **Mémoire de session** (`app/sessions/`) | Garder pour les conversations courtes. Compléter par une mémoire long-terme via SQLite (préférences apprises, historique consolidé). |
| **IHM web localhost** | Transformer en PWA SvelteKit. C'est essentiellement une nouvelle couche front, le backend reste compatible. |

### Catégorie 3 : À AJOUTER (n'existe pas en v1)

| Élément | Justification |
|---------|--------------|
| **`app/db/`** | Couche d'accès SQLite/SQLModel partagée. Migrations via Alembic. |
| **`app/modules/recettes/`** | Module métier Catalogue de recettes (cf. Phase 1 doc 02). |
| **`app/modules/stock/`** | Module métier Stock (batchs en cours, ingrédients de base). |
| **`app/modules/courses/`** | Module métier Liste de courses. |
| **`app/modules/preferences/`** | Module métier Préférences apprises. |
| **`app/modules/scheduler/`** | Sollicitations proactives (18h30 dîner, samedi planif). Nouveau besoin Phase 1. |
| **`app/modules/notifications/`** | Web Push depuis FastAPI vers iPhone. Nouveau besoin Phase 1. |
| **`app/core/tool_registry.py`** | Dispatcher pour le tool calling (cf. Phase 3 doc 07). Pas explicite en v1. |
| **`app/core/prompts/`** | Prompts versionés Markdown (cf. PR1 — Phase 3 doc 07). À structurer. |
| **`frontend/`** | Nouveau dossier pour la PWA SvelteKit. |
| **Tailscale** | Côté infra (pas dans le repo) — à configurer sur PC + iPhone. |

### Catégorie 4 : À JETER OU IGNORER

| Élément | Raison |
|---------|--------|
| **`.codex/skills`** | Vide ou résidu d'une orientation "skills runtime" abandonnée. À supprimer si non utilisé. |
| **`.agents/skills/vivi-mvp-ui`** | Idem — à vérifier et nettoyer si vide. |
| **Politique "VIVI_IA legacy"** dans AGENTS.md | Tout le § 19 sur l'audit VIVI_IA peut être archivé : on est passé à autre chose, VIVI_IA n'est plus une référence active. |
| **Interdits obsolètes** dans AGENTS.md (cf. catégorie 2) | À reformuler ou supprimer. |

---

## Points d'attention spécifiques

### 1. Le vault Obsidian comme système de docs

Vivi v1 utilise `knowledge_vault/` avec une structure numérotée (`00_product/`, `02_architecture/`, `03_decisions/`, etc.). C'est plus mature que nos `phase-N/*.md` produits dans cette conversation.

**Recommandation :** intégrer nos 15 documents de conception dans le vault aux bons emplacements :
- Phase 0 → `00_product/` et `03_decisions/`
- Phase 1 → `00_product/`
- Phase 2 → `01_user_docs/` ou nouvelle section `02_methodology/`
- Phase 3 → `02_architecture/`
- Phase 4 → `03_decisions/`

Ça unifie la documentation et profite du vault Obsidian déjà en place.

### 2. La règle "AI-generated writes → generated/ runtime/ inbox/"

Cette règle est précieuse pour éviter qu'un agent IA (Codex, Claude Code) ne modifie par inadvertance les notes source. À conserver strictement.

**Implication concrète pour le build :** quand on ajoutera des outils LLM qui écrivent dans le vault (par exemple, journaliser un repas dans une note du jour), ces écritures iront systématiquement dans `92_inbox/` ou `91_runtime/`, pas dans les notes source. C'est cohérent avec l'archi tool calling read/write de Phase 3.

### 3. La discipline FEAT

Vivi v1 utilise un découpage en "FEAT-NN" (FEAT-01 à FEAT-15 cités dans README). C'est exactement la granularité dont on aura besoin pour le build progressif. **À conserver.**

Premier set de FEATs pour le MVP Repas :
- FEAT-16 : Setup Ollama + remplacement client LM Studio
- FEAT-17 : Setup SQLite + Alembic
- FEAT-18 : Module Recettes (catalogue, ajout, recherche)
- FEAT-19 : Module Stock (batchs, ingrédients)
- FEAT-20 : Module Courses (liste vivante)
- FEAT-21 : Module Préférences
- FEAT-22 : Tool registry + premiers outils LLM
- FEAT-23 : Prompts système versionés
- FEAT-24 : Module Scheduler
- FEAT-25 : Module Notifications + Web Push
- FEAT-26 : PWA SvelteKit minimale (conversation)
- FEAT-27 : PWA — écran Courses
- FEAT-28 : PWA — onboarding
- FEAT-29 : Bout-en-bout : "ce soir on mange quoi"
- FEAT-30 : Tailscale et accès iPhone

### 4. Le double système docs / agents

Tu as deux documents qui guident les agents IA : `CLAUDE.md` (pour Claude Code) et `AGENTS.md` (pour Codex). C'est bien, mais ça oblige à maintenir deux choses.

**Recommandation après mise à jour :** garder la duplication parce que les deux outils existent dans ton workflow, mais factoriser la majorité du contenu dans `CLAUDE.md` et faire de `AGENTS.md` un pointeur léger vers `CLAUDE.md` + spécificités Codex. Ça réduit la dette.

---

## Plan d'attaque suggéré pour Phase 5 (build)

Ordre logique des FEATs, à valider par toi :

**Lot 1 — Mise à niveau infra (1-2 semaines en loisir)**
1. FEAT-15bis : Mettre à jour AGENTS.md, CLAUDE.md, vault Obsidian avec les décisions Phase 0-3
2. FEAT-16 : Setup Ollama + remplacement client LM Studio
3. FEAT-17 : Setup SQLite + Alembic + structure `app/db/`

**Lot 2 — Modules métier de base (2-3 semaines)**
4. FEAT-18 : Module Recettes
5. FEAT-19 : Module Stock
6. FEAT-22 : Tool registry + premiers outils LLM (lecture seule)
7. FEAT-23 : Prompts système versionés

**Lot 3 — Boucle conversationnelle MVP (1-2 semaines)**
8. FEAT-29 : Bout-en-bout en CLI / web localhost : "ce soir on mange quoi"
9. Test : valider que la conversation fonctionne sur PC avant de complexifier

**Lot 4 — Modules complémentaires (1-2 semaines)**
10. FEAT-20 : Module Courses
11. FEAT-21 : Module Préférences
12. Étendre tool registry avec outils d'écriture

**Lot 5 — Proactivité (1-2 semaines)**
13. FEAT-24 : Module Scheduler
14. FEAT-25 : Module Notifications + Web Push

**Lot 6 — PWA et mobilité (3-4 semaines)**
15. FEAT-26 : PWA SvelteKit minimale
16. FEAT-27 : Écran Courses
17. FEAT-28 : Onboarding
18. FEAT-30 : Tailscale et accès iPhone

**Lot 7 — Validation MVP (1-2 semaines)**
19. Tests scénarios de bout en bout
20. Critères d'acceptation MVP (cf. Phase 1 doc 02)
21. Décision : continuer / itérer / pivot vers Topo D

**Horizon total estimé : 12 à 16 semaines de soir/weekend** pour atteindre la fin du Lot 7 et avoir un Vivi MVP Repas utilisable au quotidien.

---

## Conclusion de Phase 4

Vivi v1 est une base saine et qualifiée. Notre Phase 3 valide implicitement la majorité de ses choix. Le travail restant n'est pas une refonte, c'est une **extension cadrée** :

- Stack à conserver
- Architecture à étendre selon plan FEAT-16 à FEAT-30
- Documentation à harmoniser entre vault Obsidian existant et nos 15 docs Phase 0-4
- Mise à jour incontournable de AGENTS.md / CLAUDE.md pour éviter que les agents IA refusent les changements actés en Phase 3

**Phase 4 close. Phase 5 (build) peut démarrer.**
