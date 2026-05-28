# Vivi — Phase 1 : Spec fonctionnelle Repas (MVP)

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 1 — Vision produit personnelle

---

## Cadrage

Premier domaine fonctionnel de Vivi. Cible l'utilisation quotidienne du porteur du projet (couple, batch cooking pour 2 personnes mêmes préférences). Objectifs : réduire la charge mentale "qu'est-ce qu'on mange ?", sortir de la routine des courses Leclerc Drive, capitaliser un catalogue personnel qui se bonifie.

---

## Modèle mental

### Concepts métier

| Concept | Définition |
|---------|------------|
| **Recette** | Description structurée d'un plat : ingrédients avec quantités, étapes, temps, portions, tags |
| **Batch** | Préparation d'une recette en plusieurs portions, qui se conserve N jours |
| **Stock** | État courant de ce qui est dispo à manger : batchs vivants + ingrédients de base présumés |
| **Liste de courses** | Liste vivante des choses à acheter, alimentée auto + manuel |
| **Préférence apprise** | Information accumulée dans le temps sur les goûts du porteur (recette aimée, ingrédient détesté, etc.) |

### Cycles temporels

```
SAMEDI                LUNDI-VENDREDI         WEEK-END SUIVANT
   │                       │                       │
   ├─ Planif batchs        ├─ Décision soir        ├─ Bilan
   ├─ Liste courses        ├─ MAJ stock auto       ├─ Suggestions
   └─ Drive ou magasin     └─ Ajout courses        └─ Cycle suivant
                              ad hoc
```

---

## Source des recettes

**Décision : catalogue interne (local) + LLM en complément.**

### Catalogue interne

- Stockage local chez l'utilisateur, format structuré (JSON ou SQLite à trancher Phase 3).
- Schéma : `{titre, ingredients[], etapes[], portions, temps_prep, temps_cuisson, conservation_jours, tags[], notes_perso, statut_valeur_sure, dernière_fois_cuisinée}`.
- Démarrage : 20-30 recettes de batchs cooking que le porteur connaît et aime, ajoutées par lui à la main ou via Vivi.
- Croissance : enrichi progressivement, soit par ajout manuel, soit par import sélectif depuis sources libres (Wikipedia recettes, TheMealDB FR avec tri).

### LLM en complément

- **Adaptation :** "j'ai pas de poireau, je remplace par quoi ?"
- **Variantes :** "le dahl, mais en version coco"
- **Conversation :** "raconte-moi cette recette" / "donne-moi la version courte"
- **Ne crée pas** de recettes ex nihilo dans la base de référence (risque hallucinations sur quantités).

---

## Mécanique de proposition

### Équilibre nouveauté / valeur sûre

Le porteur a explicité un besoin précis : "beaucoup de nouveauté ET des bases connues qui rassurent."

Une recette devient **"valeur sûre"** quand elle a été cuisinée plusieurs fois et notée positivement. C'est un statut acquis dans l'usage, pas un tag éditorial.

Proposition par défaut pour une semaine type :
- **1 batch "valeur sûre"** — pioché parmi les recettes au statut "valeur sûre"
- **1 batch "découverte"** — pioché parmi les recettes jamais ou peu cuisinées, ou variante LLM d'une valeur sûre

Le ratio est modulable :
- "Cette semaine je suis fatigué" → 2 valeurs sûres
- "Cette semaine on tente" → 2 découvertes
- "Comme d'hab" → mix par défaut

### Critères de pondération

Pour chaque proposition, Vivi tient compte de :
- Variété : éviter de re-proposer ce qu'on a mangé la semaine d'avant
- Saisonnalité : privilégier les ingrédients de saison (à terme, simple liste statique au démarrage)
- Préférences apprises : ne jamais proposer un ingrédient noté "détesté"
- Effort : si batch précédent compliqué, proposer simple ensuite (et inversement)

---

## Les trois moments d'usage

### 1. Décision quotidienne — "ce soir on mange quoi ?"

**Quand :** vers 18h30 — Vivi sollicite proactivement par notification push.
**Où :** iPhone principalement, en mobilité.
**Mode :** échange court, 1 à 3 options proposées, validation rapide.

