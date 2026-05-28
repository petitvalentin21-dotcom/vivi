# Vivi — Synthèse exécutive

**Date :** 25 mai 2026
**Statut :** Conception terminée, build à démarrer
**Documents de référence :** 16 livrables sur 5 phases (voir annexe)

---

## En une phrase

> *Vivi est un assistant personnel local qui décharge la charge mentale du quotidien, joignable depuis n'importe où, qui retient le contexte de la vie de son utilisateur, et qui prend l'initiative quand c'est utile.*

---

## En cinq points

1. **Projet personnel.** Vivi est conçu pour son porteur et un cercle proche éventuel. Pas de commercialisation, pas de structure juridique, pas de pression marketing.

2. **Local-first.** Tout tourne chez le porteur (PC fixe au démarrage, puis mini-PC dédié à 2-3 mois). Aucune donnée ne quitte le périmètre maîtrisé.

3. **Mobile en pratique.** Joignable depuis l'iPhone partout (via tunnel Tailscale), sans config réseau côté utilisateur.

4. **Proactif.** Vivi sollicite à 18h30 pour le dîner, le samedi pour la planification. Il ne se contente pas d'attendre qu'on lui parle.

5. **Premier domaine : Repas.** MVP focalisé sur la charge mentale culinaire (que mange-t-on ce soir, batch cooking week-end, liste de courses). D'autres domaines (mémoire, agenda, finances, dev) viendront après validation de l'usage quotidien.

---

## Genèse du projet

Vivi v1 existe déjà : un fork recadré d'un projet plus ancien (VIVI_IA), avec une stack FastAPI minimaliste, une IHM web localhost, un vault Obsidian comme source de vérité documentaire, et une intégration LM Studio comme provider LLM local. Cette base est saine, mais limitée à un usage devant le PC, sans mobilité réelle et sans persistance structurée.

La présente conception (mai 2026) refait *from scratch* la définition du besoin, sans présupposer ce qui existe. Le travail a démarré sur une hypothèse commerciale (Goliath vs. ChatGPT, structuration juridique, etc.), avant un **pivot conscient en milieu de Phase 0** : Vivi devient strictement personnel, le porteur conservant son job en parallèle et acceptant un horizon long sans revenu projet.

Cette synthèse documente l'état final de la conception personnelle, prête à attaquer le build.

---

## Le besoin (Phase 1)

Le porteur formule trois besoins distincts mais reliés autour du domaine Repas :

| Besoin | Moment | État d'esprit |
|--------|--------|---------------|
| **Décision quotidienne** : "ce soir on mange quoi ?" | Vers 18h30, fatigué | Délégation, "dis-moi" |
| **Planification batch cooking** : 2-3 batchs pour la semaine | Week-end, calme | Conception, projection |
| **Liste de courses** : vivante, complétable à la voix | En cours de semaine, ad hoc | Pragmatique, rapide |

La **priorité 1 est la décision quotidienne** : c'est là que la friction est la plus forte et la satisfaction immédiate. Si Vivi règle ça, il crée de la valeur perçue à chaque soir.

**Frustration sous-jacente** : le porteur fait du Leclerc Drive et a un "problème d'originalité des courses". Donc le besoin réel n'est pas seulement la mécanique — c'est la **stimulation créative** sans risque. D'où l'équilibre voulu entre **nouveauté** (découvertes) et **valeurs sûres** (rassurantes).

---

## L'architecture cible (Phase 3)

### Topologie physique

- **Démarrage** : PC fixe Windows allumé H24. RTX 3060 12 GB, 32 GB RAM. Mobilité iPhone via Tailscale.
- **Cible à 2-3 mois** : mini-PC dédié (Beelink/Geekom N100 ou équivalent, ~250-300 €). Le PC fixe redevient un PC normal.

### Architecture logicielle

**Principe directeur :** un seul Cœur LLM conversationnel, entouré de modules de code spécialisés. Pas de multi-agents (plusieurs LLMs dialoguant), mais des modules de code déterministes qui exposent des outils au LLM.

```
        Toi (iPhone via Tailscale)
                  │
                  ▼
            ┌─────────────┐
            │  Cœur LLM   │ ← Ministral 3 14B
            │  (Ollama)   │
            └──┬──────┬───┘
               │      │
        ┌──────┘      └──────┐
        ▼                    ▼
   Modules métier      Modules techniques
   - Recettes          - Conversation
   - Stock             - Scheduler
   - Courses           - Notifications
   - Préférences       
         │
         ▼
     SQLite (vault Obsidian pour les recettes Markdown)
```

