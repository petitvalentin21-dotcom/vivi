# Validation RAG MVP+

Ce jeu de validation sert a mesurer le RAG lexical avant toute amelioration du moteur. Il ne change pas l'algorithme, le scoring, le backend chat, l'API, l'IHM, le provider LM Studio, les prompts, ni la selection des sources.

## Fichiers

- `tests/fixtures/rag_validation_cases.json` : mini-vault de test et questions de reference.
- `tests/test_rag_validation.py` : tests automatises reproductibles.

## Cas couverts

| Cas | Question | Attendu principal |
| --- | --- | --- |
| Cadrage produit | Objectif MVP de VIVI | Source produit, extrait avec objectif MVP, interface web, LM Studio et vault Obsidian |
| Backend/API | Endpoints API backend FastAPI | Source architecture, extrait avec endpoint, API, runtime et contrat |
| RAG/Obsidian | Role du vault Obsidian dans le mode document | Source RAG/architecture, extrait avec contexte documentaire, sources visibles et extrait |
| Hors contexte | Question volontairement sans recouvrement lexical | Aucune source retournee, aucune source inventee |
| Ambigue | Question courte `MVP` | Resultat borne, deterministe et sans explosion du nombre de sources |

## Utilisation

Lancer la validation ciblee :

```bash
pytest -q tests/test_rag_validation.py
```

Lancer toutes les validations RAG :

```bash
pytest -q tests/test_rag*.py
```

Lancer toute la suite :

```bash
pytest -q
```

## Regles de lecture

- Une regression indique que le RAG lexical ne retrouve plus les documents de reference ou retourne des extraits moins utiles.
- Le cas hors contexte doit rester vide : aucune source forte ne doit etre inventee.
- Les tests n'appellent pas LM Studio et utilisent une mini-vault temporaire.
- La fixture est volontairement petite pour servir de baseline stable avant optimisation future.
