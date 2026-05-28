---
title: Run Log — Mise à jour AGENTS.md état MVP FEAT-19 + run log auto
doc_type: run
llm_index: true
llm_priority: low
updated: 2026-05-28
---

## Résumé

Mise à jour de `AGENTS.md` pour synchroniser le fichier avec l'état réel du projet après FEAT-19 (module Stock) et formaliser l'automatisation des run logs pour Codex.

## Fichiers modifiés

- `AGENTS.md` — 5 sections mises à jour :
  - **§2 Product vision** : ajout "(local chat via Ollama)" dans l'architecture principle
  - **§6 Outside MVP scope** : suppression de `provider registry`, ajout note Ollama actif depuis FEAT-16
  - **§7 Ollama provider** : section entièrement réécrite (titre → "Ollama provider rule", retrait streaming + fallback model, URL corrigée)
  - **§8 Backend architecture** : bloc modules mis à jour (recettes, stock, db, migrations), endpoints actifs remplacent les endpoints MVP planifiés, test count ajouté (329)
  - **§13 Run history policy** : ajout des étapes d'automatisation Codex (créer, stager, signaler)

## Validation

Aucun test impacté — modifications documentation uniquement.

## Résultat

`AGENTS.md` reflète fidèlement l'état du repo au 2026-05-28 : Ollama comme provider unique, modules recettes + stock opérationnels, 329 tests passants, run log automatisé.
