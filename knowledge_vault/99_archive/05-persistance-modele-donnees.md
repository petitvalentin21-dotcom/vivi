# Vivi — Phase 3 : Persistance et modèle de données

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique
**Casquette :** CTO + CISO + Architect

---

## Décisions actées

| # | Décision |
|---|----------|
| DB1 | Base de données = **SQLite** |
| DB2 | ORM = **SQLModel** (sur SQLAlchemy 2.0) |
| DB3 | Migrations = **Alembic** |
| DB4 | Chiffrement BDD MVP = **aucun (SQLite vanilla)** |
| DB5 | Backups = **chiffrés (restic ou borg)** dès le MVP |
| DB6 | Pas de chiffrement disque BitLocker (décision CEO) |
| DB7 | Migration cible post-MVP : SQLCipher quand l'usage sera validé |

---

## Justification des choix

### Pourquoi SQLite

1. **Un seul fichier** — portable, sauvegardable, lisible par tout outil SQL.
2. **Embarqué dans Vivi** — pas de service séparé à lancer, à maintenir, à monitorer.
3. **Largement suffisant en volume** — un usage perso génère des Mo, pas des To. SQLite tient sans peine jusqu'à des centaines de Go.
4. **Performance excellente en lecture** — meilleure que Postgres pour les patterns "lots de petites requêtes locales".
5. **Path de migration vers Postgres** trivial si jamais utile (SQLAlchemy compatible avec les deux dialectes).

### Pourquoi SQLModel

1. **Conçu par le créateur de FastAPI** — intégration parfaite, pas de friction.
2. **Combine Pydantic et SQLAlchemy** — une seule définition de modèle sert d'ORM et de validation API.
3. **Construit sur SQLAlchemy 2.0** — la puissance et l'évolutivité sont préservées.
4. **Réduit le code répétitif** — pas de duplication entre schémas API et modèles BDD.

### Pourquoi Alembic

Standard de facto pour les migrations SQLAlchemy. Support rollback, génération auto depuis les modèles, mature.

---

## Stratégie de chiffrement et menaces acceptées

### Stratégie MVP (3 premiers mois)

- **SQLite vanilla** (pas SQLCipher).
- **Pas de BitLocker disque** — décision CEO assumée.
- **Backups chiffrés** dès le MVP via `restic` ou `borg`.

### Justification

Le porteur a choisi de **différer la complexité chiffrement** au profit de la vélocité MVP. Cette décision est cohérente avec la philosophie "valider l'usage avant d'engager la complexité technique" qui guide le projet depuis le pivot perso.

### Menaces résiduelles acceptées explicitement

Ces menaces ne sont **PAS** mitigées dans l'architecture MVP. Le porteur en est informé et accepte ce niveau de risque :

| # | Menace | Conséquence si elle se réalise | Acceptée car |
|---|--------|--------------------------------|-------------|
| MR1 | **Cambriolage** : le PC fixe est volé chez toi | Voleur a accès à toutes tes données Vivi en clair (finances, agenda, conversations privées) | Probabilité jugée faible par le porteur |
| MR2 | **Fin de vie du disque** : SSD/HDD remplacé sans wipe sécurisé | Disque revendu/jeté contient les données Vivi | À mitiger manuellement le jour venu (wipe ou destruction physique) |
| MR3 | **Intervention SAV** : PC apporté en réparation | Technicien a accès au disque | Rare, mais à anticiper |
| MR4 | **Autre utilisateur Windows sur la machine** lit le fichier `.db` | Données lisibles sans authentification | Acceptable si tu es seul utilisateur, à revoir si machine partagée |

**Ces menaces seront mitigées en migration SQLCipher** (post-MVP), qui chiffre la BDD avec un mot de passe que seul Vivi connaît. MR1, MR3, MR4 deviennent alors résolus. MR2 reste à gérer manuellement (wipe disque en fin de vie).

### Pourquoi les backups sont chiffrés dès le MVP (et pas la BDD)

Asymétrie volontaire :
- **La BDD** est sur le PC dans ton salon : risque relatif faible (cf. décision CEO).
- **Les backups** sortent du PC : vers un disque externe, un NAS, un cloud (même souverain). Ils sont **plus exposés** par nature.

Donc même si on n'investit pas dans le chiffrement BDD au MVP, **chiffrer les backups est non-négociable**. C'est ce qui empêche qu'une fuite de backup vers OneDrive/Drive/NAS familial expose tes données.

### Migration SQLCipher post-MVP

Quand l'usage est validé (3 mois), migration vers SQLCipher :

1. **Trigger** : décision CEO après MVP réussi.
2. **Effort** : ~1-2 jours (compilation Windows + script migration + tests).
3. **Risque migration** : faible (SQLCipher est mature, le script `ATTACH ... KEY` est standardisé).
4. **Impact code** : minime (configuration SQLAlchemy uniquement, les modèles SQLModel restent identiques).

---

