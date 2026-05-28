# Vivi — Phase 0 : Modèle de menace v1

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 0 — Cadrage stratégique
**Casquette :** CISO + DPO

---

## Préambule

Un modèle de menace réaliste répond à quatre questions :

1. Qu'est-ce qu'on protège ? (les actifs)
2. Contre qui ? (les attaquants plausibles)
3. Comment peuvent-ils nous atteindre ? (les vecteurs)
4. Qu'est-ce qu'on accepte de ne PAS protéger ? (les non-objectifs assumés)

Le dernier point est crucial. Un système qui "protège tout" ne se construit pas. Il faut accepter explicitement les compromis.

---

## 1. Actifs à protéger

### Niveau 1 — Catastrophique si compromis

- **A1. Données personnelles utilisateur** — conversations, mémoire persistante, contexte de vie. Finances, santé, relations, agenda. Si ça fuit, le projet est mort en 48h.
- **A2. Clés de chiffrement utilisateur** — si compromises, A1 devient lisible.
- **A3. Identité fondateur + équipe** — un fondateur dont l'identité est piratée peut être contraint à signer des updates malveillantes (chantage, supply chain attack).

### Niveau 2 — Grave si compromis

- **A4. Intégrité du code distribué** — injection dans une release = compromission de tous les utilisateurs simultanément.
- **A5. Infrastructure de mise à jour** — serveur de release, certificats de signature, pipeline CI/CD.
- **A6. Communauté et confiance** — réputation perçue plus que réelle. Une fausse alerte médiatique = exode.

### Niveau 3 — Important si compromis

- **A7. Données de télémétrie / usage** (si elles existent — choix à faire) — même anonymisées, peuvent réidentifier.
- **A8. Adresses email utilisateurs** — phishing ciblé.
- **A9. Données de facturation Vivi Cloud** (le jour où ça existera).

### Niveau 4 — Acceptable si compromis

- **A10. Site marketing** — défacement gérable.
- **A11. Logs anonymes d'erreur** (crashes, métriques perf) — perte mineure.

---

## 2. Attaquants réalistes

### T1. Voleur d'opportunité (probabilité ÉLEVÉE)

Script kiddie, ransomware operator, botnet. Motivation = monétisation rapide. Cibles = instances self-hostées mal configurées exposées sur Internet. Pas spécifique à Vivi, opportuniste.

### T2. Criminel ciblé (probabilité MOYENNE)

Groupe organisé. Valeur d'une base utilisateur Vivi = très élevée (données ultra-personnelles). Exfiltration en masse, rançon, revente. Capacité : phishing sophistiqué, supply chain, 0-day si ROI. Cible probable : infra de release Vivi.

### T3. Attaquant étatique (probabilité FAIBLE, conséquences ÉNORMES)

