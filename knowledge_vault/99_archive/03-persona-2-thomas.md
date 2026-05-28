# Vivi — Phase 0 : Persona #2

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 0 — Cadrage stratégique

---

## Thomas Vasseur, 34 ans — le développeur self-hosted déçu

### Identité

Vit à Nantes, maison avec jardin en deuxième couronne. En couple, pas d'enfant. **Développeur backend** dans une scale-up SaaS (~200 personnes), équipe plateforme. Salaire 70 k€ + BSPCE. Stack : Go, PostgreSQL, Kubernetes. MacBook Pro M3 (perso et pro mélangés). iPhone. Synology DS923+ chez lui avec 16 To. Pi-hole sur Raspberry Pi. Tailscale entre tous ses appareils.

**Lit** Hacker News quotidiennement, *Lobsters*, r/selfhosted, r/LocalLLaMA. Suit Simon Willison, Drew DeVault, et trois ou quatre devs français sur Mastodon (instance mamot.fr). N'est plus sur Twitter/X.

### Stack actuelle

**Auto-hébergé sur son NAS :**
- Nextcloud (fichiers, contacts, calendrier — synchro iPhone via DAVx⁵)
- Vaultwarden (gestionnaire mots de passe)
- Immich (photos, alternative à Google Photos)
- Jellyfin (média)
- Home Assistant (domotique)
- AdGuard Home (DNS filtrant)

**Tenté puis abandonné :**
- Ollama + Open WebUI — installé en mars 2025, abandonné après 2 mois. Qualité des modèles 7B/14B insuffisante, mises à jour cassantes.
- LibreChat — pareil.
- Mycroft / Leon — "pas mûrs", oubliés.

**Utilise quand même en SaaS :**
- Claude Pro (20 $/mois, payé par lui)
- GitHub (pas le choix au boulot)
- Gmail perso (n'a pas migré vers Proton par flemme)

### Rapport au numérique

Il sait tout faire. Si Vivi demandait une install CLI, il y arriverait en 10 minutes. **Mais il refuse** parce qu'il en a marre de maintenir des trucs le week-end. Il a passé l'âge où c'était fun de "faire marcher" les choses.

**C'est ça, le tech déçu : il a la compétence, il n'a plus l'envie.**

### Convictions privacy

- Convictions philosophiques solides. A lu Stallman, suit Snowden, signe les pétitions de La Quadrature du Net.
- Refuse le Cloud Act par principe, pas par effet d'aubaine.
- A migré sa famille vers Signal.
- Sait expliquer pourquoi le chiffrement iMessage n'est pas équivalent à celui de Signal.

**Différence avec Camille** : sa sensibilité est argumentée, militante. Il ne fera **jamais** confiance à une boîte qui ne montre pas son code.

### Frustrations explicites

1. **« Tout ce qui existe en local est inutilisable pour mon usage réel. »**
2. **« Je veux pas réinventer la roue à chaque mise à jour. »** Coût en temps de maintenance = ennemi #1.
3. **« Les modèles open-weight sont OK pour du toy, pas pour du sérieux. »** Sa barre = Claude/GPT-4.
4. **« OpenClaw c'est cool mais le créateur est parti chez OpenAI, on est encore baisés. »**
5. **« J'aimerais un truc européen qui ait l'air sérieux. »**

### Frustrations implicites

- Veut aussi des choses pour sa vie perso, mais ne le dirait jamais comme ça.
- Voudrait pouvoir recommander un outil à ses parents/sa sœur sans devoir le configurer lui-même.
- Espère secrètement que quelqu'un fasse le boulot à sa place — quelqu'un de fiable, transparent, européen.

### Comment il découvrirait Vivi

1. **Hacker News** : "Show HN: Vivi — local-first personal AI assistant, code open, conformité RGPD audité". Marketing sans code = fuite.
2. **r/selfhosted** et **r/LocalLLaMA** : benchmark vs ChatGPT, vs OpenClaw.
3. **Mastodon dev FR** : mention par un nom respecté.
4. **Conférence** : Devoxx France, OSXP.

### Ce qu'il est prêt à payer

| Tarif | Réaction probable |
|-------|-------------------|
| 0 €/mois | Attendu pour version self-hosted open-source. |
| 5 €/mois | Pour soutenir, donation-style. |
| 10–15 €/mois | OK si version hosted optionnelle ou features pro. |
| 50–100 €/an | **Préfère ce modèle** à un mensuel. Plus simple, plus engagé. |
| One-shot 80–150 € | **Très acceptable** pour licence "lifetime perso" (cf. Sublime Text, Bear). |
| Sponsoring GitHub 10 €/mois | Possible. |

### Objections probables

1. *« C'est encore du LLM cloud déguisé en local. »*
2. *« Quel modèle vous utilisez vraiment ? Si c'est Gemma 3B, c'est de la merde. »*
3. *« Le code est sur GitHub ? Licence ? »*
4. *« Vous êtes financés par qui ? »*
5. *« Et dans 2 ans quand vous fermez, je fais quoi de mes données ? »*
6. *« Vous prétendez RGPD-natif, prouvez-le. »*

### Phrases spontanées

- *« Si c'est pas open-source, je l'installe pas, point. »*
- *« Je veux bien payer, mais pas pour de la confiance aveugle. Montrez-moi le code. »*
- *« Mistral + Vivi, c'est ça la souveraineté. Faites-le bien. »*

---

## Implications business à mémoriser

1. **Thomas exige de l'open-source. Camille s'en fout.** Pour les deux à la fois, il faut une stratégie d'**ouverture du code** (au moins le client, sinon plus). Décision structurante à trancher.

2. **Thomas est un canal d'acquisition pour Camille.** S'il valide Vivi, il le recommande à sa famille, ses collègues, il en parle en dîner. *Conquérir Thomas = conquérir les Camille de son entourage.* Démesurément précieux pour le volume qu'il génère indirectement.

3. **Thomas paiera moins en cash mais investira plus en temps.** Contribue, signale bugs, propose features. Différenciation tarifaire potentielle : version self-hosted gratuite + version hosted payante.

4. **Le départ de Steinberger chez OpenAI a vacciné Thomas contre les "projets cool".** Il scrutera notre gouvernance, notre financement, notre engagement long terme.

5. **Question critique débloquée :** *quelle relation contractuelle entre la société commerciale Vivi et le code open-source ?*
   - Modèle Mastodon (gGmbH non-profit + dons)
   - Modèle Sentry (open-source + cloud commercial)
   - Modèle Element/Matrix (fondation + société de services)
   - Modèle Sublime/Bear (closed-source one-shot perpétuel)
   - À trancher avant le modèle économique.