## Stratégie de backups (à appliquer dès le MVP)

### Quoi sauvegarder

- Le fichier SQLite Vivi (`vivi.db`).
- Le dossier de config (`.env`, prompts, modelfiles Ollama).
- Le catalogue de recettes (s'il est externalisé en Markdown, à voir Bloc D).

### Outil recommandé

**Restic** (cross-platform, Windows OK, chiffrement par défaut, déduplication, snapshots).

```bash
# Init du dépôt (une fois)
restic init --repo /chemin/vers/backups

# Backup automatique (à programmer en tâche planifiée Windows)
restic backup C:\Vivi\data --repo /chemin/vers/backups

# Restauration (en cas de besoin)
restic restore latest --target C:\Vivi\restore --repo /chemin/vers/backups
```

### Cible de backup

Trois cibles possibles, ordre de souveraineté :
1. **Disque externe USB** dédié, branché 1×/semaine — souveraineté maximale.
2. **NAS local** si tu en montes un dans le futur.
3. **Cloud souverain européen chiffré** (Scaleway Object Storage, Infomaniak kDrive, OVH Cloud Archive) — utile si tu veux du off-site.

À trancher au moment de l'install. Pour le MVP, le **disque externe** est suffisant.

### Fréquence et rétention

- **Quotidien** automatique (tâche planifiée Windows).
- **Rétention** : 7 quotidiens, 4 hebdomadaires, 6 mensuels. Restic gère ça avec `forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6`.

---

## Modèle de données — esquisse (à affiner par module)

Note : les schémas précis seront définis par module dans leur `models.py`. Ce qui suit est l'esquisse de haut niveau pour valider la cohérence d'ensemble.

### Tables principales (par module)

#### Module Recettes
```
recettes
├── id (uuid)
├── titre (str)
├── ingredients (JSON list of {nom, quantite, unite})
├── etapes (JSON list of str)
├── portions (int)
├── temps_prep_min (int)
├── temps_cuisson_min (int)
├── conservation_jours (int, nullable)
├── tags (JSON list of str)
├── notes_perso (str, nullable)
├── statut_valeur_sure (bool, default false)
├── nb_fois_cuisinee (int, default 0)
├── dernier_fois_cuisinee (datetime, nullable)
├── created_at (datetime)
└── updated_at (datetime)
```

#### Module Stock
```
batchs_en_cours
├── id (uuid)
├── recette_id (uuid, FK)
├── date_preparation (date)
├── portions_initiales (int)
├── portions_restantes (int)
├── date_peremption_estimee (date)
└── notes (str, nullable)

ingredients_base_presents
├── id (uuid)
├── nom (str)
├── quantite_estimee (str, ex: "1 paquet", "à moitié plein")
├── confiance (enum: certain, probable, incertain)
└── derniere_maj (datetime)
```

#### Module Courses
```
liste_courses
├── id (uuid)
├── article (str)
├── quantite (str, nullable)
├── rayon (enum, nullable)
├── ajoute_par (enum: auto, manuel, voix)
├── statut (enum: a_acheter, achete, abandonne)
├── created_at (datetime)
└── coche_at (datetime, nullable)
```

#### Module Préférences
```
preferences
├── id (uuid)
├── type (enum: aliment_aime, aliment_deteste, allergie, regime)
├── element (str)
├── force (int, 1-5)
├── source (enum: declare, infere)
└── created_at (datetime)
```

#### Module Conversation (historique)
```
conversations
├── id (uuid)
├── started_at (datetime)
└── ended_at (datetime, nullable)

messages
├── id (uuid)
├── conversation_id (uuid, FK)
├── role (enum: user, assistant, tool)
├── content (text)
├── tool_calls (JSON, nullable)
├── created_at (datetime)
```

#### Module Scheduler
```
solicitations_programmees
├── id (uuid)
├── type (enum: dîner_soir, planif_weekend, custom)
├── horaire (cron expression)
├── actif (bool)
└── derniere_execution (datetime, nullable)
```

### Discipline de modélisation

1. **UUID en clé primaire**, pas d'auto-increment. Permet la sync multi-appareils future sans collision.
2. **created_at / updated_at** sur toutes les tables "objets métier".
3. **Soft delete par défaut** (colonne `deleted_at`) — on n'efface pas, on cache. Permet rollback.
4. **JSON pour les structures imbriquées** simples (ingrédients, étapes, tags). Pas de table normalisée pour ça → c'est de la donnée toujours lue avec son objet parent.
5. **Pas de tables croisées entre modules** → pas de `recettes_x_courses`. Si lien nécessaire, c'est par référence d'ID dans un JSON, et la logique de jointure est dans le module qui en a besoin.

---

## Points encore ouverts (Bloc D suivant)

- **Interface client iPhone** : PWA / Tauri / Swift natif ?
- **Format tool calling Ollama** : appel direct API ou via wrapper Pydantic ?
- **Stratégie de prompts** : où vivent les prompts système, format, versioning.