**Logique :**
```
ÉTAT du stock
  ├─ Batch en cours
  │  ├─ Encore frais ? → propose en priorité 1
  │  └─ Bientôt périmé ? → propose en priorité 1 + urgence
  ├─ Plus de batch
  │  └─ Bascule mode "express" :
  │     ├─ Recettes "express" du catalogue (≤ 15 min)
  │     ├─ Option "tu commandes" si pas commandé depuis N jours
  │     └─ Cas exceptionnel : "à voir, j'improvise"
```

**Après choix :**
- Stock mis à jour automatiquement (1 portion consommée).
- Si batch épuisé, Vivi note "à racheter / repréparer".

### 2. Planification batch cooking — week-end

**Quand :** samedi matin ou dimanche selon habitude.
**Où :** indifférent — moment calme, peut être à la maison sur PC, ou tranquille en terrasse sur iPhone.
**Mode :** conversation plus longue, échanges, validation, ajustements.

**Logique :**
```
1. Vivi propose 2-3 batchs (1 valeur sûre + 1 ou 2 découvertes)
2. Porteur valide / change / ajuste portions
3. Vivi calcule la liste d'ingrédients
4. Vivi soustrait ce qui est déjà au stock présumé
5. Vivi produit la liste de courses finale
```

**Sortie :**
- Planning de la semaine (quels jours quel batch)
- Liste de courses (format exportable)

### 3. Liste de courses — vivante toute la semaine

**Quand :** au gré de la semaine + jour J.
**Où :** principalement iPhone, parfois PC.
**Mode :** ajouts rapides ("plus de café"), réorganisation finale par rayon.

**Fonctions :**
- Ajout vocal ou texte ad hoc ("plus de café")
- Marquage "fait" par cocher
- Réorganisation par rayon avant la course (juste avant Leclerc Drive ou trajet magasin)
- Export : texte simple, format Leclerc Drive (à terme — pas une intégration auto, juste un format facile à copier-coller dans leur interface)

---

## Apprentissage des préférences

Vivi capture, sans demander explicitement, des signaux :

| Signal | Conséquence |
|--------|-------------|
| Recette refusée 3 fois de suite | Marquée "peut-être à éviter" — demande discrète |
| Recette acceptée + validée comme aimée | Tag "valeur sûre" candidate |
| Ingrédient déclaré "j'aime pas" | Filtrage automatique |
| Batch fini sans gaspillage | Indicateur positif (bonnes portions, bon goût) |
| Batch jeté à moitié | Indicateur négatif — Vivi demande "à éviter ou problème ponctuel ?" |

L'apprentissage est **transparent et révisable** : le porteur peut consulter à tout moment "ce que Vivi a appris sur mes préférences" et l'éditer.

---

## Hors scope MVP (rappel)

- Scan automatique frigo (caméra, IoT)
- Lien comptes Carrefour/Picard/Auchan
- Calcul nutritionnel détaillé
- Génération de recettes ex nihilo dans la base de référence
- Multi-profils alimentaires distincts (v1 = 2 personnes mêmes préférences)
- Suivi budget alimentaire
- Conseils diététiques

---

## Critères d'acceptation MVP

Au bout de 3 mois d'usage :

1. Le porteur **pose moins souvent la question "qu'est-ce qu'on mange ?"** — Vivi sollicite avant.
2. Le porteur **jette moins de bouffe** — gestion des batchs vivants alerte avant péremption.
3. Le porteur **arrive à Leclerc Drive avec une liste à jour** — auto-générée + ajouts en cours de semaine.
4. Le porteur **a découvert au moins 5 nouvelles recettes** qu'il a aimées et marquées "valeur sûre".
5. **L'usage est plus simple que le système actuel**, pas plus compliqué.

---

## Implications archi (rappel pour Phase 3)

- **Catalogue local + schéma structuré** — pas juste de la mémoire LLM.
- **Stock = état persistant** — pas juste de la conversation, vraie BDD.
- **Notifications proactives push iPhone** — Vivi tourne en permanence quelque part.
- **Sync multi-appareils** — iPhone + PC voient le même état.
- **Tool calling LLM** — mise à jour stock, ajout liste de courses, etc.
