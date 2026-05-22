---
title: Run Log — FEAT SSE Streaming
doc_type: run
llm_index: false
llm_priority: low
updated: 2026-05-19
---

# Run Log — FEAT SSE Streaming (2026-05-19)

## Changements

- `app/llm/lmstudio.py` : `prepare_stream_payload()` + `iter_stream()` avec `httpx.stream()` et parsing SSE ligne par ligne (`data: {...}` / `[DONE]`)
- `app/api/server.py` : endpoint `POST /chat/stream` → `StreamingResponse` SSE (events `meta`, `delta`, `error`, `done`) ; RAG toujours actif
- `app/web/app.js` : `sendChat()` migré vers `/chat/stream` avec `ReadableStream` ; `createStreamingMessage()` + `updateStreamingContent()` pour rendu progressif

Note : server.py et app.js embarquent aussi les changements FEAT export enrichi (commits séparés impossibles sur fichiers partagés).

## Tests

159 passed
