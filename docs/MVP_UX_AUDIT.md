# VIVI MVP local — Audit UX réel

Ce document sert à observer l'usage réel de VIVI MVP local après validation technique. Il ne définit pas de nouvelle fonctionnalité produit et ne remplace pas la Release Candidate.

## 1. Objectif de l'audit UX

L'audit UX vise à passer de "techniquement validé" à "agréable à utiliser localement".

Objectifs :

- repérer les irritants concrets pendant une manipulation réelle ;
- distinguer les micro-corrections MVP des demandes post-MVP ;
- conserver une interface simple, sans refonte ni cockpit ;
- prioriser les corrections qui améliorent l'usage immédiat ;
- éviter d'élargir le produit au-delà du MVP local.

## 2. Protocole de test manuel 10 à 15 minutes

Préparer l'environnement :

1. Lancer LM Studio Local Server avec le modèle configuré.
2. Lancer le backend VIVI.
3. Ouvrir `http://127.0.0.1:8000/`.
4. Préparer une question simple et une question documentaire liée au vault.
5. Si `VIVI_API_KEY` est activée, préparer la clé locale.

Durée recommandée :

- 2 minutes : ouverture et lecture du runtime ;
- 3 minutes : chat simple ;
- 4 minutes : mode document et sources ;
- 2 minutes : reset conversation ;
- 2 minutes : auth ou erreur simulée si facile ;
- 2 minutes : remplir la grille d'observation.

Ne pas chercher à explorer tous les cas. L'objectif est d'observer les frictions visibles sur le parcours principal.

## 3. Parcours utilisateur à tester

Tester dans cet ordre :

1. Ouvrir l'IHM locale.
2. Lire le runtime status.
3. Lire l'encart d'aide.
4. Saisir un message simple en mode chat.
5. Lire la réponse.
6. Passer en mode document.
7. Poser une question documentaire liée au vault.
8. Lire les sources affichées.
9. Utiliser le reset conversation.
10. Tester le comportement avec auth API key si activée.
11. Tester le comportement avec LM Studio indisponible ou modèle absent si c'est facile à simuler.

Questions utiles :

- "Bonjour VIVI, réponds en une phrase."
- "Quels sont les objectifs du MVP ?"
- "Quelle est l'architecture backend prévue ?"

## 4. Grille d'observation simple

Copier une ligne par observation.

| Zone | Action testée | Résultat attendu | Résultat observé | Gêne ressentie | Priorité | Correction proposée | Décision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Runtime | Lire le statut | État compréhensible en moins de 10 secondes |  |  |  |  |  |
| Aide | Lire l'encart | Usage chat/document/sources clair |  |  |  |  |  |
| Chat | Envoyer un message simple | Réponse lisible et erreur claire si échec |  |  |  |  |  |
| Document | Poser une question vault | Réponse avec sources si contexte trouvé |  |  |  |  |  |
| Sources | Lire les sources | Sources visibles et compréhensibles |  |  |  |  |  |
| Reset | Réinitialiser la conversation | Conversation vidée et reprise claire |  |  |  |  |  |
| Auth | Utiliser la clé API | Auth compréhensible, sans fuite de secret |  |  |  |  |  |
| Erreur provider | LM Studio indisponible | Message utile avec action de récupération |  |  |  |  |  |

Priorités possibles :

- bloquant ;
- gênant ;
- confort ;
- post-MVP.

Décisions possibles :

- corriger maintenant ;
- documenter seulement ;
- garder pour post-MVP ;
- ignorer.

## 5. Irritants à relever

Relever uniquement les irritants observés, pas les idées abstraites.

Catégories utiles :

- texte ambigu ;
- bouton ou action difficile à trouver ;
- statut runtime incompréhensible ;
- mode chat/document peu clair ;
- sources difficiles à lire ;
- erreur insuffisamment actionnable ;
- reset peu rassurant ;
- auth API key confuse ;
- latence non expliquée ;
- contraste ou lisibilité insuffisants ;
- comportement mobile ou petit écran gênant ;
- différence entre documentation et comportement réel.

