---
title: Écrire pour VIVI et le RAG
status: active
doc_type: developer-guide
scope: mvp
llm_index: true
llm_role: developer_guide
llm_priority: high
updated: 2026-05-28
tags:
  - vivi
  - mvp
  - obsidian
  - rag
  - redaction
  - retrieval
---

# Écrire pour VIVI et le RAG

## But

Ce guide explique comment écrire une note Obsidian utile pour un humain et facile à retrouver par le RAG lexical de VIVI.

Le RAG MVP ne comprend pas le vault comme un humain. Il cherche des mots, des titres, des tags, des chemins et des sections. Une bonne note doit donc être claire, stable et bien découpée.

## Résumé pratique

- Donner un titre explicite.
- Ajouter un frontmatter simple.
- Écrire un résumé en haut de document.
- Utiliser des sections courtes.
- Répéter naturellement les mots importants.
- Employer le même vocabulaire pour le même concept.
- Séparer produit, architecture, backlog, run log et archive.
- Mettre `llm_index: false` sur les notes bruyantes ou non validées.

## Titres explicites

Un bon titre dit ce que la note apporte.

Bon:

- `VIVI MVP — Architecture réelle`
- `VIVI — Gouvernance Obsidian et qualité retrieval`
- `Run Log — FEAT-16 — Ollama provider`

À éviter:

- `Notes`
- `Divers`
- `Idées`
- `Compte rendu`

## Résumé en haut de document

Après le titre, ajouter une section courte qui dit:

- le sujet de la note ;
- son statut ;
- ce que VIVI doit pouvoir retrouver dedans.

Exemple:

```markdown
## Résumé

Cette note décrit l'architecture réelle du backend VIVI MVP: FastAPI, Ollama, modules Repas, RAG lexical, sources visibles, runtime info et mémoire de session simple.
```

## Sections courtes

Préférer plusieurs sections ciblées plutôt qu'un long texte continu.

Bon découpage:

- `## Objectif`
- `## Périmètre MVP`
- `## Endpoints`
- `## Sécurité`
- `## Tests`
- `## Limites volontaires`

Chaque section doit pouvoir être lue seule.

## Vocabulaire stable

Le RAG lexical retrouve mieux les documents quand les mêmes concepts gardent les mêmes mots.

Utiliser régulièrement:

- `Ollama`
- `provider local`
- `RAG lexical`
- `Obsidian`
- `sources visibles`
- `runtime info`
- `session memory`
- `API key`
- `local-first`
- `repas` / `recettes` / `stock` / `courses` / `préférences`

Éviter d'alterner sans raison entre plusieurs synonymes comme `mémoire`, `state`, `historique`, `contexte durable` pour parler d'une même chose.

## Synonymes utiles

Quand un concept peut être demandé avec plusieurs mots, ajouter une phrase naturelle qui contient les synonymes utiles.

Exemple:

```markdown
Le RAG lexical correspond à la recherche documentaire Obsidian, au retrieval de notes Markdown et à la récupération de sources visibles.
```

Ne pas bourrer une note de mots-clés. Le texte doit rester lisible.

## Décisions claires

Une décision doit être formulée directement.

Bon:

```markdown
## Décision

Le MVP utilise Ollama comme provider local (depuis FEAT-16). Aucun fallback cloud n'est ajouté.
```

À éviter:

```markdown
On verra plus tard pour les providers, peut-être qu'on gardera LM Studio.
```

## Éviter les longs journaux bruts

Les logs bruts, copier-coller de terminal, traces d'erreur longues et historiques non triés polluent le retrieval.

Préférer:

- un résumé ;
- les fichiers touchés ;
- les tests lancés ;
- le résultat ;
- les risques restants.

Mettre les longs dumps dans `91_runtime/` ou hors index.

## Éviter les documents fourre-tout

Une note doit avoir un rôle principal.

Si une note mélange produit, architecture, backlog, journal d'exécution et idées futures, elle devient difficile à retrouver et à croire.

Préférer plusieurs notes courtes:

- une note produit ;
- une note architecture ;
- une note décision ;
- une note backlog ;
- une note run.

## Utiliser les liens Obsidian

Relier les notes importantes aux hubs.

Exemples:

- [[01_user_docs/VIVI_MVP_DOC_HUB]]
- [[00_product/VIVI_MVP_REPAS_v1.0]]
- [[02_architecture/VIVI — Frontmatter documentaire MVP]]

Les liens aident l'humain à naviguer. Les titres liés aident aussi le retrieval lexical.

## Quand mettre llm_index:false

Utiliser `llm_index: false` quand la note:

- est un brouillon confus ;
- contient un dump runtime ;
- contient des informations non validées ;
- est une archive historique peu utile ;
- mélange trop de sujets ;
- contient du contenu généré non relu ;
- risque de contredire une source de vérité MVP.

Pour l'exclusion runtime actuelle, ajouter aussi:

```yaml
index: false
```

## Écrire une note de décision

Structure recommandée:

```markdown
# Décision — Titre court

## Contexte

Pourquoi la décision existe.

## Décision

La décision formulée clairement.

## Conséquences

Ce que cela implique.

## Alternatives écartées

Options non retenues et raison.
```

Frontmatter recommandé:

```yaml
---
title: Décision — Provider Ollama unique
status: validated
doc_type: decision
scope: mvp
llm_index: true
llm_role: decision
llm_priority: high
updated: 2026-05-28
tags: [vivi, mvp, decision, ollama]
---
```

## Écrire une note backlog

Une note backlog doit être actionnable.

Inclure:

- ID ou titre ;
- problème ;
- scope ;
- hors scope ;
- validation attendue ;
- priorité si connue.

Si la priorité est incertaine, écrire:

- `priority: unknown`
- ou `Assumption: priorité inconnue`.

## Écrire une note architecture

Une note architecture doit distinguer:

- architecture réelle ;
- architecture cible ;
- limites volontaires ;
- endpoints ;
- modules ;
- variables de configuration ;
- tests associés.

Ne pas annoncer comme implémenté ce qui est seulement prévu.

## Écrire une note run

Une note run doit être courte.

Inclure:

- résumé ;
- fichiers modifiés ;
- tests lancés ;
- résultat ;
- risques ;
- prochaine étape.

Éviter:

- full diff ;
- logs volumineux ;
- historique de conversation ;
- détails non réutilisables.

## Règle finale

Une bonne note RAG doit permettre à VIVI de répondre clairement à une question précise avec une source visible et vérifiable.
