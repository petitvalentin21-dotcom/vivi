---
title: Décision — Périmètre MVP local-first et non-objectifs
status: archived
doc_type: decision
scope: mvp
llm_index: false
llm_role: decision
llm_priority: high
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - decision
  - local-first
  - perimetre
  - non-objectifs
---

# Décision — Périmètre MVP local-first et non-objectifs

## Contexte

Le projet VIVI est issu d'un recentrage volontaire depuis un ancien projet (VIVI_IA) plus ambitieux qui visait multi-agent, orchestration avancée, SSE, rate limiting, Docker, Open WebUI et mémoire JSON avancée.

Cette décision cadre ce qui est et ce qui n'est pas dans le périmètre du MVP actuel. Elle est structurante pour éviter la dérive architecturale à chaque nouvelle FEAT.

## Décision

VIVI MVP est local-first. Son périmètre est délibérément restreint.

Ce que le MVP fait :

- Interface web simple dédiée à VIVI (vanilla HTML/CSS/JS, pas de framework).
- Chat local avec LM Studio.
- Mode document/RAG basé sur Obsidian (retrieval lexical).
- Sources visibles dans l'interface.
- Runtime info clair.
- Auth par clé API locale (`VIVI_API_KEY`).
- Capture explicite vers `92_inbox/` (Mémoire VIVI).
- Smoke tests fiables.
- Accès LAN optionnel sur réseau privé documenté.

Ce que le MVP ne fait pas (non-objectifs) :

- Pas de multi-agent ni d'orchestration complexe.
- Pas de fallback cloud si LM Studio indisponible.
- Pas de provider externe (OpenAI, Anthropic, Ollama) par défaut.
- Pas de vector DB ni d'embeddings obligatoires.
- Pas d'Open WebUI comme interface principale.
- Pas de Docker obligatoire.
- Pas de gestion multi-utilisateur.
- Pas d'authentification avancée (JWT, OAuth).
- Pas de SSE (streaming).
- Pas d'indexation ou de validation automatique des notes Obsidian.
- Pas de promotion automatique des notes inbox.
- Pas de registry de providers.
- Pas d'appel externe non explicitement demandé.

## Conséquences

- Chaque FEAT doit être évaluée contre cette liste avant implémentation.
- Si une FEAT introduit l'un des non-objectifs, elle doit être explicitement validée comme exception.
- L'ancien projet VIVI_IA peut servir d'inspiration technique mais ne doit pas guider les priorités MVP.
- La conformité MVP est vérifiée à chaque rapport Codex.

## Alternatives écartées

- **Réimporter l'architecture VIVI_IA** : écarté, complexité non justifiée, dérive contraire au principe de MVP testable et maintenable.
- **Open WebUI comme interface principale** : écarté, dépendance externe lourde, moins contrôlable.
- **Streaming SSE dès le MVP** : écarté, complexité réseau et UI non nécessaire pour valider le cas d'usage core.
