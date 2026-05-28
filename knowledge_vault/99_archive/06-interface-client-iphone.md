# Vivi — Phase 3 : Interface client iPhone (PWA)

**Statut :** ✅ Validé le 25 mai 2026
**Version :** 1.0
**Phase :** 3 — Architecture technique
**Casquette :** CTO + Architect + ResearchLead

---

## Décisions actées

| # | Décision |
|---|----------|
| UI1 | Client iPhone = **PWA** (Progressive Web App), pas app native ni wrapper |
| UI2 | Framework = **SvelteKit** |
| UI3 | Style = **Tailwind CSS** |
| UI4 | Composants UI = **shadcn-svelte** ou minimal custom |
| UI5 | Service Worker = **Workbox** |
| UI6 | Push notifications = **Web Push API** standard (depuis FastAPI vers iOS via APNs) |
| UI7 | Hors ligne = **non requis** (le porteur a presque toujours du réseau) |
| UI8 | Tauri / Capacitor : **écarté** (build iOS requiert Mac, compte Apple 99$/an, sur-ingénierie pour MVP perso) |
| UI9 | Swift natif : **écarté** (pas de Mac, friction démesurée) |

---

## Justification du choix PWA

### Contexte technique

- **Pas de Mac à disposition** chez le porteur → Swift et Tauri/Capacitor mobile (qui ont besoin de Xcode pour signer une build iOS) sont éliminés.
- **Web Push fonctionne sur iOS 16.4+** depuis mars 2023, sous condition que la PWA soit installée à l'écran d'accueil.
- **Hors ligne non critique** → la principale faiblesse PWA (background sync absent, storage limité) n'impacte pas le porteur.

### Pourquoi PWA gagne

1. **Zéro friction de dev mobile** : pas de Mac, pas de Xcode, pas de compte développeur Apple à 99$/an.
2. **Stack familière** : HTML / CSS / JS, ce que le porteur connaît.
3. **Itération ultra-rapide** : tu déploies une nouvelle version, l'utilisateur recharge. Pas de cycle App Store.
4. **Cross-plateforme automatique** : PC, iPhone, futur Android : tous accèdent à la même interface.
5. **Push notifications fonctionnent** depuis iOS 16.4 quand la PWA est installée.
6. **Pas d'App Store** = aucune validation Apple, aucune règle contraignante, distribution libre via URL.

### Limitations acceptées explicitement

| Limitation | Impact réel | Mitigation |
|------------|------------|-----------|
| Friction onboarding "Ajouter à l'écran d'accueil" | Geste 1x lors de la première utilisation | Page d'onboarding explicite avec captures |
| Push iOS parfois fragile (subscription qui "disparaît") | À re-souscrire occasionnellement | Vérification périodique de l'état de souscription |
| Web Speech API moins bonne que Siri | Latence et qualité Speech-to-Text inférieures | Acceptable pour le MVP ; opt-in saisie texte toujours possible |
| Pas d'intégration Siri/Shortcuts | Pas d'invocation par "Dis Siri" | Acceptable ; on rouvre la PWA classiquement |
| Pas de widgets / Live Activities | Pas de badge dans l'écran de verrouillage | Acceptable pour MVP |

---

## Stack PWA détaillée

### Framework : SvelteKit

**Pourquoi SvelteKit** :
- Plus simple à apprendre que React/Next pour un usage perso.
- Build output très léger (Svelte compile à la build, pas de runtime lourd).
- Service Worker / PWA support natif.
- Type-safe avec TypeScript par défaut.
- Communauté active, doc excellente.

**Alternative si déjà familier d'un autre framework** : React (Next.js), Vue (Nuxt), Solid (SolidStart). Ne pas apprendre Svelte juste pour Vivi si on est productif ailleurs.

### Style : Tailwind CSS

