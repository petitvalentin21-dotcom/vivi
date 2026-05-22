# Frontières des agents

## Hiérarchie de confiance

| Action | Agent autonome | Dev agent orchestré | Humain |
|---|---|---|---|
| Lire le code | ✅ | ✅ | ✅ |
| Proposer dans une PR | ✅ | ✅ | ✅ |
| Merger une PR | ❌ | ❌ | ✅ |
| Modifier `.env`, secrets | ❌ | ❌ | ✅ |
| Migration BDD | ❌ (propose) | ❌ (propose) | ✅ |
| Déployer | ❌ | ❌ | ✅ |
| Ajouter une dépendance | ❌ (propose) | ❌ (propose) | ✅ |
| Modifier `CLAUDE.md` ou `.claude/*` | ❌ | ❌ | ✅ (validé à deux) |
| Toucher l'infra (Terraform, k8s) | ❌ | ❌ | ✅ |

---

## Chemins protégés

Jamais modifiés sans validation humaine explicite :

- `.env*`
- `secrets/`, `**/secrets/`
- `**/migrations/`
- `**/.github/workflows/` (sauf demande explicite)
- `CLAUDE.md` et `.claude/`
- `infrastructure/`, `terraform/`, `k8s/`, `docker-compose.prod.*`
- `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `composer.lock` (sauf si l'objectif est d'ajouter une dépendance validée)

---

## Conditions d'escalade obligatoire

L'agent s'arrête et demande quand :

- Le ticket est ambigu sur le résultat attendu
- Plusieurs solutions ont des trade-offs significatifs
- Une modification touche un chemin protégé
- Le scope dépasse ce qui était prévu (effet boule de neige)
- Un test existant échoue de façon inattendue
- Une dépendance externe doit être ajoutée ou mise à jour
- Une décision a un impact long terme sur l'architecture
- L'agent ne comprend pas une partie du code qu'il doit modifier

---

## Format d'escalade

```
🛑 Escalade
Raison      : [pourquoi je m'arrête]
État actuel : [ce qui est déjà fait]
Options     : [si pertinent, 2-3 pistes avec trade-offs]
Question    : [ce dont j'ai besoin pour continuer]
```

L'agent **ne devine pas**. Il s'arrête, expose, attend.
