# Vivi — Phase 0 : Pivot perso

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 0 — Cadrage stratégique (clôture)

---

## Contexte du pivot

À l'issue de la production des 5 premiers documents de Phase 0 (Problem Statement, Personas Camille et Thomas, Orientation éthique, Modèle de menace), le porteur du projet a décidé d'abandonner l'objectif de commercialisation.

Raison invoquée : le poids cumulé des contraintes (RGPD, AI Act, zero-knowledge commercial, modèle éco viable, gouvernance open-source, pérennité face aux géants) rendait le projet décourageant et disproportionné par rapport à l'énergie disponible et à l'envie initiale.

Le projet devient donc strictement personnel.

---

## Nouveau cap

**Vivi est un projet personnel.**

- **Utilisateur principal :** le porteur du projet, pour son usage quotidien.
- **Utilisateurs secondaires éventuels :** cercle proche restreint (famille, amis), à préciser plus tard, sans engagement de support.
- **Pas de commercialisation.** Pas de pricing, pas de marketing, pas de structure juridique.
- **Code :** privé par défaut. Possibilité d'ouvrir publiquement plus tard, sans obligation.
- **Engagement support :** strictement zéro vis-à-vis d'éventuels utilisateurs tiers.

---

## Ce qu'on jette

- Tout le volet commercialisation : modèles économiques, structure juridique, financement, pricing.
- Stratégie d'acquisition, marketing, presse, RP.
- Roadmap go-to-market, jalons commerciaux.
- Pression "vs ChatGPT" — Vivi n'est plus en compétition avec qui que ce soit.
- Étude concurrentielle comme analyse de marché (reste utile en veille technique).

## Ce qu'on garde

### Principes de sécurité fondateurs (issus du Modèle de menace)

Même pour un usage perso + proches, ces principes restent pertinents :

1. **Zero-knowledge by design** — adapté : aucun tiers extérieur ne doit pouvoir accéder aux données. Plus simple en perso : pas de "cloud Vivi", donc pas de risque côté éditeur. Le zero-knowledge devient automatique.
2. **Privacy by default** — toujours valable.
3. **Minimisation des données** — toujours valable.
4. **Crypto à l'état de l'art** — toujours valable, jamais de crypto maison.
5. **Auditable par construction** — moins critique en perso, mais bonne hygiène pour pouvoir relire son propre code dans 2 ans.

### Exigences fonctionnelles cœur (issues du Problem Statement, recalibrées)

- **Mobilité réelle** — accessible depuis n'importe quel appareil du porteur, à tout moment. C'était le besoin n°1 exprimé dès le départ.
- **Multi-appareils** — iPhone + Windows + autres machines éventuelles, sans config réseau pénible.
- **Mémoire persistante** — Vivi connaît le contexte du porteur, retient les choses.
- **Qualité conversationnelle suffisante** — local quand possible, hybride si nécessaire.
- **Actions concrètes, pas juste du chat** — repas, courses, RDV, finances, conseils (à préciser).

### Modèle de menace recalibré

Les menaces probables pour un usage perso + proches :

- **T1 — Voleur opportuniste** : ÉLEVÉE. Si Vivi est exposé sur Internet, scanners automatiques le trouveront. Mitigation : pas d'exposition publique directe, VPN ou tunneling (Tailscale-like).
- **T6 — Utilisateur (toi)** : ÉLEVÉE. Mauvais mot de passe, machine non patchée, oubli de backup. Mitigation : design qui rend les bons comportements faciles.
- **T7 — LLM lui-même** : MOYENNE. Hallucinations, prompt injection via contenus ingérés. Mitigation : cloisonnement des outils, validation des actions sensibles.

Menaces écartées (vs. version commerciale) :

- T2 (criminel ciblé) — peu de raison de cibler un utilisateur unique anonyme.
- T3 (étatique légal) — il n'y a personne à mettre en demeure, le code et les données sont chez le porteur.
- T4 (contributeur malveillant) — pas de contributeur externe.
- T5 (concurrent) — sans objet.

### Acquis méthodologiques

- Mode de travail par phases avec livrables écrits validés explicitement.
- Casquettes multiples (CPO, CISO, CTO, etc.) pour explorer les angles.
- Documentation systématique des décisions structurantes.

---

## Ce qui devient possible et qui ne l'était pas

1. **Compromis pragmatiques.** En commercial, chaque compromis fragilise une promesse à des utilisateurs. En perso, un compromis fragilise quoi ? Toi-même, et seulement si ça te gêne. Tu peux par exemple décider d'utiliser une API Claude/Mistral pour la qualité, et un LLM local pour les contenus sensibles, et ça ne pose problème à personne.
2. **Itération sans pression.** Pas de roadmap commerciale, pas de release notes, pas de SLA. Tu construis quand tu as envie, comme tu as envie.
3. **Stack technique qui te plaît.** Tu peux choisir tes outils par plaisir technique, pas par contrainte d'écosystème ou de recrutement.
4. **Pas de support à fournir.** Si un proche utilise Vivi et que ça casse, c'est de leur responsabilité de comprendre ou d'attendre.

---

## Documents Phase 0 — statut après pivot

| Doc | Statut |
|-----|--------|
| 01 — Problem Statement + Positionnement | Archivé. Le diagnostic du marché reste juste mais sans objet pour toi. |
| 02 — Persona #1 Camille | Archivé. Utile si retour au commercial un jour. |
| 03 — Persona #2 Thomas | Archivé. Idem. |
| 04 — Orientation éthique et structure | Partiellement archivé. Engagements 3 (self-hosted gratuit) et 4 (code ouvert) deviennent automatiques. Le reste sans objet. |
| 05 — Modèle de menace | Recalibré (cf. plus haut). |
| 06 — Pivot perso | **Ce document. Référence active.** |

---

## Phase 0 considérée comme terminée

La Phase 0 (cadrage stratégique) est close. La phase qui suit n'est plus "Vision produit commerciale" mais **Vision produit personnelle** : qu'est-ce que tu veux que Vivi fasse pour toi, concrètement, et dans quel ordre on l'attaque ?
