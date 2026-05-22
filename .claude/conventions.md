# Conventions universelles

S'applique à tous les projets sauf override explicite dans `.claude/projects/[nom].md`.

---

## Git

### Branches

- `main` / `master` — production, protégée
- `dev` — intégration (si présent)
- `feat/[nom-court]` — nouvelle fonctionnalité
- `fix/[nom-court]` — correction
- `chore/[nom-court]` — maintenance
- `refactor/[nom-court]` — refactoring sans changement de comportement
- `ai/audit-[date]` — output d'un agent d'audit
- `ai/spec-[date]` — output d'un agent de spec
- `ai/dev-[ticket-id]` — output d'un dev agent orchestré

### Commits

Format conventionnel court :

```
type(scope): description courte

Corps optionnel : pourquoi ce changement.
```

Types : `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ai`

### Pull Requests

- **Titre** : résumé de l'intention, pas du code
- **Description** : quoi, pourquoi, comment tester
- Si générée par un agent : préfixe `[AI]` dans le titre
- Une PR = une intention (pas de mélange feat + refactor + fix)

---

## Code

### Principes

- **Lisibilité > concision** — préférer explicite à clever
- **Une fonction = une responsabilité** — si le nom hésite, le scope est trop large
- **Pas d'abstraction préventive** — abstraire au 3e usage, pas au 1er
- **Erreurs explicites** — pas de silent fail, pas de `catch` vide
- **Pas de code mort** — si c'est inutilisé, supprimer (git garde l'historique)

### Choix de stack

La stack est choisie projet par projet selon :

1. Maturité de l'écosystème pour le besoin
2. Maintenabilité long terme
3. Compétences existantes équipe
4. Coût d'hébergement / exécution

Le choix et sa justification sont documentés dans `.claude/projects/[nom].md`.

### Nommage

- Variables / fonctions : `camelCase` (JS/TS), `snake_case` (Python)
- Constantes : `UPPER_SNAKE_CASE`
- Classes / Types : `PascalCase`
- Booléens : préfixe `is`, `has`, `should`, `can`
- Pas d'abréviation cryptique (`usr` → `user`, `cfg` → `config`)

---

## Tests

- Toute modification de comportement = test associé (ajout ou mise à jour)
- Tests lisibles comme une spec : `describe` clair, pas de magie
- Pas de test qui dépend d'un autre test (ordre indépendant)
- Coverage n'est pas l'objectif, c'est un indicateur — viser les chemins critiques
- Un test cassé est un signal, pas un obstacle à contourner

---

## Documentation

- `README.md` à jour à chaque feature notable (1 ligne suffit)
- Décisions d'architecture dans `DECISIONS.md` (format ADR léger : contexte / décision / conséquences)
- Commentaires dans le code = **pourquoi**, pas **quoi** — le code dit quoi
- Pas de commentaire qui répète le nom de la fonction
