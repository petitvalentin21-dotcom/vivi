# Vivi — Phase 3 : Choix LLM et runtime

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique
**Casquette :** ResearchLead + CTO

---

## Décisions actées

| # | Décision |
|---|----------|
| LLM1 | Cœur LLM Vivi v1 = **Ministral 3 14B Instruct** (Mistral AI) en quantization Q4_K_M |
| LLM2 | Runtime = **Ollama** |
| LLM3 | Communication backend ↔ LLM via l'API REST OpenAI-compatible exposée par Ollama (port 11434) |
| LLM4 | Gemma 4 12B candidat à tester en parallèle si on veut faire de la comparaison |
| LLM5 | Llama 3.3 / Qwen3 14B = options de repli si Ministral 3 pose problème |

---

## Configuration matérielle de référence

- **PC fixe**, Windows
- **GPU :** NVIDIA RTX 3060 (12 GB VRAM)
- **RAM :** 32 GB
- **Disque :** 50-200 GB libre

Capacité confortable pour la gamme 7B-14B en quantization Q4-Q5. Ministral 3 14B Q4_K_M occupe environ 8-9 GB VRAM, laissant ~3 GB de marge pour le contexte conversationnel.

---

## Justification du choix Ministral 3 14B

### Pourquoi ce modèle

1. **Conçu pour notre cas d'usage exact** — Mistral AI cible explicitement "fast response conversational agents, low latency function calling, local inference for hobbyists and organizations handling sensitive data". C'est notre profil quasi mot pour mot.

2. **Tool calling natif et fiable** — entraîné dès le départ pour ça, avec un format que Ollama parse nativement en `tool_calls` structurés. Pas de prompting custom ni de parsing maison.

3. **Français natif** — Mistral est français, le modèle a été entraîné avec le français comme langue de premier rang. Important pour les conversations quotidiennes naturelles ("ce soir on mange quoi ?" qui doit sonner juste).

4. **Souveraineté européenne** — Mistral est français, Apache 2.0, aligné Phase 0 (engagement souverain).

5. **Optimisé latence** — la proactivité 18h30 et les conversations courtes du quotidien exigent des réponses rapides. Ministral 3 est explicitement conçu pour la latence faible.

6. **Rentre confortablement sur RTX 3060 12 GB** — Q4_K_M ≈ 8-9 GB VRAM, marge pour contexte (32K+ tokens).

### Pourquoi pas Gemma

Tu as utilisé Gemma 3n e4b en Vivi v1, et c'est un excellent modèle conversationnel. Trois raisons l'écartent pour le rôle de Cœur LLM Vivi v2 :

- **Tool calling non-natif** sur Gemma 3 — pas de tokens spéciaux dédiés, format de retour parfois incompatible avec le parsing Ollama. Plusieurs utilisateurs ont demandé que Google mette à jour le chat template pour gérer le function calling comme Qwen, Mistral et Llama le font déjà.
- **Forks fine-tunés requis** (ex. `orieg/gemma3-tools`) pour atteindre une fiabilité de tool calling équivalente. Dépendance maintenance externe.
- **Risque de plusieurs jours perdus** sur le parsing et le prompting custom, alors que le tool calling est le cœur de l'archi.

Gemma 4 (Apache 2.0, sorti avril 2026) est noté comme **candidat à tester** plus tard si la situation évolue ou si on veut benchmarker.

### Pourquoi pas Qwen3

Qwen3 14B est techniquement très bon (excellent tool calling, multilingue). Deux raisons de le mettre en repli plutôt qu'en principal :

- **Souveraineté** : Alibaba, chinois. Modèle open-weight Apache 2.0 donc utilisable sans contrainte, mais moins aligné Phase 0 que Mistral pour les choix par défaut.
- **Français** : très bon mais pas natif. Sur le quotidien parlé/écrit français, Mistral est un cran au-dessus.

Qwen3 14B reste **option de repli n°1** si Ministral 3 14B montre des limites inattendues.

---

## Justification du choix Ollama

### Pourquoi ce runtime

1. **API REST stable et OpenAI-compatible** — on développe le backend Vivi contre une API standard. Si on change de runtime ou de modèle plus tard, on ne réécrit pas le backend.

2. **Daemon always-on** — Ollama tourne en service en arrière-plan, sans cold-start. Quand Vivi backend appelle Ollama à 18h30, la réponse est immédiate (pas de chargement à la volée).

