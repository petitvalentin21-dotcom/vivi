# Vivi — Phase 3 : Tool calling, prompts, authentification

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique
**Casquette :** CTO + Linguiste + CISO

---

## Décisions actées

### Tool calling

| # | Décision |
|---|----------|
| TC1 | Format = OpenAI function calling (standard Ollama natif) |
| TC2 | Déclaration des outils via Pydantic models → JSON Schema auto-généré |
| TC3 | Dispatcher central dans `core/tool_registry.py` |
| TC4 | Logging systématique : nom, args sans payload sensible, succès/échec, durée |
| TC5 | Limite par tour utilisateur : 5 appels d'outils max |
| TC6 | Pattern read/write : outils d'écriture audités, actions destructives demandent confirmation |

### Prompts

| # | Décision |
|---|----------|
| PR1 | Prompts versionés dans Git sous `backend/core/prompts/` |
| PR2 | Trois niveaux : système / contextuel / outils |
| PR3 | Format Markdown ou texte brut |
| PR4 | Tests de non-régression par scénarios |
| PR5 | Pas de prompts en BDD au MVP |

### Authentification

| # | Décision |
|---|----------|
| AU1 | MVP : pas d'auth applicative, Tailscale fait office d'auth réseau |
| AU2 | Middleware FastAPI `AuthDependency` existe dès le MVP mais permissif |
| AU3 | Activation d'auth Bearer le jour où on partage à un proche (post-MVP) |

---

## 1. Tool calling — détail

### Le standard 2026

Tous les LLMs récents convergent sur le **format OpenAI function calling**, exposé par Ollama nativement. Mistral 3 supporte ce format.

### Flux complet (en 4 étapes)

**Étape 1 — Déclaration des outils.** À chaque tour, le backend envoie au LLM la liste des outils disponibles via JSON Schema.

**Étape 2 — Le LLM décide.** Il répond soit du texte, soit une demande d'appel structurée :
```json
{
  "tool_calls": [{
    "id": "call_abc123",
    "function": {
      "name": "get_propositions_repas_ce_soir",
      "arguments": "{\"max_options\": 3}"
    }
  }]
}
```

**Étape 3 — Le backend exécute.** Le dispatcher identifie la fonction, valide les arguments via Pydantic, exécute, renvoie le résultat structuré au LLM dans le tour suivant.

**Étape 4 — Le LLM formule.** Reçoit le résultat, le présente naturellement à l'utilisateur.

### Pattern de déclaration en Python

```python
from pydantic import BaseModel, Field
from uuid import UUID

class MarquerPortionConsommeeArgs(BaseModel):
    batch_id: UUID = Field(description="Identifiant UUID du batch")

class MarquerPortionConsommeeResult(BaseModel):
    success: bool
    portions_restantes: int
    message: str

@tool(
    name="marquer_portion_consommee",
    description="Décrémente d'une portion le stock d'un batch cuisiné",
    write=True,
)
def marquer_portion_consommee(
    args: MarquerPortionConsommeeArgs,
) -> MarquerPortionConsommeeResult:
    # logique métier
    ...
```

Le décorateur `@tool` :
- Enregistre la fonction dans le `tool_registry`.
- Génère le JSON Schema pour Ollama depuis le modèle Pydantic.
- Active le logging et l'audit.
- Marque le caractère "write" pour la couche de sécurité.

### Garde-fous spécifiques

- **5 appels max par tour** utilisateur. Au-delà, retour forcé à l'utilisateur. Évite les boucles infinies du LLM.
- **Confirmation pour les actions destructives** : `supprimer_recette`, `effacer_historique` exigent un appel explicite à l'utilisateur (via un message intermédiaire) avant exécution.
- **Logging exhaustif sans données sensibles** : on log "marquer_portion_consommee appelé avec batch_id=xxx-yyy" mais pas le contenu de la recette ou de la conversation.

---

## 2. Prompts — détail

### Structure des fichiers

```
backend/core/prompts/
├── system.md           # Identité et règles intangibles
├── context/
│   ├── matin.md       # Contexte injecté le matin
│   ├── soir.md        # Contexte injecté le soir (dîner)
│   └── weekend.md     # Mode planif batch cooking
└── tools_meta.md      # Méta-instructions sur l'usage des outils
```

