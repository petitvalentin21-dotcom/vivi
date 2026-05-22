---
title: VIVI — Roadmap
status: draft
doc_type: roadmap
scope: pilotage
llm_index: true
llm_role: source_of_truth
llm_priority: high
updated: 2026-05-22
tags:
  - vivi
  - roadmap
  - pilotage
---

# VIVI — Roadmap

## Statut du document

Source de vérité unique pour le pilotage du projet VIVI.

Toute évolution prioritaire passe par ce fichier. Les conversations Claude (.ai, Code, Cowork) sont des moyens d'exécution, jamais des sources de vérité.

Convention de mise à jour : on ré-édite ce fichier, on n'en crée pas un nouveau.

## Légende

**Statuts** : `not_started` · `in_progress` · `blocked` · `done` · `parked`

**Canal d'exécution** :
- `Code` = Claude Code dans VSC (implémentation)
- `Chat` = Claude.ai / Cowork (réflexion, cadrage, specs)
- `Solo` = action hors-Claude (usage, tests manuels, décisions)

---

# P0 — En cours

Une seule chose à la fois. Tant que P0 n'est pas terminé, on ne démarre rien d'autre.

## P0.1 — Logger de sessions v1

- Statut : `in_progress`
- Canal : `Code`
- Spec : `vivi-logger-spec.md` (déjà transmise à Claude Code)
- Critères de sortie : PR mergée, tests verts, sessions JSONL chiffrées produites en usage réel.
- Bloque : tout l'axe apprentissage (P2).

---

# P1 — Fondations utilisables

Objectif de la phase : pouvoir utiliser VIVI au quotidien et accumuler de la donnée d'usage réelle.

## P1.1 — Usage réel quelques jours

- Statut : `not_started`
- Canal : `Solo`
- Pré-requis : P0.1 terminé.
- Critères de sortie : au moins une semaine de sessions logguées, notes prises sur les frictions observées.
- Objectif : laisser parler les vraies données avant de figer l'agent d'apprentissage.

## P1.2 — Accès mobile minimal

- Statut : `not_started`
- Canal : `Chat` pour le choix, `Code` pour l'exécution.
- Options à trancher : PWA (interface web améliorée) vs bot Telegram (push gratuit, multi-device).
- Décision attendue : choisir UNE des deux pour démarrer, pas les deux.
- Critères de sortie : VIVI accessible depuis l'iPhone sans ouvrir Safari à chaque fois.

## P1.3 — Roadmap vivante

- Statut : `in_progress` (ce fichier)
- Canal : `Chat`
- Critères de sortie : ce fichier mis à jour à chaque transition de phase.

---

# P2 — Apprentissage asynchrone

Objectif de la phase : VIVI commence à apprendre de son usage.

## P2.1 — Triage des sessions

- Statut : `not_started`
- Canal : `Chat` pour la spec, `Code` pour l'implémentation.
- Pré-requis : P1.1 (données réelles disponibles).
- Logique : `pending_triage` → `worth_processing` / `skip`.
- Décisions ouvertes : critères de triage, automatique ou supervisé.

## P2.2 — Agent d'apprentissage

- Statut : `not_started`
- Canal : `Chat` pour la spec, `Code` pour l'implémentation.
- Rôle : extraire faits, préférences, patterns, corrections depuis les sessions triées.
- Décisions ouvertes : quand il tourne (post-session / batch / on-demand), gestion des conflits.

## P2.3 — Notes atomiques dans Obsidian

- Statut : `not_started`
- Canal : `Chat` pour la structure, `Code` pour l'écriture automatisée.
- Cible : `90_generated/` puis validation manuelle vers zones sources.
- Convention : une note = un fait / un pattern, tagués par domaine.

## P2.4 — Intégration apprentissage → RAG

- Statut : `not_started`
- Canal : `Code`
- Critères de sortie : VIVI utilise effectivement les notes apprises dans ses réponses.

---

# P3 — Extension produit

Objectif de la phase : VIVI devient plus capable et accessible.

## P3.1 — RAG enrichi

- Statut : `not_started`
- Canal : `Chat` puis `Code`
- Contenu : sources cliquables, scores, extraits, type de note, niveau de confiance.

## P3.2 — RAG vectoriel

- Statut : `not_started`
- Canal : `Code`
- Mode : shadow d'abord, basculé si meilleur que lexical.

## P3.3 — Voix entrante (Whisper)

- Statut : `not_started`
- Canal : `Code`
- Pré-requis : P1.2 décidé (Telegram facilite ce point).

## P3.4 — Voix sortante (TTS)

- Statut : `not_started`
- Canal : `Code`

## P3.5 — Sécurité hors LAN

- Statut : `not_started`
- Canal : `Chat` pour la spec, `Code` pour l'exécution.
- Contenu : TLS, reverse proxy, auth dédiée, audit des appels.
- Pré-requis : usage stable en LAN.

---

# P4 — Multi-LLM & orchestration

Objectif de la phase : VIVI route intelligemment entre plusieurs modèles.

## P4.1 — Provider abstraction étendue

- Statut : `not_started`
- Canal : `Code`
- Contenu : Ollama, OpenAI, Mammouth pluggables.

## P4.2 — Routing par domaine

- Statut : `not_started`
- Canal : `Chat` puis `Code`
- Pré-requis : notes atomiques tagées par domaine (P2.3).

## P4.3 — Switch LLM temps réel

- Statut : `not_started`
- Canal : `Code`

---

# P5 — Agents spécialisés

Objectif de la phase : VIVI devient un orchestrateur d'agents.

## P5.1 — Agent DEV

- Statut : `not_started`
- Canal : `Chat` puis `Code`

## P5.2 — Agent PM / ARCH / QA

- Statut : `not_started`
- Canal : `Chat` puis `Code`

## P5.3 — Agents domaines de vie

- Statut : `not_started`
- Canal : `Chat` puis `Code`
- Contenu : Nutrition, Finance, Maison, Organisation perso.

## P5.4 — Auto-amélioration / Créateur de skills

- Statut : `not_started`
- Canal : `Chat` puis `Code`
- Note : zone à risque, nécessite supervision stricte.

---

# Idées parkées

À ne pas oublier mais hors roadmap active tant qu'on n'a pas tranché.

- Wrapper natif Capacitor / Tauri (vs PWA)
- App native SwiftUI
- Raccourcis Siri / Shortcuts iOS
- Widget iOS écran d'accueil
- Benchmarking automatique des modèles
- Mémoire vectorielle long terme autonome
- Mémoire comportementale auto-modifiée

---

# Règles de fonctionnement

1. **Une seule P en cours.** P0 finit avant P1.
2. **Ce fichier est source de vérité.** Toute idée nouvelle passe par `92_inbox/`, puis migre ici si retenue.
3. **Chaque transition de phase** est l'occasion de relire ce fichier en entier et de réajuster.
4. **Spec avant code.** Toute tâche en canal `Code` doit avoir une spec écrite (canal `Chat`) avant ouverture de branche.
5. **PR avant merge.** Aucune auto-validation par Claude Code.
