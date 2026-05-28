# Vivi — Phase 3 : Topologie physique

**Statut :** ✅ Validé le 24 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique

---

## Décision

**Topologie A pour le démarrage, Topologie D comme cible à 2-3 mois.**

### Topologie A — PC fixe allumé H24 (démarrage)

```
                Internet
                   │
        ┌──────────┴──────────┐
        │ Tunnel sécurisé      │
        │ (Tailscale)          │
        │                      │
   ┌────▼────┐         ┌──────▼──────┐
   │ iPhone  │◄───────►│  PC fixe    │
   │ Client  │         │  - Vivi     │
   │ Vivi    │         │  - LLM local│
   │         │         │  - BDD      │
   │         │         │  - Scheduler│
   └─────────┘         └─────────────┘
                              │
                              ▼ (push)
                       Service notif
                       (Ntfy ou Pushover)
```

**Composants :**
- **PC fixe :** porte tout le backend Vivi, LLM local, base de données, scheduler des proactivités.
- **iPhone :** client (PWA ou app native), reçoit push notifications.
- **Tailscale :** tunnel sécurisé entre iPhone et PC, sans config réseau, sans port ouvert.
- **Service de push :** Ntfy auto-hébergé sur le PC, ou Pushover (5 € one-shot).

**Critères d'usage à valider sur 2-3 mois :**
1. Vivi t'apporte réellement de la valeur quotidienne.
2. Le PC allumé H24 ne pose pas de problème pratique (bruit, conso, espace).
3. La connexion Tailscale fonctionne bien depuis l'iPhone en mobilité.

Si ces 3 critères sont validés → on migre vers D.

### Topologie D — Hybride avec mini-PC dédié (cible)

Le PC fixe redevient un PC normal qu'on éteint. Vivi déménage sur un mini-PC dédié (~250-300 € pour un Beelink/Geekom N100 16 GB). Le reste de l'archi est identique.

---

## Principes d'architecture portable

Pour rendre la migration A → D triviale, tous les choix d'archi suivent ces principes :

1. **Composants conteneurisés ou en services isolés.** Chaque brique (LLM, backend, BDD, scheduler) tourne en process indépendant. Idéalement Docker ou systemd-services.

2. **Configuration externalisée.** Aucune adresse en dur, aucun path en dur. Tout passe par fichier de config / variables d'environnement.

3. **Données dans un volume identifiable.** Toute la donnée persistante dans un seul répertoire facile à `tar / rsync` pour migration.

4. **Client agnostique de la machine.** L'iPhone parle à une adresse Tailscale qui change juste de host lors de la migration. La couche transport est invariante.

5. **Pas de dépendance Windows-specific.** Le PC fixe est sous Windows, le futur mini-PC sera probablement sous Linux. Tous les composants doivent tourner sur les deux — préférer WSL2 sur le PC fixe, ou containers Docker directement.

---

## Composants à installer sur le PC (démarrage)

| Composant | Rôle | Choix candidat |
|-----------|------|---------------|
| Runtime LLM | Exécute le modèle local | Ollama (recommandé) ou LM Studio (v1 utilisait celui-ci) |
| Backend Vivi | Logique métier, API, scheduler | À concevoir Phase 3 — choix de stack |
| Base de données | Persiste recettes, stock, conversations | À choisir : SQLite (simple) ou Postgres (extensible) |
| Service push | Envoie notifications iPhone | Ntfy auto-hébergé |
| Tunnel mobilité | Lien sécurisé iPhone↔PC | Tailscale (compte gratuit) |
| Client iPhone | Interface | PWA d'abord, app native plus tard |

---

## Coûts engagés

### Démarrage (Topologie A)
- **Matériel :** 0 €
- **Logiciel :** 0 € (Tailscale gratuit, Ntfy gratuit, LLM open-source, BDD open-source)
- **Récurrent :** ~80 €/an d'élec PC fixe en plus
- **Optionnel :** Pushover 5 € one-shot si on préfère à Ntfy

### Migration cible (Topologie D)
- **Matériel one-shot :** 250-300 € (mini-PC)
- **Récurrent :** ~20 €/an d'élec mini-PC (à la place des 80 € du PC fixe)
- **Économie nette à terme :** ~60 €/an + retour du PC fixe en machine normale

---

## Points ouverts à trancher en suite Phase 3

- **Choix de stack backend** (langage, framework) — prochain sujet
- **Architecture logicielle interne** : monolithe vs multi-services, multi-agents
- **Modèle de données** (SQLite vs Postgres, schémas)
- **Choix du LLM local** (Mistral, Gemma, Qwen — tailles, quantizations)
- **Choix d'interface client** (PWA, Tauri, app native)

---

## Sécurité de cette topologie

Les principes de Phase 0 § 5 appliqués ici :

- **Zero-knowledge** : trivialement respecté en topologie A (tout est chez toi).
- **Privacy by default** : aucune télémétrie sortante par défaut.
- **Minimisation** : seules les données nécessaires à Vivi sont collectées (pas d'analytics).
- **Crypto à l'état de l'art** : Tailscale utilise WireGuard, chiffrement à l'état de l'art. Au niveau BDD : chiffrement at-rest selon module (SQLCipher si SQLite, pgcrypto si Postgres).
- **Auditable** : tous les composants sont open-source.

Menaces résiduelles spécifiques à A :
- Si ton PC fixe est compromis (malware), Vivi est compromis. Mitigation : Vivi n'a pas de privilèges élevés, tourne sous un utilisateur dédié.
- Tailscale a vu un fournisseur tiers (gentil) entre tes appareils. Pour durcir : Headscale auto-hostée plus tard.

Ces résiduelles sont acceptables pour un usage perso. Si jamais on partage à des proches, on réévalue.
