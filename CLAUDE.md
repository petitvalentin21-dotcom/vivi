# CLAUDE.md — Contexte partagé pour les agents IA

> Ce fichier est le point d'entrée. Tout agent (Claude, Cursor, Copilot, autre) doit le lire en premier, puis charger les fichiers pertinents listés ci-dessous.

---

## Équipe

- **[Ton nom]** — owner technique
- **Vivi** — [rôle à compléter]
- **Agents IA** — assistants, jamais décideurs

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
Toute mise à jour passe par une PR humaine, validée par [toi] **et** Vivi.
