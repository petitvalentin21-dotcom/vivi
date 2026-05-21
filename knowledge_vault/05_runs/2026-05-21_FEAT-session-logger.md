---
title: Run Log — FEAT session-logger
doc_type: run
llm_index: false
llm_priority: low
updated: 2026-05-21
---

## Résumé

Implémentation du module `SessionLogger` : capture chiffrée AES-256 (Fernet) des échanges user↔Vivi en fichiers JSONL par fenêtre de 15 min d'activité.

## Fichiers créés / modifiés

- `app/sessions/logger.py` — nouveau module SessionLogger
- `app/api/server.py` — intégration dans create_app() et /chat
- `app/config.py` — champs log_encryption_key, session_log_path
- `tests/test_session_logger.py` — 11 tests couvrant les 9 critères d'acceptation
- `scripts/decrypt_session.py` — utilitaire de déchiffrement manuel
- `requirements.txt` — ajout cryptography>=42.0
- `.env.example` — ajout VIVI_LOG_ENCRYPTION_KEY, VIVI_SESSION_LOG_PATH
- `.gitignore` — exclusion data/sessions/
- `tests/conftest.py` — clé de test pour l'env pytest

## Résultat des tests

170 passed in 3.51s (153 existants + 17 nouveaux, 0 régression)

## Points notables

- Transition active→pending_triage : lazy (au prochain message post-timeout), TODO worker proactif documenté dans le code
- La "session logger" (fenêtre 15 min) est distincte de la "session SessionStore" (UUID conversationnel) — documenté en tête de logger.py
- La clé de chiffrement est dérivée via PBKDF2 (100k itérations, sel fixe) — l'utilisateur peut mettre n'importe quelle chaîne dans VIVI_LOG_ENCRYPTION_KEY
