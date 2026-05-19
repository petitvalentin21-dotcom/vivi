---
title: Run Log — FEAT Export enrichi
doc_type: run
llm_index: false
llm_priority: low
updated: 2026-05-19
---

# Run Log — FEAT Export enrichi (2026-05-19)

## Changements

- `app/api/schemas.py` : `ConversationExportRequest.messages` devient optionnel (default `[]`)
- `app/api/server.py` : `/conversation/export` auto-load depuis `SessionStore` si `messages` vide + `session_id` fourni ; format enrichi avec timestamps session (démarré / dernière activité)
- `app/web/index.html` : bouton "Sauvegarder" ajouté dans la barre d'actions
- `app/web/app.js` : `saveConversation()` avec feedback ; `exportConversation()` envoie `session_id` seul si log vide

## Tests

159 passed
