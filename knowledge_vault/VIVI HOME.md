---
title: VIVI HOME
status: active
doc_type: index
scope: mvp
llm_index: true
llm_role: home
llm_priority: high
updated: 2026-05-28
tags:
  - vivi
  - home
  - index
---

# VIVI HOME

VIVI est un assistant local de repas. Projet strictement personnel, local-first, propulsé par Ollama. Premier domaine fonctionnel : les Repas (décision soir proactive à 18h30, batch cooking hebdo, liste de courses vivante).

## Références principales

- [[00_product/VIVI_MVP_REPAS_v1.0]] — vision produit actuelle, modules, stack, critères d'acceptation MVP
- [[03_decisions/DECISION-pivot-usage-perso]] — décision de pivot vers usage personnel (24 mai 2026)
- [[03_decisions/DECISION-base-v1-conservee]] — décision de conserver la base v1 et plan d'extension FEAT-16→FEAT-30 (25 mai 2026)

## Zones du vault

| Dossier | Contenu |
|---------|---------|
| `00_product/` | Cadrage produit |
| `01_user_docs/` | Documentation utilisateur |
| `02_architecture/` | Architecture validée |
| `03_decisions/` | Décisions projet |
| `04_backlog/` | Backlog et idées |
| `05_runs/` | Comptes rendus d'exécution (run logs) |
| `10_nutrition/` | Données nutritionnelles |
| `90_generated/` | Contenus générés par IA |
| `91_runtime/` | Données runtime, index, logs |
| `92_inbox/` | Propositions à valider |
| `99_archive/` | Archives (docs Phase 0-4, legacy-mvp-v0) |

## FEATs livrés

| FEAT | Module | Contenu |
|------|--------|---------|
| FEAT-15bis | Infra | Mise à jour CLAUDE.md / AGENTS.md / vault |
| FEAT-16 | LLM | Ollama — remplacement client LM Studio |
| FEAT-17 | DB | SQLite + SQLModel + Alembic |
| FEAT-18 | Recettes | Catalogue recettes CRUD |
| FEAT-19 | Stock | Batchs en cours + ingrédients de base |
| FEAT-20 | Courses | Liste de courses vivante |
| FEAT-21 | Préférences | Préférences utilisateur |
| FEAT-21bis | Vault | Realignment vault Obsidian sur réalité MVP Repas |

## Prochaines étapes

- FEAT-22 : Tool registry + premiers outils LLM (lecture recettes, stock, courses)
- FEAT-23 : Prompts système versionés
- FEAT-29 : Boucle conversationnelle bout-en-bout "ce soir on mange quoi ?"

## Référence historique

Les 18 documents de conception Phase 0-4 sont dans `99_archive/` (ne pas toucher — référence longue) :

- Phase 0 (cadrage stratégique) : `01-problem-statement-et-positionnement.md`, `02-persona-1-camille.md`, `03-persona-2-thomas.md`, `04-orientation-ethique-et-structure.md`, `05-modele-de-menace.md`, `06-pivot-perso.md`
- Phase 1 (vision produit) : `01-vision-produit-v1.md`, `01-topologie-physique.md`, `01-equipe-vivi.md`, `02-spec-repas-mvp.md`
- Phase 2–3 (architecture) : `02-architecture-logicielle.md`, `03-choix-llm-runtime.md`, `04-stack-backend.md`, `05-persistance-modele-donnees.md`, `06-interface-client-iphone.md`, `07-tool-calling-prompts-auth.md`
- Phase 4 (audit) : `01-audit-vivi-v1.md`
- Synthèse : `SYNTHESE-EXECUTIVE.md`

Notes archivées en `99_archive/legacy-mvp-v0/` (pré-pivot, LM Studio, chat générique) : `VIVI_MVP_CADRAGE_v0.1.md`, `VIVI — Backend MVP Spec v0.1.md`, et 6 autres notes legacy.
