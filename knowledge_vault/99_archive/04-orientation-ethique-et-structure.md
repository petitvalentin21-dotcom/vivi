# Vivi — Phase 0 : Orientation éthique et structure

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 0 — Cadrage stratégique

---

## Contexte

À l'issue de l'étude comparée des modèles open-source / commercial (Mastodon, Sentry, Element/Matrix, Sublime/Bear), une décision philosophique a été prise. Mais la décision juridique correspondante est volontairement reportée pour éviter de se peindre dans un coin trop tôt.

---

## Orientation philosophique actée

**Vivi est conçu comme un projet d'intérêt général.**

L'objectif premier est de construire un assistant IA personnel souverain, accessible et respectueux des utilisateurs. La génération de revenu est un objectif secondaire, instrumental — un revenu doit exister pour pérenniser le projet, pas pour maximiser un retour sur investissement.

Cette orientation se traduit par cinq engagements de principe :

1. **Vivi ne sera jamais une entreprise qui revend des données utilisateurs.** Aucune monétisation indirecte de la donnée. Jamais. Cette clause sera inscrite dans les statuts de toute structure juridique future.

2. **Vivi ne prendra pas de capital de fonds d'investissement américains.** Les fonds français ou européens alignés sur la souveraineté numérique restent envisageables si la traction le justifie. Les VC US sont exclus par principe (incompatible avec le positionnement souverain et le Cloud Act).

3. **La version self-hosted de Vivi sera toujours pleinement fonctionnelle et gratuite.** Pas de "version castrée" pour pousser au cloud payant. La version cloud, si elle existe, apporte la commodité, pas les fonctionnalités essentielles.

4. **Le code de Vivi sera ouvert.** Licence à trancher (AGPL, FSL, BSL — voir points ouverts), mais l'auditabilité par la communauté est non-négociable. Camille n'a pas besoin de lire le code ; Thomas oui ; les deux comptent.

5. **La gouvernance sera transparente.** Décisions structurantes documentées et publiées. Rapport annuel d'activité dès qu'il y aura de l'activité à rapporter. Financement traçable.

---

## Contexte personnel du porteur

- **Rapport au revenu Vivi :** loisir avec mission. Job principal en parallèle, capacité à porter le projet 3 à 5 ans sans en vivre.
- **Plafonnement éventuel de la rémunération :** point ouvert. À retrancher si le projet atteint un seuil où la question devient concrète.
- **Acceptation explicite :** 18 à 36 mois sans revenu Vivi probable, et c'est OK.

Ce contexte est ce qui rend cette orientation viable. Une orientation non-profit pure exigerait sinon des compromis personnels (auto-exploitation, dépendance grants) qui ne sont pas acceptables.

---

## Décision sur la structure juridique : reportée

**La structure juridique de Vivi ne sera tranchée qu'au moment où elle devient nécessaire**, c'est-à-dire :

- au premier euro de revenu (don, vente, contrat),
- ou à la première intégration d'un contributeur externe régulier,
- ou à la première obligation légale (mise sur le marché d'un produit commercial),
- ou à un moment de Phase 2 / Phase 4 où ne plus décider deviendrait un frein.

### Pourquoi reporter

Une structure prématurée (création d'une association loi 1901 dès le démarrage) ferme des portes :

- Plafond de rémunération du dirigeant (~SMIC en association d'intérêt général).
- Difficulté à dissoudre / pivoter sans pertes fiscales (les actifs d'une asso ne peuvent pas être transmis gratuitement à une société commerciale détenue par le fondateur).
- Gouvernance collégiale obligatoire (~SCIC : 7+ sociétaires) ou contraintes lourdes (~fondation : dotation, CA).

En l'absence de revenu et de contributeurs externes, **aucune structure n'est requise**. Le code peut être publié sur GitHub sous une licence ouverte, hébergé sous un compte perso ou une organisation neutre. Le projet existe ; la personne morale n'existe pas encore.

### Trois variantes candidates au moment du choix

| Variante | Structure | Plafond rému | Liberté décisionnelle | Souplesse pivot |
|----------|-----------|--------------|----------------------|-----------------|
| **1a — Asso pure** | Association loi 1901 d'intérêt général | ~SMIC | Forte au début, contestable ensuite | Quasi nulle |
| **1b — SCIC** | Coopérative d'intérêt collectif | Libre | Partagée (7+ sociétaires min) | Faible |
| **1c — Hybride** | SASU + asso satellite + double licence | Libre côté SASU | Forte | Élevée |

**Pré-recommandation à l'horizon "premier revenu" :** la variante 1c (hybride) — SASU détenue à 100%, plus une association satellite qui détient le code open-source et anime la communauté. C'est en pratique le modèle Element/Matrix appliqué à un projet solo. À réévaluer le moment venu.

---

## Référence — pourquoi pas un Modèle 2 (Sentry-like) pur

Le Modèle 2 (Sentry-like) reste **la solution la plus pragmatique** d'un point de vue purement business. La raison de ne pas le choisir est philosophique : le porteur souhaite que la cohérence éthique soit *le coeur* du projet, pas une couche RSE ajoutée par-dessus une SASU classique. Le modèle 1c (hybride) reflète cette priorité — la composante associative n'est pas une décoration, elle est la propriétaire du code ouvert et le gardien de la mission.

Si la pratique montrait que ce montage est trop lourd ou bloquant, le repli sur Modèle 2 pur reste accessible. L'inverse (commencer en Modèle 2 puis passer en hybride) est beaucoup plus difficile.

---

## Implications immédiates pour la suite

1. **Aucune création de structure juridique avant la Phase 4 minimum.** Le projet existe sous forme de spec, doc, code public.
2. **Repository GitHub à créer sous compte personnel ou organisation neutre** quand le code sera prêt à être publié.
3. **Choix de licence à trancher avant publication code.** Trois options : AGPL-3.0 (la plus protectrice côté communauté), FSL (compromis Sentry), BSL (compromis HashiCorp). Point ouvert.
4. **Charte fondatrice à rédiger** quelque part en Phase 1 ou 2 — formaliser les 5 engagements ci-dessus avant que les questions deviennent concrètes.
5. **Le storytelling fondateur doit inclure cette intention dès le départ.** C'est un argument de différenciation pour Thomas et un signal de confiance pour Camille.
