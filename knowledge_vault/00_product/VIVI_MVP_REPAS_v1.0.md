---
title: VIVI MVP Repas — Cadrage produit v1.0
status: validated
doc_type: product
scope: mvp
llm_index: true
llm_role: source_of_truth
llm_priority: high
updated: 2026-05-28
tags:
  - vivi
  - mvp
  - produit
  - repas
  - local-first
  - ollama
---

# VIVI MVP Repas — Cadrage produit v1.0

## Résumé

VIVI est un assistant local de repas pour usage personnel. Ce document est la source de vérité produit actuelle, après pivot vers l'usage personnel (Phase 0) et extension du repo v1 avec les modules métier Repas (FEAT-16 à FEAT-21).

Source longue : `99_archive/02-spec-repas-mvp.md` (Phase 1) et `99_archive/01-audit-vivi-v1.md` (Phase 4).

## Vision

VIVI est un assistant **local-first** centré sur les repas du quotidien.

- Utilisateur : 1 porteur + cercle proche (2 personnes, mêmes préférences alimentaires).
- Horizon : 3-5 ans sans pression de revenu projet.
- Principe directeur : réduire la charge mentale "qu'est-ce qu'on mange ?", pas remplacer l'autonomie.

## Trois besoins cœur

| Besoin | Moment | Déclencheur |
|--------|--------|-------------|
| Décision repas du soir | 18h30, semaine | Notification push proactive |
| Planning batch cooking | Samedi matin | Notification push proactive |
| Liste de courses vivante | Toute la semaine | Ajout manuel ou auto |

## Mécanique centrale

- **Catalogue interne** de recettes (SQLite) — 20-30 recettes de départ, enrichi progressivement.
- **Mix par défaut** : 1 batch "valeur sûre" + 1 batch "découverte" par semaine.
- **Préférences apprises** transparentes et révisables : ingrédients détestés, recettes favorites, portions.
- **LLM Ollama en complément** (adaptations, variantes conversationnelles) — jamais seul auteur des recettes de référence.
- **Cycles temporels** : décision quotidienne → batch weekend → liste courses → bilan.

## Stack MVP

| Composant | Technologie |
|-----------|-------------|
| LLM local | Ollama — modèle Ministral-3:14b |
| API backend | FastAPI + Python 3.12 |
| Persistance | SQLite + SQLModel + Alembic |
| Frontend | SvelteKit PWA + Tailwind CSS |
| Mobilité | Tailscale (iPhone ↔ PC) |
| RAG documentaire | Markdown lexical (vault Obsidian) |

## Modules existants (FEAT-18 à FEAT-21)

| Module | Chemin | FEAT | État |
|--------|--------|------|------|
| Recettes | `app/meals/recettes/` | FEAT-18 | ✅ livré |
| Stock | `app/meals/stock/` | FEAT-19 | ✅ livré |
| Courses | `app/meals/courses/` | FEAT-20 | ✅ livré |
| Préférences | `app/meals/preferences/` | FEAT-21 | ✅ livré |

## Modules à venir

| Module | FEAT | État |
|--------|------|------|
| Tool registry (dispatcher outils LLM) | FEAT-22 | À faire |
| Prompts système versionés | FEAT-23 | À faire |
| Scheduler proactif (18h30 / samedi) | FEAT-24 | À faire |
| Notifications Web Push | FEAT-25 | À faire |
| PWA SvelteKit minimale | FEAT-26–28 | À faire |
| Boucle conversationnelle bout-en-bout | FEAT-29 | À faire |
| Tailscale + accès iPhone | FEAT-30 | À faire |

## Hors scope MVP

| Élément | Raison |
|---------|--------|
| Scan frigo (caméra, IoT) | Complexité non justifiée |
| Intégration Carrefour/Picard/Auchan | Dépendance externe |
| Calcul nutritionnel détaillé | Post-MVP |
| Génération de recettes ex nihilo | Risque hallucinations sur quantités |
| Multi-profils alimentaires distincts | v1 = 2 personnes mêmes préférences |
| Suivi budget alimentaire | Post-MVP |
| Agents LLM multiples | 1 LLM + modules Python — pas multi-agent |
| Vector DB / embeddings | Post-MVP |
| App mobile native | PWA autorisée, natif non |

## Critères d'acceptation MVP

Au bout de 3 mois d'usage :

1. Le porteur pose moins souvent "qu'est-ce qu'on mange ?" — VIVI sollicite avant.
2. Moins de gaspillage alimentaire — batchs en cours gérés et alertes péremption.
3. Liste de courses à jour au départ pour Leclerc Drive.
4. Au moins 5 nouvelles recettes découvertes et aimées, marquées "valeur sûre".
5. L'usage est plus simple que le système actuel, pas plus compliqué.

## Référence historique

Les sources longues restent dans `99_archive/` :

- `99_archive/02-spec-repas-mvp.md` — spec fonctionnelle Repas complète (Phase 1)
- `99_archive/01-audit-vivi-v1.md` — audit du repo v1 et plan d'extension FEAT-16→FEAT-30 (Phase 4)
- `99_archive/SYNTHESE-EXECUTIVE.md` — synthèse exécutive de toutes les phases
