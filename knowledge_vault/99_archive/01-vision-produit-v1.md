# Vivi — Phase 1 : Vision produit v1

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 1 — Vision produit personnelle

---

## Énoncé court

> *Vivi est un assistant personnel qui décharge la charge mentale du quotidien. Il est joignable depuis n'importe où, retient le contexte de la vie de son utilisateur, et prend l'initiative quand c'est utile.*

---

## Premier domaine fonctionnel : Repas

Validé comme MVP. Trois besoins distincts mais reliés, par ordre de priorité :

### Priorité 1 — Décision quotidienne "ce soir on mange quoi ?"

Le besoin le plus fréquent, le moment de plus forte friction (fin de journée, fatigue, charge mentale). C'est là que Vivi crée la valeur perçue maximale **à chaque utilisation**.

**Scénario cible :**
- Vivi sollicite l'utilisateur en début de soirée (18h30 par exemple).
- Propose 1 à 3 options en fonction de ce qui est dispo dans les batchs cuisinés + ingrédients de base + variété récente + temps de préparation.
- Validation rapide. Vivi met à jour le stock.

### Priorité 2 — Planification du batch cooking week-end

Une fois par semaine (samedi typiquement), proposition de 2-3 nouveaux batchs pour la semaine à venir. Critères :
- Convient à 2 personnes (couple, mêmes préférences pour la v1 — à confirmer).
- Tient sur N jours de conservation.
- Variété par rapport à la semaine précédente.
- Génère la liste de courses associée (uniquement ce qui manque).

### Priorité 3 — Tenue de la liste de courses

Liste vivante : générée par P2, complétable à la voix ou au texte par l'utilisateur quand il pense à un truc (*"plus de café"*), réorganisable par rayon le jour J.

---

## Principes d'interaction

### 1. Proactif, pas passif

Vivi sollicite. Il n'attend pas que l'utilisateur ait l'idée d'ouvrir l'app. Il sait qu'il est 18h30 et qu'on n'a pas encore parlé du dîner.

**Implication technique majeure :** Vivi doit tourner en permanence quelque part. Pas une simple app iPhone. Voir architecture (Phase 3).

### 2. Sobre dans la sollicitation

Une notification "qu'est-ce qu'on mange ?" par soir, pas dix. Si l'utilisateur ne répond pas, Vivi ne harcèle pas. Il propose une option par défaut et passe.

### 3. Conversationnel court par défaut

Pendant la semaine : phrases courtes, réponses rapides. Vivi ne fait pas de monologues. Une question → une réponse → une action.

Le week-end (planification) : conversation plus longue acceptable, l'utilisateur est dispo et en mode conception.

### 4. Multimodal

Texte ET vocal. Le vocal est important : en cuisine, mains sales, ou en marchant tram. Pas obligatoire pour la v1 mais à anticiper dans l'archi.

### 5. Mémoire qui s'enrichit

Vivi apprend les habitudes : *"je sais que tu détestes les blettes"*, *"tu ne cuisines presque jamais le mercredi"*. Pas de feature distincte — c'est diffus dans toute l'utilisation.

---

## Exigences transversales (héritées Phase 0)

- **Mobilité réelle :** accessible depuis iPhone, n'importe où, sans config réseau pénible côté utilisateur.
- **Privacy by default :** données alimentaires = données personnelles (santé, budget, habitudes). Chiffrement at-rest, pas de partage tiers, pas de télémétrie.
- **Qualité conversationnelle suffisante :** local quand possible. Si LLM cloud (Mistral, Claude API), opt-in conscient et seulement pour les conversations non-sensibles.
- **Robuste aux indisponibilités :** si Vivi ne peut pas joindre son cerveau (panne réseau), il dégrade gracieusement (affiche le menu prévu en cache).

---

## Ce que la v1 ne fait PAS

| Hors scope v1 | Pourquoi |
|---------------|----------|
| Scan automatique du frigo (caméra, IoT) | Complexité explosive, gain marginal vs déclaration manuelle |
| Lien comptes Carrefour / Picard / Auchan | Trop d'intégrations spécifiques, instable |
| Calcul nutritionnel détaillé (calories, macros) | Hors besoin réel exprimé |
| Génération de recettes inédites | Vivi pioche dans un catalogue (les recettes connues de l'utilisateur) |
| Gestion de plusieurs profils alimentaires distincts | V1 = 2 personnes mêmes préférences |
| Suivi budget alimentaire | Pertinent mais à part — relève d'un futur domaine "Finances" |
| Conseils diététiques (régime, médical) | Hors scope, et bordure réglementaire AI Act |

---

## Domaines futurs (post-MVP repas)

Mentionnés à titre indicatif, sans engagement de calendrier. Ordre probable :

1. **Repas/courses** ← MVP actuel
2. **Mémoire / journal du quotidien** — capturer des notes, retrouver des infos, faire des liens (héritier du vault Obsidian Vivi v1)
3. **Rappels & tâches** — l'objet "à pas oublier" récurrent dans la vie
4. **Agenda intelligent** — synchro lecture seule de l'agenda existant, propositions proactives
5. **Suivi financier léger** — pas une banque, juste catégorisation et alertes
6. **Conseils & discussion ouverte** — usage généraliste façon ChatGPT, mais privé

Le passage d'un domaine au suivant se fait quand le précédent est *vraiment* stable et utilisé au quotidien, pas avant.

---

## Critères de succès MVP

Vivi v1 Repas est un succès si, dans 3 mois d'usage personnel, ces 4 affirmations sont vraies :

1. **Tu poses moins souvent la question "qu'est-ce qu'on mange ?"** parce que Vivi te sollicite avant.
2. **Tu jettes moins de bouffe** parce que Vivi t'aide à finir les batchs avant péremption.
3. **Tu vas faire les courses avec une liste à jour**, pas avec des bouts dans la tête.
4. **Tu trouves ça plus simple, pas plus compliqué**, que ton système actuel.

Si une de ces 4 affirmations est fausse à 3 mois, on a un problème. On ne continue pas en faisant semblant.

---

## Implications architecture à mémoriser pour Phase 3

1. **Vivi tourne H24 quelque part.** Trois pistes : PC/NAS perso allumé H24, VPS souverain (~4-5 €/mois), hybride. À trancher.
2. **Notifications push iPhone** = APNs requis. Compte développeur Apple ($99/an) ou solution alternative à creuser.
3. **Stock alimentaire = état persistant structuré.** Pas juste de la mémoire conversationnelle. Schéma de données à définir.
4. **LLM = besoin de tool calling** propre (mettre à jour le stock, créer une entrée liste de courses, etc.). Soit local (Gemma/Mistral local), soit cloud, soit hybride selon sensibilité.
5. **Multi-appareils :** iPhone principal + PC perso secondaire. État synchronisé. CRDT ou DB centrale.
