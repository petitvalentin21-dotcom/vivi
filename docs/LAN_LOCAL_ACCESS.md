# VIVI — Accès LAN local sécurisé

Ce guide explique comment lancer VIVI sur le PC hôte et y accéder depuis un autre appareil du même réseau local.

Objectif : rester local-first. Ce mode n'ajoute pas d'exposition Internet, pas de VPN, pas de cloud et pas de multi-utilisateur.

## 1. Principe

- `127.0.0.1` limite l'accès au PC qui lance VIVI.
- `0.0.0.0` fait écouter VIVI sur les interfaces réseau du PC hôte, donc le LAN peut y accéder.
- L'accès LAN doit être utilisé uniquement sur un réseau privé de confiance.
- Le port ne doit pas être ouvert sur Internet.
- Aucune redirection de port routeur ne doit être configurée.

## 2. Configuration recommandée

Créer `.env` depuis `.env.example` :

```bash
copy .env.example .env
```

Pour le mode LAN, définir une clé locale forte :

```env
VIVI_API_KEY=<cle_locale_forte>
```

Rappels importants :

- `VIVI_API_KEY` protège VIVI.
- `VIVI_LMSTUDIO_API_KEY` sert uniquement à LM Studio si LM Studio demande une clé provider.
- Ne jamais confondre `VIVI_API_KEY` et `VIVI_LMSTUDIO_API_KEY`.
- Ne jamais mettre de secret dans `.env.example`.
- Ne jamais commiter `.env`.

## 3. Lancement local-only

Mode recommandé pour le développement sur le PC hôte uniquement :

```bash
python -m uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

URL depuis le PC hôte :

```text
http://127.0.0.1:8000/
```

Commande équivalente avec la configuration `.env` depuis PowerShell :

```powershell
$env:VIVI_HOST="127.0.0.1"
$env:VIVI_PORT="8000"
python -m app.main
```

## 4. Lancement LAN

Mode à utiliser uniquement pour accéder à VIVI depuis un appareil du même réseau local :

```bash
python -m uvicorn app.api.server:app --host 0.0.0.0 --port 8000
```

Commande équivalente avec la configuration `.env` depuis PowerShell :

```powershell
$env:VIVI_HOST="0.0.0.0"
$env:VIVI_PORT="8000"
python -m app.main
```

Trouver l'adresse IP du PC hôte :

```bash
ipconfig
```

Chercher l'adresse IPv4 de l'interface Wi-Fi ou Ethernet utilisée, par exemple `192.168.1.25`.

URL depuis l'appareil LAN :

```text
http://<IP_DU_PC>:8000/
```

Exemple :

```text
http://192.168.1.25:8000/
```

## Accès depuis un iPhone

Procédure courte :

1. Préparer le PC hôte sur le réseau local privé.
2. Lancer LM Studio Local Server sur le PC hôte.
3. Charger le modèle local configuré pour VIVI.
4. Activer une clé API VIVI forte dans `.env` :

```env
VIVI_API_KEY=<cle_locale_forte>
```

5. Lancer VIVI en mode LAN depuis PowerShell :

```powershell
$env:VIVI_HOST="0.0.0.0"
$env:VIVI_PORT="8000"
python -m app.main
```

6. Trouver l'adresse IP locale du PC :

```bash
ipconfig
```

L'adresse à utiliser est généralement l'adresse IPv4 de la carte Wi-Fi du PC. Exemple :

```text
http://192.168.1.42:8000/
```

L'adresse exacte dépend du réseau local.

7. Connecter l'iPhone au même Wi-Fi que le PC.
8. Ouvrir Safari ou Brave sur l'iPhone.
9. Aller sur :

```text
http://<IP_DU_PC>:8000/
```

10. Renseigner la clé API VIVI si l'interface la demande.
11. Tester le chat, le mode document, les sources visibles et le reset conversation.

Points spécifiques iPhone :

- L'iPhone doit être sur le même Wi-Fi que le PC.
- Désactiver temporairement les données cellulaires peut aider au diagnostic.
- Éviter le relais privé iCloud ou un VPN si l'accès local échoue.
- Safari ou Brave peuvent être utilisés.
- L'URL doit commencer par `http://` et non `https://`.
- Si la page ne charge pas, vérifier le pare-feu Windows.
- Si la page charge mais le chat échoue, vérifier LM Studio, le modèle chargé et l'API key.
- Si l'auth bloque, vérifier que la clé saisie correspond à `VIVI_API_KEY`.