Services de renseignement (US Cloud Act, étrangers, ou français en cas d'enquête). Motivation : accès à des cibles spécifiques. Capacité technique illimitée, contraintes légales selon juridiction. **Cible probable : demande d'accès par voie légale, pas attaque technique.**

### T4. Ex-employé / contributeur malveillant (probabilité FAIBLE-MOYENNE à terme)

Contributeur devenu hostile, prestataire externe. Motivation : vengeance, idéologie, gain financier. Capacité : niveau d'accès accordé.

### T5. Concurrent (probabilité FAIBLE)

Pas attaque technique frontale (trop risqué légalement). Plutôt : FUD, débauchage, acquisition.

### T6. Utilisateur lui-même (probabilité ÉLEVÉE)

Utilisateur légitime se compromettant par négligence (mot de passe faible, machine non patchée).

### T7. AI lui-même (probabilité MOYENNE, sous-estimée)

LLM intégré. Pas de motivation, mais alignement imparfait : hallucinations, prompt injection via contenus tiers ingérés, fuite de contexte via tool use mal cloisonné.

### Attaquants écartés (assumés)

- APT nation-state ciblant Vivi spécifiquement.
- Evil maid attaque physique persistante.

---

## 3. Vecteurs d'attaque (STRIDE adapté)

### Sur A1 (données utilisateur)

| Vecteur | Réaliste ? | Mitigation envisagée |
|---------|-----------|---------------------|
| Vol appareil utilisateur | Oui (T6) | Chiffrement at-rest avec clé dérivée d'un secret utilisateur |
| Malware machine utilisateur | Oui (T1) | Hors périmètre Vivi (responsabilité OS) — chiffrement en mémoire possible |
| Interception réseau synchro multi-appareils | Oui (T1-T2) | Chiffrement bout-en-bout obligatoire, pas TLS seul |
| Exfiltration via prompt injection | Oui (T7) | Cloisonnement strict tool calls, validation sorties |
| Requête légale à l'éditeur Vivi | Oui (T3) | **Zero-knowledge by design : Vivi ne doit pas pouvoir techniquement accéder aux données** |

### Sur A4-A5 (intégrité code & release)

| Vecteur | Réaliste ? | Mitigation envisagée |
|---------|-----------|---------------------|
| Compromission compte GitHub mainteneur | Oui (T2) | 2FA hardware (clé physique), commits signés GPG |
| Compromission CI/CD | Oui (T2) | Builds reproductibles, pipeline transparent |
| Compromission certificat de signature | Oui (T2) | Hardware security key dédié, jamais sur machine de dev |
| Injection par contributeur | Oui (T4) | Code review obligatoire 2 yeux dès le premier contrib externe |
| Dépendance NPM/PyPI compromise | Oui (T2) | Verrouillage versions, audits réguliers, minimisation deps |

### Cas particulier T3 (étatique légal)

Le but n'est pas de protéger un terroriste contre la DGSI, mais d'assurer que Vivi (éditeur) ne peut pas être *contraint* de remettre les données d'un utilisateur, parce qu'il ne les a pas.

**Conclusion : architecture zero-knowledge non-négociable.** L'éditeur Vivi ne doit JAMAIS avoir accès aux données utilisateurs en clair, même côté Vivi Cloud. Sinon le Modèle 1 (éthique souveraine) est un mensonge.

---

## 4. Non-objectifs assumés

1. **Vivi ne protège pas contre un attaquant ayant un accès root persistant à la machine utilisateur.** Responsabilité de l'OS et de l'utilisateur.
2. **Vivi ne protège pas contre l'utilisateur qui partage volontairement ses données ailleurs.** Copier-coller vers ChatGPT = responsabilité utilisateur.
3. **Vivi ne protège pas contre la coercition physique de l'utilisateur.**
4. **Vivi ne protège pas contre les analyses de trafic réseau passives.** FAI sait quand tu utilises Vivi Cloud, pas le contenu.
5. **Vivi ne garantit pas l'absence d'hallucination du LLM.** Mitigation possible (citations, modes de confiance), garantie impossible.
6. **Vivi ne garantit pas la disponibilité 24/7 en self-hostée.** Sauvegardes triviales = oui. Haute dispo = autre produit.
7. **Vivi n'est pas conçu pour threat models extrêmes** (journaliste zone hostile, dissident sous régime). Bénéfices incidents possibles, mais leur threat model exige Tails / Qubes OS.

---

## 5. Cinq principes de sécurité fondateurs

Si tout le reste se perd, ces cinq principes guident toute décision technique :

1. **Zero-knowledge by design.** L'éditeur Vivi ne doit jamais pouvoir techniquement accéder en clair aux données d'un utilisateur. C'est le prix de la cohérence.

2. **Privacy by default, pas privacy by option.** Toutes les options par défaut sont les plus protectrices. L'utilisateur peut assouplir consciemment, jamais l'inverse.

3. **Minimisation des données.** Ne pas collecter ce qu'on n'utilise pas. Aucun analytics par défaut. Aucune télémétrie envoyée hors machine sans opt-in explicite.

4. **Auditable par construction.** Tout ce qui touche aux données utilisateur est dans du code ouvert, lisible, commenté. Composants critiques lisibles par un expert externe en quelques heures.

5. **Cryptographie à l'état de l'art, pas inventée.** Aucune crypto maison. Bibliothèques éprouvées (libsodium, age, OpenSSL). Algorithmes ANSSI / NIST.

---

## 6. Implications pour l'architecture (Phase 3)

1. **E2EE obligatoire pour la synchro multi-appareils.** Clés dérivées localement, Diffie-Hellman.
2. **Vivi Cloud = relais zero-knowledge.** Stockage blobs chiffrés dont Vivi n'a pas la clé. Hébergement SecNumCloud / souverain.
3. **Le LLM est un actif à risque (T7).** Tool calls cloisonnés. Pattern : agent_lecteur + agent_executeur séparés, garde-fou humain pour actions sensibles.
4. **AGPL favorable** pour forcer transparence des forks commerciaux opaques.
5. **Single point of failure mainteneur.** Inscrire l'objectif "deux personnes habilitées à signer les releases" avant première version commercialisée.

---

## Points durs identifiés (à traiter en Phase 1+)

- **Récupération de compte sans backdoor.** Pas de "compte Vivi" récupérable par mot de passe oublié. Stratégies : clés de backup imprimables, Shamir secret sharing, recovery contacts.
- **Disponibilité multi-appareils sans serveur de confiance.** CRDT chiffrés, relais aveugles. Non-trivial.
- **AI Act : classification risque.** Assistant personnel polyvalent = "risque limité" ou "haut risque" si conseils médicaux/financiers personnalisés ? À investiguer DPO.