Pour chaque irritant, noter :

- ce qui a été fait ;
- ce qui était attendu ;
- ce qui s'est produit ;
- l'impact réel sur l'usage ;
- une correction minimale possible.

## 6. Critères pour accepter une micro-correction

Une correction peut être acceptée dans le MVP uniquement si toutes les conditions sont vraies :

- elle est visuelle ou textuelle ;
- elle est très localisée ;
- elle améliore clairement le parcours principal ;
- elle ne change pas le contrat API ;
- elle ne change pas le backend ;
- elle ne change pas l'architecture ;
- elle ne crée pas de nouveau mode produit ;
- elle ne crée pas de nouvelle page complexe ;
- elle ne nécessite pas de dépendance frontend ;
- elle reste compatible HTML/CSS/JS vanilla ;
- elle est couverte par les tests UI existants ou une mise à jour légère.

Exemples admissibles :

- reformuler un libellé ;
- clarifier un message d'erreur ;
- ajuster un espacement ;
- rendre une indication visuelle plus lisible ;
- améliorer une phrase de l'aide locale ;
- corriger une petite gêne d'accessibilité.

## 7. Critères pour refuser une demande comme post-MVP

Classer en post-MVP si la demande implique :

- agents spécialisés ;
- orchestrateur multi-agent ;
- runtime skills ;
- auto-amélioration ;
- appel Codex depuis VIVI ;
- provider registry ;
- priorité Ollama ;
- provider OpenAI ou Mammouth ;
- fallback externe ;
- vector DB ;
- embeddings obligatoires ;
- Open WebUI comme interface principale ;
- cockpit avancé ;
- app mobile ;
- VPN ;
- multi-utilisateur ;
- refonte UI ;
- nouvelle architecture ;
- nouveau mode produit ;
- nouvelle page complexe ;
- tableau de bord avancé ;
- écriture automatique dans Obsidian ;
- copie depuis `F:\VIVI_IA`.

Règle de décision : si la correction n'aide pas directement à ouvrir VIVI, parler à LM Studio, interroger Obsidian, voir les sources et obtenir une réponse fiable, elle reste hors MVP.

## 8. Modèle de retour utilisateur

À remplir après une session de 10 à 15 minutes.

```markdown
# Retour UX VIVI MVP local

Date :
Environnement :
Auth activée : oui/non
Modèle LM Studio :
Backend URL :
Navigateur :

## Parcours testé

- Ouverture IHM : OK / KO / remarque
- Runtime status : OK / KO / remarque
- Encart d'aide : OK / KO / remarque
- Chat simple : OK / KO / remarque
- Mode document : OK / KO / remarque
- Sources : OK / KO / remarque
- Reset conversation : OK / KO / remarque
- Auth API key : OK / KO / non testé
- Erreur LM Studio/modèle : OK / KO / non testé

## Irritants observés

| Zone | Action testée | Résultat attendu | Résultat observé | Gêne ressentie | Priorité | Correction proposée | Décision |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## Synthèse

Irritant principal :
Micro-correction proposée :
À refuser comme post-MVP :
Décision recommandée : corriger maintenant / documenter seulement / garder pour post-MVP / ignorer
```

## 9. Prochaines décisions possibles après l'audit

Après observation, choisir une seule décision principale :

1. Ne rien corriger : le MVP est suffisamment confortable pour la release locale.
2. Corriger une micro-friction : libellé, message, espacement, indication visuelle ou accessibilité légère.
3. Documenter seulement : l'irritant vient d'une attente ou d'un prérequis local.
4. Créer une tâche post-MVP : la demande élargit le produit.
5. Bloquer la release : l'irritant empêche le parcours principal ou masque un échec runtime.

Toute correction doit rester petite, testable et compatible avec la Release Candidate MVP locale.