Le LLM ne contient **aucune logique métier**. Les chiffres, les dates, les quantités sont calculés par du code Python déterministe. Les modules sont indépendants, exposent des outils via décorateur Python, et sont testables isolément.

### Stack technique

| Brique | Choix |
|--------|-------|
| Backend | Python 3.12+ / FastAPI / monorepo monoprocess |
| LLM | Ministral 3 14B Q4_K_M via Ollama |
| BDD | SQLite vanilla en MVP, SQLCipher post-MVP |
| ORM | SQLModel (sur SQLAlchemy 2.0) + Alembic |
| Client mobile | PWA SvelteKit + Tailwind |
| Tunnel mobilité | Tailscale |
| Push iPhone | Web Push API standard |
| Outillage | uv + ruff + pyright + pytest |

### Évolution future planifiée

- **Étape 1 (aujourd'hui)** : MVP Repas tel que décrit
- **Étape 2 (M+3 à M+12)** : ajout progressif de domaines (Mémoire, Rappels, Agenda, Finances)
- **Étape 3 (M+12+)** : si casquette "Vivi développeur" justifiée, passage en routage multi-modèles (un seul Cœur routeur, plusieurs LLMs spécialisés selon contexte)
- **Étape 4 (hypothétique)** : vrai multi-agents localisé seulement si cas légitime apparaît (tâche autonome longue)

---

## Sécurité et menaces (Phase 0 doc 05)

### Principes fondateurs

1. **Zero-knowledge by design** — l'éditeur Vivi (toi) ne peut pas accéder en clair aux données utilisateur (trivialement respecté en perso).
2. **Privacy by default** — toutes les options par défaut sont les plus protectrices.
3. **Minimisation** — pas de télémétrie, pas d'analytics par défaut.
4. **Crypto à l'état de l'art** — bibliothèques éprouvées uniquement (libsodium, age, OpenSSL), pas de crypto maison.
5. **Auditable par construction** — code commenté, lisible par un expert externe en quelques heures.

### Menaces principales

| Menace | Niveau | Mitigation |
|--------|--------|-----------|
| T1 — Voleur opportuniste | Élevé | Pas d'exposition publique, Tailscale uniquement |
| T6 — Toi qui fais une bêtise | Élevé | Backups chiffrés, design qui rend les bons comportements faciles |
| T7 — LLM lui-même (hallucinations, prompt injection) | Moyen | Cloisonnement tool calls, marquage contenus externes, limite 5 appels/tour |

### Menaces résiduelles acceptées explicitement

Le porteur a choisi de différer le chiffrement BDD au MVP et de ne pas activer BitLocker. Acceptés :
- MR1 — Cambriolage du PC
- MR2 — Fin de vie du disque sans wipe
- MR3 — Intervention SAV
- MR4 — Autre utilisateur Windows sur la machine

Ces menaces seront mitigées en migration SQLCipher post-MVP.

---

## Méthodologie de conception (Phase 2)

Le projet utilise une **équipe Vivi fictive** comme outil de pensée — 13 rôles répartis en 5 pôles, le porteur étant le seul CEO (le seul décideur).

| Pôle | Rôles |
|------|-------|
| Stratégie & produit | CEO (toi), CPO, COO |
| Technique | CTO, Architect, DevLead, QA |
| Sécurité & conformité | CISO, DPO |
| Recherche & contenu | ResearchLead, Linguiste |
| Suivi & démarche | Historien, Sponsor |

**Règle d'usage** : c'est un menu, pas un protocole. Les casquettes sont invoquées quand elles servent. La plupart des échanges du quotidien n'en utilisent aucune explicitement.

---

## Plan d'attaque pour le build (Phase 4-5)

### Décision Phase 4 : Option A — Continuité avec extension

On garde le repo v1 (`petitvalentin21-dotcom/vivi`) comme base. On l'étend selon 15 "FEAT" numérotés.

### Planning prévisionnel

| Lot | Durée loisir | Livrable |
|-----|--------------|---------|
| Lot 1 — Mise à niveau infra | 1-2 semaines | Doc agents à jour, Ollama branché, SQLite en place |
| Lot 2 — Modules métier de base | 2-3 semaines | Recettes + Stock + tool registry + prompts |
| Lot 3 — Boucle conversationnelle MVP | 1-2 semaines | "Ce soir on mange quoi ?" fonctionne sur PC |
| Lot 4 — Modules complémentaires | 1-2 semaines | Courses + Préférences |
| Lot 5 — Proactivité | 1-2 semaines | Scheduler + Notifications |
| Lot 6 — PWA et mobilité | 3-4 semaines | iPhone joignable + onboarding |
| Lot 7 — Validation MVP | 1-2 semaines | Critères de succès validés sur 3 mois |

**Horizon total : 12 à 16 semaines de soir/weekend.**

### Critères de succès MVP (à 3 mois d'usage)

1. Le porteur pose moins souvent "qu'est-ce qu'on mange ?" — Vivi sollicite avant.
2. Le porteur jette moins de bouffe — gestion des batchs vivants alerte avant péremption.
3. Le porteur arrive à Leclerc Drive avec une liste à jour.
4. Le porteur a découvert au moins 5 nouvelles recettes aimées.
5. L'usage est plus simple que le système actuel, pas plus compliqué.

Si une seule de ces conditions n'est pas remplie à 3 mois, on s'arrête et on questionne sincèrement.

---

## Garde-fous psychologiques

Le projet a déjà connu un pivot conscient au milieu de Phase 0 (abandon de la commercialisation). Trois principes ont émergé pour ne pas retomber dans le piège du sur-engagement :

1. **Loisir avec mission** — Vivi est porté en parallèle d'un job principal, horizon 3-5 ans sans revenu projet.
2. **Pas de pression de calendrier** — l'horizon 12-16 semaines est indicatif, pas contraignant. Une pause de 2 mois est acceptable.
3. **Validation par l'usage** — chaque lot du build doit produire quelque chose d'utilisable. Si on construit pendant 6 mois sans rien utiliser, c'est un signal d'alerte.

---

## Hors-scope explicite

| Hors scope MVP | Pourquoi |
|----------------|----------|
| Multi-agents (plusieurs LLMs dialoguant) | Sur-ingénierie, on a un cas qui ne le justifie pas |
| Scan automatique du frigo (caméra, IoT) | Gain marginal vs déclaration manuelle |
| Intégrations Carrefour/Picard/Auchan | Trop instable, formats propriétaires |
| Calcul nutritionnel détaillé | Hors besoin réel |
| Génération de recettes ex nihilo | Risque d'hallucination, on pioche dans le catalogue |
| Conseils diététiques | Hors scope, bordure réglementaire AI Act |
| Mobile App native iOS/Android | PWA suffit, pas de Mac pour build iOS |
| Mode hors ligne sur iPhone | Le porteur a presque toujours du réseau |
| Multi-utilisateurs distincts | V1 = 2 personnes mêmes préférences |
| Commercialisation, structure juridique | Pivot Phase 0 — projet personnel |

---

## Annexe — Inventaire des documents de conception

### Phase 0 — Cadrage stratégique
- 01 — Problem Statement et Positionnement *(archivé après pivot)*
- 02 — Persona #1 Camille *(archivé)*
- 03 — Persona #2 Thomas *(archivé)*
- 04 — Orientation éthique et structure *(partiellement archivé)*
- 05 — Modèle de menace *(recalibré, principes utiles)*
- 06 — **Pivot perso** *(référence active)*

### Phase 1 — Vision produit
- 01 — Vision produit v1
- 02 — Spec fonctionnelle Repas MVP

### Phase 2 — Méthodologie
- 01 — L'équipe Vivi

### Phase 3 — Architecture technique
- 01 — Topologie physique
- 02 — Architecture logicielle (Cœur LLM + modules)
- 03 — Choix LLM + runtime
- 04 — Stack backend
- 05 — Persistance et modèle de données
- 06 — Interface client iPhone
- 07 — Tool calling, prompts, authentification

### Phase 4 — Audit Vivi v1
- 01 — Audit Vivi v1 et plan d'extension

### Phase 5 — Build (à venir)
- *Pas encore démarré.*

---

## Prochaine étape

**Lot 1 — Mise à niveau infra :**
1. Intégrer les 17 documents de conception dans le vault Obsidian aux bons emplacements.
2. Mettre à jour AGENTS.md et CLAUDE.md pour refléter les décisions Phase 0-3 (notamment : Ollama autorisé, PWA autorisée, module Repas autorisé).
3. FEAT-16 : remplacer le client LM Studio par un client Ollama dans `app/llm/`.
4. FEAT-17 : ajouter SQLite + Alembic + structure `app/db/`.

Une fois ces 4 étapes faites, on est prêt à attaquer les vrais modules métier.

---

*Document de référence — à conserver dans `knowledge_vault/00_product/` une fois le vault unifié.*
