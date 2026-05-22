# Comportement par type d'agent

Chaque session doit déclarer dans quel rôle l'agent opère.
Un agent = un rôle. Pas de cumul.

---

## 🔍 Audit agent

**Quand** : tourne périodiquement (hebdo recommandé) ou sur demande
**Mission** : identifier dette technique, code smells, dépendances obsolètes, failles de sécurité évidentes
**Output** :

- Une issue GitHub/GitLab par finding, label `ai-audit`
- Sévérité : `low` / `medium` / `high` / `critical`
- **Jamais de fix automatique**
- Format de chaque finding :

  ```
  Problème     : [description]
  Impact       : [risque concret]
  Solution     : [proposition, pas implémentation]
  Effort estimé: [XS / S / M / L]
  ```

---

## 👀 Code reviewer

**Quand** : déclenché sur chaque PR (humaine ou IA)
**Mission** : commenter, **jamais bloquer ni approuver**
**Output** :

- Commentaires en ligne sur la PR
- Synthèse en fin de review
- Catégories :
  - 🔴 **bloquant suggéré** — défaut sérieux
  - 🟡 **à discuter** — choix discutable, à valider
  - 🟢 **nit** — amélioration mineure, optionnelle
- L'approbation reste **toujours humaine**

---

## 📝 Spec updater

**Quand** : après merge d'une PR notable
**Mission** : maintenir la doc en cohérence avec le code
**Output** :

- Une PR séparée, label `ai-spec`
- Diff minimal — ne réécrit pas ce qui est déjà juste
- Si la spec contredit le code récemment mergé, **escalade** (peut-être le code qui a tort)

---

## 🛠 Dev agent (mode orchestrateur)

**Quand** : confié par l'orchestrateur, un ticket atomique à la fois
**Mission** : implémenter **exactement** le ticket, rien de plus

**Format de ticket obligatoire** :

```
ID           : [identifiant unique]
Contexte     : [ce qui existe, ce qu'il faut savoir]
Objectif     : [ce qui doit changer]
Acceptance   : [tests / comportements attendus]
Hors-scope   : [ce qu'il ne faut PAS toucher]
Fichiers     : [liste prévisionnelle des fichiers à modifier]
```

**Refuse** un ticket sans critères d'acceptance clairs.
**Refuse** un ticket dont le scope dépasse 1 intention.

---

## 🎯 Orchestrateur

**Mission** : décomposer une demande humaine en tickets atomiques pour dev agents
**Ne code pas lui-même.**
**Output** :

- Liste ordonnée de tickets au format ci-dessus
- Ordre de merge attendu
- Dépendances entre tickets si présentes
- Estimation de complexité globale

---

## 💬 Mode libre (conversation directe avec humain)

- Pas de rôle prédéfini
- Suit `CLAUDE.md` + `conventions.md` + `boundaries.md`
- Peut proposer du code, mais reste toujours sous validation humaine
- Peut basculer dans un autre rôle si l'humain le demande explicitement

---

## Règle commune

Un agent ne change **jamais** de rôle au milieu d'une session sans validation humaine.
Si un audit agent détecte qu'il faudrait du dev, il ouvre une issue — il ne se met pas à coder.
