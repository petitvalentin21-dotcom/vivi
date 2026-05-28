# Vivi — Phase 0 : Problem Statement & Positionnement

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 0 — Cadrage stratégique

---

## Problem Statement v2

### Le problème

En 2026, toute personne qui veut un assistant IA personnel doit choisir entre deux compromis insatisfaisants :

**Compromis 1 — sacrifier sa vie privée pour l'utilité.**
ChatGPT, Gemini, Claude et leurs équivalents sont puissants, accessibles depuis n'importe quel appareil, et savent tenir une conversation longue. Mais chaque message envoyé part sur un serveur tiers, souvent américain. Le Cloud Act de 2018 autorise les autorités US à exiger l'accès à ces données même si elles sont hébergées en Europe. Pour les contenus quotidiens — finances, santé, agenda, vie de famille — cela représente un risque que la plupart des utilisateurs ignorent ou acceptent par défaut.

**Compromis 2 — sacrifier l'utilité pour sa vie privée.**
Les solutions open-source local-first existent (OpenClaw, Vellum, Jan.ai, AnythingLLM…) mais demandent toutes des compétences techniques significatives : ligne de commande, Docker, configuration réseau, parfois VPS personnel. Elles sont conçues par et pour des développeurs. L'utilisateur grand public ne peut pas s'en servir, et même les utilisateurs avancés finissent souvent par y brancher un LLM cloud (Claude, GPT) qui annule le bénéfice initial.

**Le résultat :** il n'existe aujourd'hui aucun assistant IA personnel qui soit simultanément :
- **Utile au quotidien** (mémoire persistante, accessible partout, prend des actions concrètes)
- **Réellement privé** (données qui ne sortent jamais d'un périmètre maîtrisé par l'utilisateur)
- **Accessible à un non-technicien** (installation et usage ne demandent pas de compétences dev)
- **Conforme par construction au cadre européen** (RGPD, AI Act)

### Pour qui

Deux profils convergent sur ce besoin :

1. **L'utilisateur grand public privacy-conscious** — connaît ChatGPT, refuse d'y mettre ses comptes, son agenda médical, ses échanges familiaux. Aujourd'hui il s'auto-censure ou utilise Apple Intelligence faute de mieux.
2. **L'utilisateur tech qui a essayé l'auto-hébergement et a abandonné** — comprend l'enjeu, a tenté Ollama / OpenWebUI / OpenClaw, s'est heurté au coût en temps de maintenance, ou à la qualité dégradée des modèles locaux par rapport au cloud.

À terme : extension B2B vers professions à secret (avocats, médecins, conseillers patrimoniaux, RH).

### Pourquoi maintenant

Quatre fenêtres s'alignent en 2026 :

- **Les modèles locaux deviennent vraiment utilisables.** Gemma 3, Llama, Qwen, DeepSeek tournent sur du matériel grand public avec une qualité acceptable pour 80% des usages quotidiens.
- **Le cadre réglementaire européen entre en vigueur.** L'AI Act s'applique pleinement à partir du 2 août 2026. Les obligations de transparence, traçabilité et conformité créent un avantage structurel pour qui les intègre nativement.
- **Le concurrent open-source #1 vient de partir.** Peter Steinberger, créateur d'OpenClaw, a rejoint OpenAI en février 2026. Le projet n'a pas de modèle économique, pas de roadmap mobile, pas de stratégie européenne. La fenêtre de positionnement est ouverte.
- **La défiance vis-à-vis des géants US augmente.** Les sanctions CNIL ont dépassé 487 M€ en 2025. L'attention publique aux questions de souveraineté numérique européenne n'a jamais été aussi haute.

### Ce que ça n'est pas

