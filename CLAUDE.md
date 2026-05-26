# CLAUDE.md — Contexte partagé pour les agents IA

> Ce fichier est le point d'entrée. Tout agent (Claude, Cursor, Copilot, autre) doit le lire en premier, puis charger les fichiers pertinents listés ci-dessous.

---

## Pivot personnel

Vivi est un projet **strictement personnel**. Pas de commercialisation, pas de structure juridique, pas de marketing. Le porteur opère en parallèle d'un job. Horizon : 3-5 ans sans revenu projet.

**Garde-fou permanent** : éviter le sur-engagement et la sur-ingénierie.

---

## Équipe Vivi

Ces casquettes sont un **menu, pas un protocole** — elles sont invoquées quand elles servent.

| Casquette | Responsabilité |
| --------- | -------------- |
| CEO | Vision, arbitrage, validation finale (= porteur) |
| CPO | Scope produit, priorités, UX |
| COO | Qualité livrée, workflow |
| CTO | Choix stack, cohérence architecturale |
| Architect | Design système, interfaces, évolutivité |
| DevLead | Implémentation, revue de code |
| QA | Tests, couverture, non-régression |
| CISO | Sécurité, analyse menaces |
| DPO | Vie privée, minimisation, zero-knowledge |
| ResearchLead | Veille, benchmarks, comparatifs |
| Linguiste | NLP, qualité des prompts, réponses LLM |
| Historien | Traçabilité des décisions, mémoire projet |
| Sponsor | Garde-fou contre sur-engagement et sur-ingénierie |

**Agents IA** — assistants, jamais décideurs.

---

## Comment lire ce repo

1. Lire ce fichier en entier
2. Charger `.claude/conventions.md` pour les règles de code et git
3. Charger `.claude/boundaries.md` pour les frontières d'action
4. Charger `.claude/agents.md` si l'agent opère dans un rôle spécifique
5. Si le repo correspond à un projet listé dans `.claude/projects/`, charger ce fichier

---

## Règles immuables

Jamais d'exception sans validation humaine explicite.

1. **Pas de commit direct sur `main` / `master`** — toujours branche + PR
2. **Pas de modification de secrets, `.env`, configs de prod** — flag et stop
3. **Pas de migration BDD sans validation explicite** — proposer, ne pas exécuter
4. **Tests à jour ou pas de merge** — si le comportement change, les tests aussi
5. **En cas de doute, demander** — l'escalade vaut mieux que la dérive

---

## Démarrage d'une session agent

À chaque nouvelle conversation, l'agent doit :

1. Confirmer qu'il a lu ce fichier (mention explicite)
2. Identifier dans quel rôle il opère : `audit` / `review` / `spec` / `dev` / `orchestrateur` / `libre`
3. Lister les fichiers qu'il prévoit de modifier avant de commencer
4. Attendre confirmation si le scope dépasse 3 fichiers ou touche un chemin protégé

---

## Style de communication attendu

- Réponses concises, pas de remplissage
- Si une décision implique un trade-off, l'expliciter
- Pas de "je peux faire X" sans le faire ensuite
- Français par défaut pour les échanges ; code et identifiants en anglais
- Pas de flatterie, pas de "excellente question"

---

## Évolution de ce fichier

`CLAUDE.md` et `.claude/*` ne sont jamais modifiés par un agent.
Toute mise à jour passe par une PR humaine, validée par le porteur.
