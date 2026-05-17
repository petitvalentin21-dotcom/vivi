---
title: Décision — RAG lexical uniquement, sans vector DB ni embeddings
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
  - rag
  - lexical
  - obsidian
  - retrieval
---

# Décision — RAG lexical uniquement, sans vector DB ni embeddings

## Contexte

VIVI a besoin d'un mécanisme de retrieval documentaire sur le vault Obsidian pour fournir des sources visibles à l'utilisateur.

Deux approches étaient possibles : retrieval lexical (recherche par mots-clés, TF-IDF-like) ou retrieval sémantique (embeddings + vector DB). Cette décision a été posée dès FEAT-04 (référencé dans le rapport FEAT-03 du 06/05/2026).

## Décision

Le RAG MVP utilise uniquement la recherche lexicale.

Aucun embedding n'est calculé. Aucune vector DB n'est ajoutée. Le scoring est basé sur la correspondance de termes entre la requête et le contenu des notes Markdown.

Un marquage de confiance léger est ajouté sur les sources : `confidence_label: normal` ou `low`. Une source est `low` si son score est inférieur à 3.0 ou inférieur à 35 % du meilleur score de la requête. Ce marquage n'exclut pas les sources, il les qualifie.

Les sources retournées contiennent : `path`, `title`, `score`, `excerpt`, `confidence_label`.

## Conséquences

- Le retriever (`app/knowledge/lexical_retriever.py`) est lisible, explicable et sans dépendance lourde.
- La qualité du retrieval dépend directement de la qualité rédactionnelle des notes Obsidian (titres, mots-clés, frontmatter).
- Aucune phase d'indexation vectorielle n'est nécessaire au démarrage.
- Les sources remontées peuvent parfois être faibles (score bas) sur des requêtes vagues ou éloignées du vocabulaire du vault.
- Le guide `Écrire pour VIVI et le RAG` et le standard frontmatter compensent cette limite par la discipline rédactionnelle.

## Alternatives écartées

- **Vector DB (ChromaDB, Qdrant, etc.)** : écarté, dépendance lourde, overhead de maintenance, non justifié pour un vault petit et lisible.
- **Embeddings locaux via sentence-transformers** : écarté, consommation GPU/mémoire non souhaitée sur le MVP, complexité du pipeline.
- **OpenAI embeddings API** : écarté, appel externe contraire au principe local-first.
- **Hybrid search (lexical + sémantique)** : post-MVP uniquement, si la qualité lexicale s'avère insuffisante après stabilisation.