- Pas un clone de ChatGPT plus privé.
- Pas un outil pour développeurs.
- Pas un assistant 100% offline obligatoire (l'utilisateur doit pouvoir choisir : tout local, ou hybride avec un cloud souverain européen).
- Pas une app de productivité d'entreprise.

---

## Positionnement v1

### Phrase de positionnement

> *Vivi est l'assistant IA personnel pour celles et ceux qui refusent de choisir entre utilité et vie privée. Conçu en Europe, accessible depuis n'importe lequel de vos appareils, vos données ne quittent jamais votre périmètre de confiance.*

### Trois piliers différenciants

**1. Souverain par construction**
Les données restent chez vous (machine personnelle, NAS, ou cloud souverain européen au choix). Aucun transfert vers un acteur tiers non maîtrisé. Conformité RGPD et AI Act intégrée dès la conception, documentée, auditable.

**2. Accessible partout, simplement**
Vivi vous suit sur ordinateur, téléphone, montre. Installation en quelques clics. Pas de ligne de commande, pas de Docker, pas de configuration réseau. L'utilisateur ne pense pas à l'infrastructure — elle est conçue pour lui.

**3. Compagnon du quotidien, pas chatbot**
Mémoire persistante. Connaît vos préférences, votre contexte. Peut prendre des actions concrètes (agenda, courses, suivi financier, conseils). La relation se construit dans le temps, comme avec un assistant humain.

### Carte de positionnement

```
                    ACCESSIBLE NON-TECHO
                            ▲
                            │
          Apple Intel.      │
              ●             │
                            │           ChatGPT, Claude
                            │              Gemini
                            │                 ●
                            │
PRIVÉ ◀──────────── VIVI ──┼──────────────────────▶ NON PRIVÉ
                       ●    │
                            │
                            │     OpenClaw, Vellum,
                            │     AnythingLLM, Jan.ai
                            │           ●
                            │
                            ▼
                    TECHNIQUE / DEV
```

Vivi est volontairement positionné dans le quadrant **privé + accessible non-techo**, vide aujourd'hui à l'exception partielle d'Apple Intelligence (mais Apple-only, fermé, non-européen).

### Trois conditions de victoire

1. **L'installation doit être triviale.** « Je télécharge, j'ouvre, ça marche » — pas plus de friction qu'une app App Store.
2. **L'accès multi-appareil doit fonctionner sans config réseau.** L'utilisateur ne doit pas savoir ce qu'est une IP, un port, un firewall.
3. **La qualité conversationnelle doit être suffisante.** Inférieure à GPT-4o sur les tâches complexes est acceptable. Inférieure de moitié, non.

Si une seule de ces trois conditions n'est pas remplie, on échoue.

---

## Décisions structurantes actées en Phase 0

| # | Décision | Implication |
|---|----------|-------------|
| D1 | Vivi peut être tout-local OU hybride cloud souverain européen, au choix de l'utilisateur | Architecture modulaire avec adaptateurs LLM ; jamais de cloud US par défaut |
| D2 | Cible = grand public, pas développeurs | Toutes les décisions UX priorisent la simplicité sur la flexibilité |
| D3 | Conformité RGPD + AI Act intégrée dès la conception | DPO / CISO impliqués dès Phase 3, pas en patch |
| D4 | Double persona : utilisateur principal (toi) + cible marché | Risque de divergence assumé ; arbitrages explicites quand ça arrive |
| D5 | On s'inspire du code Vivi v1 mais on n'est pas tenu de le garder | Audit code v1 à faire avant Phase 4 |

---

## Points ouverts à trancher avant fin Phase 0

- [ ] Nom "Vivi" — vérifier disponibilité marque INPI/EUIPO + domaines `.com` `.eu` `.fr` `.ai`
- [ ] Persona cible #1 (utilisateur grand public privacy-conscious) — à construire en détail
- [ ] Persona cible #2 (utilisateur tech déçu) — à construire en détail
- [ ] Modèle économique — freemium, one-shot, abonnement, hybride ?
- [ ] Étude concurrentielle élargie : Vellum, Apple Intelligence en détail, Mistral usage personnel
- [ ] Modèle de menace initial (CISO) : qui attaque, comment, qu'est-ce qu'on protège
- [ ] Structure légale envisagée (auto-entreprise, SASU, association open-source + société commerciale)