### Prompt système v1 (esquisse)

```markdown
# Identité

Tu es Vivi, l'assistant personnel de [nom du porteur].
Tu vis sur son ordinateur. Tu connais sa vie et tu l'aides à la gérer.

# Ton

- Tutoiement, par défaut.
- Phrases courtes. Une question, une réponse, une action.
- Naturel, pas robotique. Pas de "je suis un assistant IA".
- Tu peux être affectueux mais sans en faire trop.

# Règles intangibles

1. Tu n'inventes jamais de chiffres, dates, quantités. Si tu ne sais pas, tu appelles un outil ou tu demandes.
2. Pour toute information qui ne sort pas de la conversation en cours, tu appelles un outil. Tu n'extrapoles pas.
3. Avant une action destructive (supprimer, effacer), tu demandes confirmation explicite.
4. Tu ne mentionnes jamais d'outils ou de fonctions à [nom du porteur]. Il ne voit que le résultat naturel.
5. Si tu ne sais pas faire quelque chose, tu le dis franchement.

# Mémoire et personnalisation

Tu as accès à des informations sur ses préférences (aliments aimés/détestés, recettes valeurs sûres). Utilise-les implicitement, ne les récite pas.

# Outils

Tu disposes d'outils pour interagir avec son stock, son catalogue de recettes, sa liste de courses, ses préférences. Utilise-les chaque fois qu'une information ou une action concerne ces domaines.
```

### Évolution et tests

- **Chaque modification = un commit Git** avec message descriptif.
- **Suite de scénarios** dans `tests/scenarios/` :
  - `dîner_classique.txt` : "ce soir on mange quoi ?" → attente : appel `get_propositions_repas_ce_soir`
  - `oubli_courses.txt` : "plus de café" → attente : appel `ajouter_article` avec article="café"
  - `destructif.txt` : "efface tout mon historique" → attente : demande de confirmation, pas d'exécution immédiate
- Ces scénarios tournent en CI, alertent si régression.

### Pourquoi pas en BDD

- Le prompt est du **comportement**, donc du code. Lié au code.
- Versioning Git natif.
- Pas de risque de désync entre environnements.
- Simple à débugger : un fichier à ouvrir.

Si plus tard on veut un mode "personnalité réglable par l'utilisateur final" (couleur de Vivi customisée), on ajoutera une couche d'overrides en BDD. Pas maintenant.

---

## 3. Authentification — détail

### Modèle

Tailscale fait office d'auth réseau : seuls les appareils du tailnet peuvent atteindre l'URL Vivi. Pour un usage solo, c'est suffisant.

### Couche d'auth pré-équipée

Pour ne pas se peindre dans un coin :

```python
# backend/api/dependencies.py

from fastapi import Depends, HTTPException, Header

async def get_current_user(
    authorization: str | None = Header(None),
) -> str:
    """
    MVP : permissif. Retourne "porteur" pour tout appel.
    Post-MVP : valide le Bearer token.
    """
    if settings.AUTH_ENABLED:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "Auth required")
        token = authorization[7:]
        user = validate_token(token)  # à implémenter
        if not user:
            raise HTTPException(401, "Invalid token")
        return user
    return "porteur"

# backend/api/chat.py

@router.post("/chat")
async def chat(
    message: ChatMessage,
    user: str = Depends(get_current_user),
):
    ...
```

Au MVP : `settings.AUTH_ENABLED = False`, tout passe.
Post-MVP : flip le flag, génère des tokens, distribue. Aucune refonte de code.

---

## Phase 3 — close

Avec ce document, **Phase 3 (Architecture technique) est terminée**. Six documents la composent :

| Doc | Sujet |
|-----|-------|
| 01 | Topologie physique |
| 02 | Architecture logicielle |
| 03 | LLM + runtime |
| 04 | Stack backend |
| 05 | Persistance |
| 06 | Interface client iPhone |
| 07 (ce doc) | Tool calling, prompts, authentification |

Toutes les décisions structurantes sont actées. La Phase 4 peut commencer.