Sécurité iPhone :

- Utiliser uniquement un réseau privé de confiance.
- Ne pas ouvrir le port sur Internet.
- Ne pas faire de redirection de port routeur.
- Ne pas autoriser le pare-feu Windows sur réseau public.
- Activer `VIVI_API_KEY` en mode LAN.
- Ne jamais partager la clé API VIVI hors réseau de confiance.

Checklist iPhone :

- PC et iPhone sur le même Wi-Fi.
- LM Studio lancé.
- Modèle chargé.
- `VIVI_API_KEY` configurée.
- Backend lancé avec `VIVI_HOST=0.0.0.0`.
- IP du PC récupérée.
- Safari ou Brave ouvert sur iPhone.
- URL `http://<IP_DU_PC>:8000/` chargée.
- Clé API acceptée.
- Runtime visible.
- Chat OK.
- Mode document OK.
- Sources visibles OK.
- Reset OK.

## 5. Pare-feu Windows

Au premier lancement LAN, Windows peut afficher une alerte pare-feu.

Choisir :

- autoriser uniquement sur réseau privé ;
- ne pas autoriser sur réseau public.

Si l'appareil LAN ne voit pas VIVI, vérifier :

- le PC hôte et l'appareil client sont sur le même Wi-Fi ou réseau local ;
- l'adresse IP du PC hôte est correcte ;
- le port utilisé est bien `8000` ;
- le backend est lancé avec `--host 0.0.0.0` ou `VIVI_HOST=0.0.0.0` ;
- l'URL utilisée depuis l'appareil client est `http://<IP_DU_PC>:8000/` ;
- le pare-feu Windows autorise Python ou le port `8000` sur réseau privé.

## 6. Sécurité

Le mode LAN augmente la surface d'accès locale. À respecter :

- utiliser uniquement un réseau de confiance ;
- activer `VIVI_API_KEY` pour l'accès LAN ;
- ne pas exposer VIVI sans pare-feu ;
- ne pas ouvrir le port `8000` sur Internet ;
- ne pas configurer de redirection de port routeur ;
- ne pas utiliser de réseau public ;
- arrêter le backend quand l'accès LAN n'est plus nécessaire.

Ce mode ne remplace pas une sécurité avancée. VIVI reste mono-utilisateur et local-first.

## 7. Validation manuelle LAN

Checklist :

- PC hôte connecté au Wi-Fi ou réseau local privé.
- Appareil client connecté au même réseau.
- LM Studio Local Server lancé sur le PC hôte.
- Modèle local chargé dans LM Studio.
- `VIVI_API_KEY` configurée dans `.env`.
- Backend lancé en mode LAN.
- Ouverture depuis l'appareil client : `http://<IP_DU_PC>:8000/`.
- IHM chargée.
- Clé API renseignée si demandée.
- Runtime visible.
- Chat simple OK.
- Mode document OK.
- Sources visibles OK.
- Reset conversation OK.

## 8. Tests et smoke

Les tests automatisés ne dépendent pas d'un vrai réseau LAN :

```bash
pytest -q
```

Smoke depuis le PC hôte :

```bash
python scripts/smoke_backend.py --base-url http://127.0.0.1:8000 --api-key "<VIVI_API_KEY>"
```

Smoke depuis le PC hôte vers l'adresse LAN :

```bash
python scripts/smoke_backend.py --base-url http://<IP_DU_PC>:8000 --api-key "<VIVI_API_KEY>"
```

Le smoke LAN exige que le backend, LM Studio Local Server et le modèle soient lancés. Il ne doit pas être confondu avec `pytest -q`, qui utilise des tests automatisés sans vrai LAN.

## 9. Limites conservées

Cette procédure n'ajoute pas :

- exposition Internet ;
- VPN ;
- reverse proxy ;
- HTTPS public ;
- certificat ;
- cloud ;
- tunnel externe ;
- comptes ;
- rôles ;
- permissions avancées ;
- multi-utilisateur ;
- app mobile ;
- PWA ;
- changement RAG ;
- changement UI lourd.