3. **Tool calling parsé nativement** — Ollama récupère les `tool_calls` dans la structure de réponse, prêts à être exécutés côté backend. Pas de parsing manuel de markdown ou de regex.

4. **Écosystème mûr** — 80 000+ étoiles GitHub, bibliothèques clientes Python/JS/Go, intégrations avec tous les frameworks d'agents (LangChain, LlamaIndex, AutoGen, etc.). Si on a besoin d'un truc, ça existe déjà.

5. **Gestion multi-modèles facile** — on peut avoir plusieurs modèles installés en parallèle (`ollama pull mistral`, `ollama pull gemma`, etc.) et basculer trivialement. Important pour la trajectoire d'évolution (routeur multi-modèles si dev plus tard).

6. **Commandes CLI lisibles** — `ollama list`, `ollama pull`, `ollama run` : tout est explicite. Maintenance simple.

### Pourquoi pas LM Studio (utilisé en v1)

- **GUI graphique inutile pour un backend serveur** — LM Studio est conçu pour découvrir et essayer, pas pour servir.
- **Pas d'avantage technique** — sous le capot, les deux utilisent llama.cpp ; les perfs sont identiques.
- **Workflow moins scriptable** — Ollama est conçu API-first, LM Studio est GUI-first.
- **Daemon Ollama est plus propre** pour un service H24 sur Windows (auto-start, redémarrage en cas de plantage).

Note v1 → v2 : la transition LM Studio → Ollama est triviale (les API sont équivalentes). Les apprentissages de Vivi v1 sur le prompting et l'usage LLM restent applicables.

### Pourquoi pas llama.cpp direct

- **Trop bas niveau** pour démarrer. On veut bâtir Vivi, pas optimiser l'inférence.
- **Maintenance manuelle** (compile, params, configs) qui n'apporte rien à notre cas.
- Ollama étant un wrapper autour de llama.cpp, on peut toujours descendre d'un niveau plus tard si nécessaire — sans rebâtir l'archi.

---

## Configuration cible Ministral 3 14B

| Paramètre | Valeur recommandée |
|-----------|--------------------|
| Modèle | `mistral:ministral-3-14b-instruct` (ou équivalent Ollama disponible) |
| Quantization | Q4_K_M (sweet spot perf/qualité) |
| Contexte | 32 768 tokens (large mais raisonnable) |
| Température | 0.7 par défaut, 0.3 pour les appels d'outils déterministes |
| Top-p | 0.95 |
| Repeat penalty | 1.1 |

Ces paramètres sont des points de départ, à ajuster après tests réels.

---

## Risques identifiés

| Risque | Probabilité | Mitigation |
|--------|-------------|-----------|
| Ministral 3 14B pas encore packagé proprement sur Ollama au moment du démarrage build | Moyenne | Repli temporaire sur Mistral Small 3 (24B) si possible matériellement, ou Qwen3 14B |
| Qualité de tool calling en français en dessous des attentes | Faible | Tests sur scenarios MVP avant build complet ; switch Qwen3 14B si besoin |
| Latence trop élevée sur RTX 3060 | Faible | Quantization plus agressive (Q3_K_M) ou modèle 8B (Mistral 7B / Qwen3 8B) |
| Conso énergie GPU 24/7 trop élevée | Moyenne | Décharger le modèle après période d'inactivité, recharger à la demande (≈2-3s) |

---

## Comment installer (résumé pour build)

```bash
# Installer Ollama sur Windows (depuis ollama.com)
# Lancer le daemon (auto-start après install)

# Pull du modèle
ollama pull mistral-small:24b
# OU au moment où Ministral 3 14B est disponible :
# ollama pull ministral:14b-instruct

# Test rapide
ollama run mistral-small "Bonjour, qu'est-ce que tu sais faire ?"

# Endpoint API
# http://localhost:11434/v1/chat/completions
```

**Note :** la disponibilité exacte de Ministral 3 14B sur le registre Ollama au moment du build est à vérifier. Si le modèle n'est pas encore référencé, il faudra l'importer depuis Hugging Face via un Modelfile Ollama, ou démarrer sur Mistral Small 3 (24B) en mode CPU offload, ou Qwen3 14B.

---

## Points ouverts qui découlent

- **Stack backend** : Python (FastAPI) / Go / Node ? Choix prochain.
- **Modèle de données** : SQLite vs Postgres.
- **Communication backend ↔ modules** : appels directs Python, bus de messages, ou HTTP interne ?
- **Interface client iPhone** : PWA, Tauri, Swift natif.
