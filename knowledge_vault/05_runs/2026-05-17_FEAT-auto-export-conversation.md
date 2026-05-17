---
title: Run Log — FEAT Auto-export conversation
status: done
doc_type: run
scope: mvp
llm_index: false
llm_role: run_log
llm_priority: low
updated: 2026-05-17
tags:
  - vivi
  - mvp
  - run
  - export
  - conversation
  - inbox
---

# Run Log — FEAT Auto-export conversation — 2026-05-17

## Résumé

L'historique de chaque conversation est exporté automatiquement dans `92_inbox/` à la réinitialisation ou à la fermeture de la page. Aucune action humaine supplémentaire.

## Fichiers modifiés

- app/api/schemas.py
- app/api/server.py
- app/web/app.js
- tests/test_web_interface.py
- tests/test_conversation_export.py (nouveau)

## Changements clés

- `POST /conversation/export` : accepte `{session_id, messages}`, écrit dans `92_inbox/` via `create_inbox_note(note_type="conversation_summary")`.
- `ConversationMessage`, `ConversationExportRequest`, `ConversationExportResponse` ajoutés aux schemas.
- `_format_conversation_body` : formate les échanges en markdown (`**[vous]**` / `**[VIVI]**`).
- Client JS : `conversationLog[]` alimenté à chaque échange réussi.
- `exportConversation()` : fire-and-forget fetch, vide le log immédiatement pour éviter le double-export.
- `resetConversation()` : appelle `exportConversation()` avant de vider le DOM.
- `beforeunload` : `navigator.sendBeacon()` pour capturer la fermeture de page.

## Validation

- `pytest tests/test_conversation_export.py -q` → 6 passed
- `pytest tests/ -q` → 159 passed

## Résultat

Chaque conversation VIVI est sauvegardée dans `92_inbox/` sans action humaine. Relecture possible dans Obsidian avant validation.