**Pourquoi Tailwind** :
- Standard de facto en 2026.
- Productivité maximale, classes utilitaires, pas de CSS à écrire.
- Intégration parfaite avec SvelteKit (template `npx sv create` propose Tailwind d'emblée).

### Composants UI : shadcn-svelte

Port pour Svelte de la lib shadcn/ui (composants accessibles, modifiables, basés sur Radix). Recommandé pour démarrer sans tout coder. Si on préfère minimal, du HTML+Tailwind direct suffit pour les premiers écrans.

### Service Worker : Workbox

Lib Google standard pour la gestion du Service Worker (cache, push, fetch interception). Intégration SvelteKit documentée.

### Push : Web Push API native

Depuis FastAPI côté backend, on utilise les libs `pywebpush` (Python) pour envoyer une notification au navigateur abonné. Côté front, l'API standard `navigator.serviceWorker` + `PushManager`.

Notre relais APNs sera **Web Push standard via VAPID** : pas de service tiers nécessaire, pas de Pushover, pas de Ntfy pour ce besoin précis. Apple supporte Web Push directement.

### Reconnaissance vocale : Web Speech API

API standard navigateur (`SpeechRecognition`). Disponible sur Safari iOS depuis longtemps. Suffisant pour des phrases courtes type "ce soir on mange quoi" ou "plus de café dans les courses".

---

## Architecture client / serveur

```
┌─────────────────────────────┐
│       iPhone Safari          │
│  ┌─────────────────────────┐ │
│  │   PWA Vivi (SvelteKit)  │ │
│  │   ├─ UI conversation    │ │
│  │   ├─ UI courses         │ │
│  │   ├─ UI préférences     │ │
│  │   └─ Service Worker     │ │
│  └─────────────────────────┘ │
└──────────────┬───────────────┘
               │
               │ HTTPS via Tailscale
               │
┌──────────────▼───────────────┐
│       PC fixe (Topo A)        │
│  ┌─────────────────────────┐ │
│  │   FastAPI (backend)     │ │
│  │   ├─ Sert assets PWA    │ │
│  │   ├─ API /chat          │ │
│  │   ├─ Webhooks push      │ │
│  │   └─ Modules            │ │
│  └─────────────────────────┘ │
│  ┌─────────────────────────┐ │
│  │   Ollama (LLM)          │ │
│  └─────────────────────────┘ │
└───────────────────────────────┘
```

**Notes :**
- FastAPI sert **à la fois** les assets statiques PWA (HTML, JS, CSS générés par SvelteKit build) **et** l'API. Pas de serveur web séparé.
- L'iPhone se connecte au PC via le réseau Tailscale (cf. Phase 3 / 01 — Topologie). L'URL est par exemple `https://vivi-pc.tail-xxxx.ts.net`.
- HTTPS obligatoire pour PWA (push, service worker). Tailscale fournit des certificats TLS valides via `tailscale cert`.

---

## Onboarding utilisateur (parcours type)

Première utilisation, du point de vue porteur :

1. **Activation Tailscale** sur PC et iPhone (une fois).
2. **Ouvrir Safari iPhone**, taper l'URL Vivi (ex. `https://vivi-pc.tail-xxxx.ts.net`).
3. **Page d'accueil PWA Vivi**.
4. **Première interaction** : bouton "Configurer Vivi" → assistant guidé.
5. **À la fin**, message : "Pour recevoir les notifications de Vivi, ajoute cette app à ton écran d'accueil : appuie sur le bouton Partager puis 'Sur l'écran d'accueil'".
6. **Vivi est maintenant utilisable** depuis l'icône comme une app classique.

Ce parcours sera détaillé en Phase 4 (build).

---

## Structure du projet front

```
vivi/
├── frontend/
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── src/
│   │   ├── app.html
│   │   ├── app.css
│   │   ├── service-worker.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts          # Client API vers FastAPI
│   │   │   ├── push.ts         # Gestion Web Push
│   │   │   ├── voice.ts        # Web Speech API
│   │   │   └── components/     # Composants UI réutilisables
│   │   │
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       ├── +page.svelte    # Conversation principale
│   │       ├── courses/+page.svelte
│   │       ├── preferences/+page.svelte
│   │       └── onboarding/+page.svelte
│   │
│   └── static/
│       ├── manifest.json       # Manifeste PWA
│       ├── icons/              # Icônes app
│       └── favicon.svg
│
└── backend/                    # cf. doc 04
```

Le build SvelteKit (`npm run build`) génère un dossier `build/` que FastAPI sert comme assets statiques.

---

## Manifeste PWA (extrait)

`static/manifest.json` :
```json
{
  "name": "Vivi",
  "short_name": "Vivi",
  "description": "Mon assistant personnel",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

`display: standalone` = ouverture sans la barre d'adresse Safari = ressemble à une vraie app.

---

## Points encore ouverts (Bloc E suivant et derniers détails)

- **Format tool calling Ollama** : appel direct API REST, ou via wrapper Pydantic ?
- **Stratégie de prompts** : où vivent les prompts système, format, versioning.
- **Authentification** : Vivi est-il accessible sans login (puisque Tailscale fait office d'authentification réseau), ou veut-on un mot de passe en plus ?
- **Style visuel concret** : à voir Phase 4, pas une décision d'archi.
