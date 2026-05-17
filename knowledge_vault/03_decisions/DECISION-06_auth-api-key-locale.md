---
title: Décision — Auth locale par clé API simple, pas de gestion multi-utilisateur
status: validated
doc_type: decision
scope: mvp
llm_index: true
llm_role: decision
llm_priority: high
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - decision
  - auth
  - securite
  - api-key
---

# Décision — Auth locale par clé API simple, pas de gestion multi-utilisateur

## Contexte

VIVI expose une interface web accessible localement et optionnellement en LAN. Une protection minimale est nécessaire pour éviter un accès non autorisé, notamment en mode LAN réseau privé.

Cette décision a été posée dès FEAT-01 et précisée lors de FEAT-03 (auth sur `/chat`), FEAT-12B (séparation des clés) et FEAT-28 (auth sur `/obsidian/inbox`).

## Décision

L'authentification MVP utilise une clé API locale simple : `VIVI_API_KEY`.

Si `VIVI_API_KEY` est configurée dans `.env`, tous les endpoints protégés exigent le header `Authorization: Bearer <clé>`. Une clé absente ou incorrecte retourne une erreur safe.

Si `VIVI_API_KEY` est vide, l'auth est désactivée (comportement permissif, acceptable en usage local-only).

`VIVI_LMSTUDIO_API_KEY` est une clé distincte, utilisée uniquement pour authentifier VIVI auprès de LM Studio si celui-ci le requiert. Ces deux clés ne sont jamais confondues.

Les erreurs d'auth ne fuient aucun secret. La clé n'apparaît jamais dans les logs, les réponses API, le runtime info ou les rapports Codex.

La clé API n'est jamais stockée en `localStorage` ni `sessionStorage` côté navigateur.

## Conséquences

- Mode local-only sans `VIVI_API_KEY` : aucune protection, acceptable car l'accès est limité à `127.0.0.1`.
- Mode LAN avec `VIVI_API_KEY` : protection simple sur réseau privé de confiance.
- Aucune gestion multi-utilisateur, aucun rôle, aucun JWT, aucun OAuth.
- Le pare-feu Windows reste la première ligne de défense en mode LAN.
- Ne jamais exposer VIVI sur Internet sans couche de protection supplémentaire non couverte par ce MVP.

## Alternatives écartées

- **JWT / OAuth** : écarté, complexité non justifiée pour un usage personnel local.
- **Multi-utilisateur avec comptes** : écarté, hors périmètre MVP.
- **Pas d'auth du tout** : écarté pour le mode LAN, risque réel sur réseau partagé.
- **HTTPS obligatoire** : écarté pour le MVP local, documenté comme limite connue du mode LAN.
