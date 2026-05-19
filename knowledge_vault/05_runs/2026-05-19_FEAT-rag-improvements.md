---
title: Run Log — FEAT RAG improvements
doc_type: run
llm_index: false
llm_priority: low
updated: 2026-05-19
---

# Run Log — FEAT RAG improvements (2026-05-19)

## Changements

- `app/knowledge/lexical_retriever.py` : `_PRIORITY_BOOST` (+1.0 high / 0.0 medium / -0.5 low) appliqué directement au score — plus seulement tie-breaker
- `app/knowledge/chunker.py` : splitting word-boundary-aware (`rfind(' ')` avant la limite pour éviter les coupures en milieu de mot)

## Tests

159 passed
