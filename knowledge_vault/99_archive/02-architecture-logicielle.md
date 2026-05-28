# Vivi — Phase 3 : Architecture logicielle (cœur unique, périphérie spécialisée)

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique

---

## Principe directeur

> *Vivi est un Cœur LLM unique qui dialogue avec l'utilisateur, entouré de modules de code spécialisés qu'il appelle quand il faut faire ou savoir quelque chose de précis. Aucun module ne contient de LLM. Aucun LLM ne contient de logique métier.*

Cette architecture prend le meilleur de deux écoles de pensée :

- De l'approche "LLM avec outils" : la simplicité, un seul interlocuteur conversationnel, débogage clair, performance.
- De l'approche "multi-agents" : le découplage des domaines fonctionnels, la possibilité d'ajouter sans refondre.

Sans en payer les coûts. Spécifiquement :
- **Pas de chaîne de LLMs qui dialoguent entre eux** (ce qu'on appelle improprement "multi-agents"). Une seule inférence par tour conversationnel.
- **Pas de LLM monolithique qui porte la logique métier.** Le LLM parle ; les modules calculent.

---

## Vocabulaire précis (à ne pas mélanger)

| Terme | Définition |
|-------|------------|
| **Multi-agents** | Plusieurs LLMs qui dialoguent entre eux pour résoudre une tâche. **Pas notre choix.** |
| **Multi-modèles** | Plusieurs LLMs invoqués par un routeur selon le contexte, sans dialogue entre eux. **Évolution future possible.** |
| **Multi-modules** | Un seul LLM + plusieurs modules de code spécialisés. **Notre choix MVP.** |

---

## Architecture MVP (l'état de référence pour Vivi v1)

### Schéma

```
                  ┌──────────────────┐
                  │   TOI (iPhone)   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  CŒUR LLM        │
                  │  (un seul)       │
                  │                  │
                  │  - dialogue      │
                  │  - appelle des   │
                  │    outils        │
                  └─┬────────┬────┬──┘
                    │        │    │
        ┌───────────┘        │    └────────────┐
        ▼                    ▼                 ▼
   ┌──────────┐       ┌──────────┐      ┌──────────┐
   │ Module   │       │ Module   │      │ Module   │
   │ Recettes │       │ Stock    │      │ Courses  │
   └──────────┘       └──────────┘      └──────────┘
        │                    │                 │
        └────────────────────┼─────────────────┘
                             ▼
                     ┌───────────────┐
                     │ Base de       │
                     │ données       │
                     └───────────────┘
```

### Composants

#### Cœur LLM
- Un seul modèle, exécuté localement (Mistral 7B / Gemma 9B / Qwen 14B selon perf matériel — choix précis traité plus tard en Phase 3).
- Reçoit l'historique conversationnel + la description des outils disponibles.
- Décide à chaque tour : répondre directement ou appeler un outil.
- Ne contient aucune logique métier persistante.

#### Modules métier
Chaque module est :
- Un **service indépendant** (process séparé, ou module logique d'un même process, à trancher selon performance).
- Une **API d'outils** que le Cœur LLM peut appeler.
- Possède sa propre **table ou son propre namespace BDD**.
- **Testable isolément**, sans LLM.

| Module | Rôle | Outils exposés au LLM |
|--------|------|-----------------------|
| **Conversation** | Mémoire courte de la session, historique | `get_historique`, `effacer_historique` |
| **Recettes** | Catalogue de recettes du porteur | `lister_recettes`, `chercher_recette`, `ajouter_recette`, `tagger_valeur_sure` |
| **Stock** | État courant : batchs vivants, ingrédients | `get_stock`, `marquer_portion_consommee`, `ajouter_batch`, `signaler_peremption` |
| **Courses** | Liste vivante | `get_liste_courses`, `ajouter_article`, `cocher_article`, `reorganiser_par_rayon` |
| **Préférences** | Apprentissage transversal | `noter_preference`, `get_preferences`, `est_aliment_deteste` |
| **Scheduler** | Déclenche les proactivités | `planifier_solicitation`, `annuler_solicitation` |
| **Notifications** | Envoie les push iPhone via Ntfy | `envoyer_notification` |

### Flux type — "Ce soir on mange quoi ?"

```
1. Toi : "Ce soir on mange quoi ?"
2. Cœur LLM : reçoit la question. Comprend = décision repas.
   Appelle l'outil get_propositions_repas_ce_soir().
3. Module Stock + Recettes : 
   - Lit la BDD
   - Trouve les batchs encore valides
   - Croise avec recettes express si nécessaire
   - Retourne 1 à 3 propositions structurées (dict Python ou JSON).
4. Cœur LLM : reçoit les options structurées.
   Les formule en langage naturel pour toi.
5. Toi : "Ok parfait."
6. Cœur LLM : confirmation. 
   Appelle marquer_portion_consommee(batch_id="dahl_samedi").
7. Module Stock : 
   - Décrémente le stock
   - Met à jour la BDD
   - Retourne confirmation.
```

### Garde-fous LLM (cf. modèle de menace Phase 0)

1. **Pattern read/write séparés.** Les outils de lecture sont sans danger. Les outils d'écriture sont audités. Les actions destructives demandent confirmation utilisateur.

2. **Limite d'appels d'outils par tour.** Maximum 5 appels d'outils par message utilisateur. Au-delà, retour forcé à l'utilisateur.

3. **Marquage des contenus externes.** Les recettes importées du web (futur) sont injectées avec marquage explicite `<contenu_externe>...</contenu_externe>`. Les outils sensibles refusent les demandes issues d'un contexte marqué non-confiance.

4. **Logs des appels d'outils.** Tous les appels sont loggués (identifiant, horodatage, succès/échec, **sans** payload sensible). Audit possible si comportement étrange.

5. **Mode "dry-run" pour les actions destructives.** Suppression de recettes, effacement d'historique, modification massive du stock : confirmation explicite obligatoire.

---

## Trajectoire d'évolution

### Étape 1 — MVP Repas (aujourd'hui)

Tel que décrit ci-dessus. Un Cœur LLM, 7 modules.

**Critère pour passer à l'étape 2 :** MVP utilisé au quotidien depuis 3 mois, critères de succès atteints.

### Étape 2 — Domaines additionnels (M+3 à M+12)

Ajout progressif de modules :

| Domaine | Modules ajoutés |
|---------|-----------------|
| Mémoire / Journal | `Notes`, `Journal`, `Recherche_semantique` |
| Rappels & Tâches | `Taches`, `Rappels_recurrents` |
| Agenda | `Agenda` (lecture intelligente d'un calendrier existant) |
| Suivi financier léger | `Comptes` (catégorisation), `Alertes_budget` |

**Pas de changement d'archi à cette étape.** On ajoute des modules, on déclare leurs outils au LLM, ça marche. C'est précisément ce que permet l'architecture hybride.

**Critère pour passer à l'étape 3 :** au moins une de ces deux conditions :
- Un Vivi LLM unique commence à montrer ses limites (latence, qualité dégradée sur certains domaines).
- Un nouveau domaine très différent en besoins LLM apparaît (cas typique : code).

### Étape 3 — Routage multi-modèles (M+12 ou plus, conditionné usage)

**Déclencheur réaliste : ajout d'une casquette Vivi-développeur.**

Pourquoi : un assistant code a besoin de modèles fondamentalement différents (Qwen Coder, DeepSeek Coder, ou Claude API) qui sont disproportionnés pour le quotidien.

Évolution architecturale :

```
                  ┌──────────────────┐
                  │   TOI            │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  CŒUR ROUTEUR    │
                  │  (léger)         │
                  └─┬────────────────┘
                    │
        ┌───────────┼──────────────┐
        ▼           ▼              ▼
   ┌─────────┐ ┌─────────┐  ┌──────────┐
   │ LLM     │ │ LLM     │  │ LLM      │
   │ Quoti-  │ │ Code    │  │ Conv.    │
   │ dien    │ │         │  │ longue   │
   │(Mistral)│ │(Qwen C.)│  │(Claude?) │
   └────┬────┘ └────┬────┘  └────┬─────┘
        │           │             │
        └───────────┴─────────────┘
                    │
                    ▼
            Modules (inchangés)
```

**Ce qui change :** introduction d'un Cœur Routeur. Conversation toujours unique du point de vue utilisateur, mais le routeur choisit quel LLM répond selon le contexte (intention détectée, mots-clés, mode explicite déclaré).

**Ce qui ne change pas :** les modules. Ils restent les mêmes, exposent les mêmes outils. C'est la grande force de cette archi : la migration n'impacte que la couche LLM.

**Hypothèse de design du routeur :** classifieur léger (règles + petit modèle de classification, voire petit LLM rapide en mode "intent detection"). Pas un LLM lourd qui réfléchit longuement avant d'orienter.

### Étape 4 — Cas particuliers de vrai multi-agents (hypothétique, non planifié)

**Pas dans le plan.** Mais à mentionner pour exhaustivité.

S'il apparaît un jour un besoin d'autonomie longue (Vivi qui travaille seul pendant des heures sur une tâche complexe, par exemple "explore tous mes documents et propose une synthèse"), alors **ce module spécifique** peut être implémenté en vrai multi-agents (planificateur → ouvriers → coordinateur).

**Règle :** ne pas multi-agents-iser tout Vivi. Localiser strictement aux cas où c'est justifié. La grande majorité des interactions resteront un seul LLM par tour.

---

## Décisions actées

| # | Décision | Réversibilité |
|---|----------|---------------|
| AD1 | Architecture hybride "Cœur LLM unique + modules code spécialisés" | Forte — c'est le mode de référence évolutif |
| AD2 | Aucune chaîne de LLMs dialoguant en MVP | Forte — réversible si cas légitime apparaît |
| AD3 | Modules indépendants, BDD propre par module ou namespace | Moyenne |
| AD4 | Le LLM ne contient pas de logique métier | Très forte — principe non-négociable |
| AD5 | Trajectoire : MVP → ajout modules → routeur multi-modèles → cas exceptionnels multi-agents | Forte — chaque étape déclenche sur critère explicite |

---

## Points à trancher en suite Phase 3

- **Choix précis du Cœur LLM MVP :** Mistral 7B, Gemma 9B, Qwen 14B, ou autre. Dépend perf PC fixe.
- **Choix du runtime LLM :** Ollama (recommandé, simple) vs LM Studio (Vivi v1) vs llama.cpp direct.
- **Choix de stack backend :** Python (FastAPI), Go, Node.js. Question de langage et frameworks.
- **Modèle de données :** SQLite (simple, fichier unique) vs Postgres (extensible, multi-process).
- **Communication inter-modules :** simples appels de fonction Python ? bus de messages ? API HTTP interne ?
- **Format de tool calling :** JSON schema standard, function calling natif du LLM choisi.
- **Interface client iPhone :** PWA (web), Tauri (cross-platform), Swift natif.

Chacun de ces points fera l'objet d'une décision ciblée. On les attaque l'un après l'autre.
