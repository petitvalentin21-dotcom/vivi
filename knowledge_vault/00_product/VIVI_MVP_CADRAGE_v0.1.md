## 1. Statut du document

Ce document définit le cadrage produit du MVP de VIVI.

Il doit servir de référence avant toute reprise de développement, fork, nettoyage, refactorisation ou audit du projet existant.

Objectif principal :

- recadrer VIVI autour d’un produit clair ;
- éviter la dérive fonctionnelle ;
- définir le MVP strict ;
- distinguer le cœur produit des idées post-MVP ;
- guider l’audit du projet actuel ;
- préparer un fork propre.

Ce document prime sur l’état actuel du code lorsque le code et la vision produit divergent.

---

# 2. Vision produit

VIVI est une IA locale d’assistance personnelle.

Sa fonction première est simple :

> Je lui parle, elle me répond.

VIVI doit fonctionner principalement en local, sur un serveur personnel accessible depuis le réseau privé.

À terme, VIVI pourra devenir un orchestrateur d’agents spécialisés, capables d’aider sur différents domaines :

- développement ;
- architecture ;
- documentation ;
- nutrition ;
- finances ;
- maison ;
- organisation personnelle ;
- auto-amélioration du système.

Mais pour le MVP, VIVI doit d’abord prouver une base fiable :

- interface dédiée ;
- discussion locale ;
- modèle local via LM Studio ;
- interrogation d’une base Obsidian ;
- sources visibles ;
- statut runtime clair ;
- sécurité minimale.

---

# 3. Objectif MVP

Le MVP strict de VIVI doit permettre le parcours suivant :

> Depuis un appareil du réseau local, j’ouvre une interface web dédiée VIVI, je communique avec un modèle local servi par LM Studio, je pose une question sur la base Obsidian, VIVI récupère un contexte pertinent, affiche les sources utilisées, puis me répond clairement.

Le MVP ne cherche pas encore à être complet, intelligent sur tous les sujets ou autonome.

Il cherche à valider le socle produit :

- parler à VIVI ;
- recevoir une réponse locale ;
- interroger la connaissance Obsidian ;
- comprendre quelles sources ont été utilisées ;
- voir l’état du système ;
- éviter les crashs opaques ;
- garder une architecture extensible sans complexité excessive.

---

# 4. Utilisateur cible

Le MVP est destiné à un seul utilisateur : le propriétaire du serveur local.

VIVI n’est pas encore un produit multi-utilisateur.

Contraintes MVP :

- mono-utilisateur ;
- usage local ;
- réseau privé ;
- interface web simple ;
- aucune gestion avancée de comptes ;
- aucune exposition publique ;
- sécurité simple mais présente.

---

# 5. Parcours utilisateur cible

## 5.1 Parcours principal

1. L’utilisateur lance le serveur VIVI localement.
2. LM Studio est lancé avec un modèle local disponible.
3. L’utilisateur ouvre l’interface VIVI depuis son navigateur.
4. L’interface affiche l’état du système.
5. L’utilisateur saisit une question.
6. VIVI route la demande.
7. Si nécessaire, VIVI interroge le vault Obsidian.
8. VIVI envoie le prompt contextualisé au modèle local.
9. VIVI affiche la réponse.
10. VIVI affiche les sources Obsidian utilisées.

## 5.2 Exemple de validation

Question utilisateur :

- Où en est le projet VIVI ?
- Quelle est l’architecture prévue ?
- Quelles règles de gestion du vault sont définies ?
- Quel est le périmètre du MVP ?

Réponse attendue :

- réponse claire ;
- contexte issu d’Obsidian ;
- sources visibles ;
- absence d’appel externe ;
- absence d’erreur opaque ;
- état runtime cohérent.

---

# 6. Périmètre MVP strict

## 6.1 Inclus dans le MVP

Le MVP inclut uniquement les éléments suivants.

### Interface dédiée VIVI

- interface web simple ;
- design fonctionnel ;
- une page principale ;
- accès depuis navigateur ;
- affichage chat ;
- affichage modèle actif ;
- affichage mode actif ;
- affichage runtime status ;
- affichage sources utilisées ;
- affichage erreurs lisibles.

### Provider LM Studio

- LM Studio est le provider local prioritaire ;
- communication via API locale compatible OpenAI ;
- endpoint configurable ;
- modèle configurable ;
- healthcheck minimal ;
- chat completion fonctionnel.

### Chat local

- VIVI doit permettre une conversation simple ;
- l’utilisateur pose une question ;
- VIVI répond via un modèle local ;
- aucune dépendance cloud obligatoire.

### RAG Obsidian

- VIVI doit lire une base Obsidian ;
- VIVI doit récupérer des notes pertinentes ;
- VIVI doit utiliser ce contexte dans ses réponses ;
- le RAG MVP est simple, explicable et fiable.

### Sources visibles

- chaque réponse contextualisée doit afficher les sources Obsidian utilisées ;
- l’utilisateur doit pouvoir vérifier d’où vient la réponse ;
- les sources doivent aider à détecter les erreurs de contexte.

### Runtime status

L’interface doit afficher un statut simple :

- serveur VIVI disponible ou non ;
- provider LM Studio disponible ou non ;
- modèle actif ;
- vault détecté ou non ;
- RAG disponible ou non ;
- mémoire session active ou non ;
- erreur bloquante si présente.

### Mémoire simple

Le MVP inclut :

- mémoire de session courte ;
- mémoire projet via Obsidian ;
- préférences minimales visibles.

Le MVP exclut :

- mémoire agent ;
- mémoire opaque ;
- mémoire vectorielle obligatoire ;
- mémorisation automatique incontrôlée.

### Sécurité simple

Le MVP inclut une protection minimale :

- accès réseau local contrôlé ;
- clé ou mot de passe simple ;
- aucun appel externe par défaut ;
- logs sans secrets ;
- erreurs safe ;
- écriture Obsidian limitée aux zones autorisées.

### Orchestration minimale

Le MVP peut contenir une orchestration simple :

- Router ;
- Planner léger ;
- Retriever RAG ;
- Responder.

Cette orchestration doit rester simple et justifiée par le parcours MVP.

---

# 7. Hors périmètre MVP

Les éléments suivants ne font pas partie du MVP.

## 7.1 Agents spécialisés

Sont post-MVP :

- agent DEV ;
- agent PM ;
- agent ARCH ;
- agent QA ;
- agent nutrition ;
- agent finance ;
- agent maison ;
- agent auto-amélioration ;
- agent créateur de skills.

## 7.2 Auto-amélioration

Sont post-MVP :

- analyse autonome du backlog ;
- création automatique de skills ;
- création automatique d’agents ;
- modification automatique de la base ;
- refactorisation proposée et appliquée sans validation ;
- amélioration autonome du système.

Pour le MVP, VIVI peut préparer le terrain mais ne doit pas agir automatiquement.

## 7.3 Providers multiples avancés

Sont post-MVP :

- Ollama prioritaire ;
- registry provider complexe ;
- benchmark automatique des modèles ;
- routage intelligent entre modèles ;
- fallback automatique OpenAI ou Mammouth ;
- sélection automatique du meilleur modèle.

## 7.4 Interface cockpit avancée

Sont post-MVP :

- dashboard agents ;
- éditeur de workflows ;
- gestion avancée mémoire ;
- visualisation graphe ;
- cockpit multi-écrans ;
- admin panel complet ;
- gestion multi-utilisateur.

## 7.5 Accès distant avancé

Sont post-MVP :

- VPN ;
- app mobile dédiée ;
- accès hors domicile ;
- gestion utilisateurs ;
- permissions avancées.

## 7.6 Obsidian autonome

Sont exclus du MVP :

- écriture libre dans les notes sources ;
- modification automatique de décisions ;
- réécriture automatique de documentation humaine ;
- mélange entre documentation humaine et données runtime ;
- génération incontrôlée dans le vault.

---

# 8. Architecture cible MVP

## 8.1 Vue générale

Architecture cible :

- Interface Web dédiée ;
- API locale ;
- LLM Gateway minimal ;
- Provider LM Studio ;
- Knowledge Layer Obsidian ;
- Retriever RAG simple ;
- Session Memory ;
- Runtime Status ;
- Safe Errors.

Structure logique :

- User Interface
  - Chat
  - Mode selector minimal
  - Runtime status
  - Sources panel
  - Error panel

- API locale
  - health
  - runtime info
  - chat
  - sessions
  - knowledge search

- Orchestrateur minimal
  - Router
  - Planner léger
  - Retriever
  - Responder

- LLM Gateway
  - LM Studio provider
  - client OpenAI-compatible
  - contrat provider simple

- Knowledge Layer
  - Obsidian reader
  - metadata parser
  - lexical retriever
  - source ranking
  - generated index

- Memory Layer
  - session memory
  - runtime state
  - préférences minimales visibles

- Runtime
  - diagnostics simples
  - erreurs safe
  - logs contrôlés
  - smoke tests

## 8.2 Principe d’architecture

L’architecture doit permettre le futur sans implémenter prématurément le futur.

Règle :

> On code uniquement ce qui sert le MVP maintenant, mais sans bloquer Ollama, les agents ou les providers externes plus tard.

---

# 9. Interface MVP

## 9.1 Objectif

L’interface dédiée VIVI doit être simple, directe et fonctionnelle.

Elle ne doit pas être un cockpit avancé au MVP.

## 9.2 Contenu minimal

L’interface MVP contient :

- zone de conversation ;
- champ de saisie ;
- bouton d’envoi ;
- modèle actif ;
- provider actif ;
- mode actif ;
- statut du système ;
- sources utilisées ;
- erreurs lisibles.

## 9.3 Modes MVP

Modes autorisés au MVP :

- Chat simple ;
- Question documentaire ;
- Diagnostic simple.

Les modes avancés sont post-MVP.

## 9.4 Règle UI

> Une page principale suffit pour le MVP.

Pas de dashboard complexe tant que le chat local et le RAG Obsidian ne sont pas stables.

---

# 10. Provider LM Studio

## 10.1 Décision

LM Studio est le provider local prioritaire du MVP.

Raison :

- usage plus générique ;
- interface utilisateur pratique ;
- expérimentation facile avec plusieurs modèles ;
- serveur local compatible OpenAI ;
- bon choix pour valider un assistant local personnel.

## 10.2 Contrat MVP

Le provider LM Studio doit supporter :

- endpoint configurable ;
- modèle configurable ;
- vérification de disponibilité ;
- envoi d’une requête chat ;
- réception d’une réponse ;
- gestion d’erreur claire si LM Studio est indisponible.

## 10.3 Ce qui n’est pas MVP

Ne pas implémenter au MVP :

- registry provider complexe ;
- fallback multi-provider ;
- sélection automatique modèle ;
- benchmarking ;
- routage par type d’agent ;
- optimisation avancée des modèles.

## 10.4 Compatibilité future

Le code doit rester compatible avec une évolution vers :

- Ollama ;
- OpenAI ;
- Mammouth ;
- autre API OpenAI-compatible.

Mais cette compatibilité doit rester légère.

---

# 11. RAG Obsidian

## 11.1 Rôle d’Obsidian

Obsidian est le cerveau principal du projet.

Il sert à deux usages distincts :

- documentation humaine ;
- connaissance exploitable par VIVI.

## 11.2 Rôle dans le MVP

Au MVP, VIVI doit pouvoir :

- lire le vault ;
- indexer ou parcourir les notes autorisées ;
- récupérer un contexte pertinent ;
- injecter ce contexte dans la réponse ;
- afficher les sources utilisées.

## 11.3 Type de RAG MVP

Le RAG MVP doit rester simple :

- recherche lexicale ;
- métadonnées ;
- chemins de fichiers ;
- titres ;
- tags ;
- sections ;
- priorité documentaire si disponible.

Le vectoriel et les embeddings sont post-MVP ou shadow mode.

## 11.4 Sources visibles

Chaque réponse basée sur Obsidian doit afficher les sources utilisées.

Affichage minimal :

- chemin de la note ;
- titre si disponible ;
- éventuellement section utilisée.

Affichage post-MVP :

- score ;
- extrait ;
- type de note ;
- niveau de confiance ;
- lien cliquable vers Obsidian.

## 11.5 Règle de confiance

Si aucune source pertinente n’est trouvée, VIVI doit le dire clairement.

Exemple :

- Aucun contexte Obsidian pertinent n’a été trouvé.
- Réponse produite sans contexte documentaire.
- Le fallback externe est désactivé.

---

# 12. Organisation Obsidian

## 12.1 Principe

La documentation humaine et les données générées doivent rester séparées.

Règle centrale :

> Toute écriture IA va dans une zone generated/, runtime/ ou inbox/, jamais directement dans les notes sources.

## 12.2 Zones recommandées

Structure logique recommandée :

- docs_humaines/
  - documentation lisible par l’utilisateur ;
  - source humaine ;
  - lecture seule pour VIVI au MVP.

- architecture/
  - architecture validée ;
  - décisions techniques ;
  - lecture seule pour VIVI au MVP.

- decisions/
  - décisions projet ;
  - source de vérité ;
  - lecture seule pour VIVI au MVP.

- backlog/
  - idées, tâches, améliorations ;
  - lecture au MVP ;
  - écriture seulement si explicitement contrôlée.

- generated/
  - contenus générés par IA ;
  - propositions ;
  - résumés ;
  - brouillons ;
  - non source de vérité tant que non validé.

- runtime/
  - index ;
  - logs ;
  - états générés ;
  - mémoire runtime ;
  - données techniques.

- inbox/
  - propositions à valider ;
  - suggestions d’amélioration ;
  - brouillons à intégrer manuellement.

## 12.3 Règles d’écriture

VIVI peut écrire au MVP uniquement dans :

- generated/ ;
- runtime/ ;
- inbox/ ;
- data/runtime/ si utilisé hors vault.

VIVI ne peut pas modifier automatiquement :

- documentation source ;
- décisions ;
- architecture validée ;
- README ;
- fichiers code ;
- backlog validé.

---

# 13. Mémoire

## 13.1 Décision MVP

La mémoire MVP doit être :

- simple ;
- explicite ;
- inspectable ;
- limitée ;
- supprimable ;
- séparée de la documentation source.

## 13.2 Types de mémoire MVP

### Session memory

Contient :

- historique récent ;
- contexte court ;
- mode actif ;
- provider actif ;
- modèle actif.

Statut : MVP.

### Project memory

Contient :

- cadrage ;
- décisions ;
- architecture ;
- documentation ;
- backlog validé.

Support : Obsidian.

Statut : MVP.

### User preferences

Contient uniquement les préférences minimales nécessaires :

- local-first ;
- supervision obligatoire ;
- provider préféré ;
- règles de sécurité ;
- préférences d’affichage.

Statut : MVP minimal.

## 13.3 Types de mémoire post-MVP

Sont post-MVP :

- mémoire par agent ;
- mémoire vectorielle ;
- mémoire long terme autonome ;
- mémoire auto-modifiée ;
- mémoire comportementale avancée.

---

# 14. Orchestration et agents

## 14.1 Décision MVP

Les agents spécialisés ne sont pas MVP.

Le MVP peut contenir une orchestration minimale :

- Router ;
- Planner léger ;
- Retriever RAG ;
- Responder.

## 14.2 Rôle du Router

Le Router décide du type de demande :

- chat simple ;
- question documentaire ;
- diagnostic ;
- demande non supportée.

## 14.3 Rôle du Planner léger

Le Planner prépare une stratégie courte :

- répondre directement ;
- chercher dans Obsidian ;
- vérifier le runtime ;
- signaler un manque d’information.

Le Planner ne doit pas lancer de workflow long au MVP.

## 14.4 Rôle du Retriever

Le Retriever récupère le contexte Obsidian pertinent.

Il doit être :

- déterministe autant que possible ;
- explicable ;
- limité ;
- traçable via sources.

## 14.5 Rôle du Responder

Le Responder produit la réponse finale avec le modèle local.

Il doit :

- utiliser le contexte fourni ;
- ne pas inventer de sources ;
- signaler les limites ;
- rester clair.

## 14.6 Agents post-MVP

Sont prévus plus tard :

- DEV ;
- PM ;
- ARCH ;
- QA ;
- Nutrition ;
- Finance ;
- Maison ;
- Auto-amélioration ;
- Créateur de skills.

Aucun de ces agents ne doit être implémenté dans le MVP strict.

---

# 15. Sécurité MVP

## 15.1 Principes

Même en local, VIVI doit être protégé.

Principes :

- local-first ;
- réseau privé uniquement ;
- aucun appel externe par défaut ;
- aucune fuite de secret ;
- erreurs safe ;
- actions critiques supervisées ;
- écriture limitée.

## 15.2 Protection simple

Le MVP doit prévoir une protection simple :

- mot de passe local ;
- ou clé API locale ;
- ou token simple configuré.

La solution exacte peut être choisie pendant l’implémentation, mais l’absence totale de protection n’est pas souhaitée.

## 15.3 Appels externes

Par défaut :

- OpenAI désactivé ;
- Mammouth désactivé ;
- aucun fallback externe automatique.

Un appel externe futur devra être :

- explicitement configuré ;
- visible dans l’interface ;
- confirmé ou supervisé ;
- tracé dans les logs ;
- jamais implicite.

## 15.4 Logs

Les logs ne doivent pas contenir :

- secrets ;
- clés API ;
- tokens ;
- données sensibles inutiles.

## 15.5 Erreurs

Les erreurs doivent être lisibles.

Exemples :

- LM Studio indisponible ;
- modèle absent ;
- vault introuvable ;
- aucune source pertinente ;
- accès refusé ;
- provider externe désactivé ;
- erreur interne safe.

---

# 16. Fork et nettoyage

## 16.1 Décision

Le projet actuel sera forké puis nettoyé.

Le projet actuel est considéré comme un laboratoire.

Le fork devient le produit recentré.

## 16.2 Méthode

Avant toute modification, auditer le projet existant selon le cadrage MVP.

Chaque composant doit être classé en 5 catégories :

- KEEP_MVP ;
- KEEP_POST_MVP ;
- ARCHIVE ;
- DELETE ;
- REWRITE.

## 16.3 Définitions

### KEEP_MVP

Élément nécessaire au MVP strict.

Critères :

- sert directement interface + LM Studio + chat + RAG + sources + runtime status ;
- fonctionne ou peut être conservé sans complexité excessive ;
- respecte le cadrage.

### KEEP_POST_MVP

Élément utile plus tard, mais non nécessaire au MVP.

Exemples :

- agents spécialisés ;
- auto-amélioration ;
- providers secondaires ;
- workflows avancés ;
- vectoriel avancé.

### ARCHIVE

Élément historique utile mais hors produit actuel.

Critères :

- peut aider à comprendre l’ancien projet ;
- ne doit pas rester dans le chemin actif ;
- peut être conservé dans une zone archive.

### DELETE

Élément inutile, obsolète, redondant ou dangereux.

Critères :

- ne sert pas le MVP ;
- ne sert pas clairement le post-MVP ;
- complexifie inutilement ;
- crée de la confusion ;
- duplique une autre source.

### REWRITE

Élément dont l’idée est utile mais dont l’implémentation doit être refaite.

Critères :

- trop complexe ;
- mal isolé ;
- trop couplé ;
- difficile à tester ;
- ne respecte pas le nouveau cadrage.

---

# 17. Règles de développement

## 17.1 Principes

Le développement doit rester contrôlé.

Règles :

- une tâche = une intention claire ;
- une branche = une FEAT courte ;
- une PR = un changement validable ;
- pas de refonte opportuniste ;
- pas de nouvelle abstraction sans usage MVP immédiat ;
- pas de feature sans critère d’acceptation ;
- pas de modification automatique des notes sources ;
- pas de complexité post-MVP dans le MVP.

## 17.2 Codex

Codex peut être utilisé, mais sous règles strictes.

Règles Codex :

- respecter ce cadrage ;
- ne pas modifier le code pendant l’audit initial ;
- produire les rapports dans tmp/ ;
- indiquer les fichiers analysés ;
- indiquer les fichiers modifiés lorsque modification autorisée ;
- indiquer les tests exécutés ;
- indiquer les risques ;
- indiquer les suppressions proposées ;
- ne pas créer d’abstraction future non demandée.

## 17.3 Rapports Codex

Chaque tâche Codex doit produire un rapport court dans tmp/.

Format attendu :

- résumé ;
- fichiers modifiés ;
- comportement ajouté ;
- comportement supprimé ;
- tests lancés ;
- risques ;
- prochaines étapes ;
- conformité au cadrage MVP.

---

# 18. Tests et validation

## 18.1 Objectif

Le MVP doit être validé par un parcours utilisateur réel.

## 18.2 Tests MVP nécessaires

Tests attendus :

- serveur démarre ;
- interface accessible ;
- LM Studio détecté ;
- modèle actif affiché ;
- question simple traitée ;
- réponse reçue ;
- vault Obsidian détecté ;
- question documentaire traitée ;
- sources affichées ;
- erreur LM Studio indisponible lisible ;
- erreur vault absent lisible ;
- protection simple active ;
- aucun appel externe par défaut.

## 18.3 Smoke test MVP

Un smoke test minimal doit vérifier :

- health ;
- runtime info ;
- provider status ;
- chat simple ;
- RAG simple ;
- sources ;
- erreur safe.

## 18.4 Critère de validation

Le MVP est validé si :

> Depuis un navigateur sur le réseau local, l’utilisateur ouvre VIVI, voit que LM Studio et le vault sont disponibles, pose une question, reçoit une réponse locale contextualisée, et peut voir les sources Obsidian utilisées.

---

# 19. Roadmap post-MVP

## 19.1 Phase post-MVP 1 — Stabilisation

Objectifs :

- améliorer l’interface ;
- renforcer les erreurs ;
- améliorer les sources ;
- ajouter historique conversation ;
- améliorer le RAG lexical ;
- ajouter tests réseau local.

## 19.2 Phase post-MVP 2 — Providers

Objectifs :

- ajouter Ollama ;
- préparer OpenAI ;
- préparer Mammouth ;
- comparer providers ;
- permettre sélection contrôlée du provider.

## 19.3 Phase post-MVP 3 — Agents

Objectifs :

- agent DEV ;
- agent PM ;
- agent ARCH ;
- agent QA ;
- workflows supervisés ;
- production de fichiers sous validation.

## 19.4 Phase post-MVP 4 — Auto-amélioration

Objectifs :

- lire backlog ;
- proposer améliorations ;
- créer brouillons dans inbox/ ;
- suggérer nouveaux skills ;
- suggérer nouveaux agents ;
- ne jamais appliquer sans validation.

## 19.5 Phase post-MVP 5 — Accès avancé

Objectifs :

- VPN ;
- app mobile ou PWA ;
- sécurité avancée ;
- permissions ;
- cockpit avancé.

---

# 20. Principes anti-dérive

## 20.1 Question de contrôle

Avant chaque nouvelle fonctionnalité, poser la question :

> Est-ce nécessaire pour ouvrir VIVI, parler à LM Studio, interroger Obsidian, voir les sources et obtenir une réponse fiable ?

Si non :

- post-MVP ;
- archive ;
- backlog ;
- ou refus.

## 20.2 Interdictions MVP

Ne pas faire au MVP :

- agents spécialisés ;
- auto-amélioration active ;
- provider registry complexe ;
- fallback externe automatique ;
- cockpit avancé ;
- vector DB obligatoire ;
- écriture libre dans Obsidian ;
- app mobile ;
- multi-utilisateur ;
- appels Codex depuis VIVI.

## 20.3 Priorité

Priorité absolue :

1. assistant local de discussion ;
2. LM Studio ;
3. interface dédiée ;
4. Obsidian RAG ;
5. sources visibles ;
6. runtime status ;
7. sécurité simple.

Tout le reste attend.

---

# 21. Résumé exécutable

VIVI MVP v0.1 :

- assistant local de discussion ;
- interface web dédiée simple ;
- provider LM Studio ;
- chat local ;
- RAG Obsidian ;
- sources visibles ;
- runtime status ;
- mémoire session simple ;
- sécurité simple ;
- aucune auto-amélioration ;
- aucun agent spécialisé ;
- aucun fallback externe automatique ;
- nettoyage du fork guidé par KEEP_MVP / KEEP_POST_MVP / ARCHIVE / DELETE / REWRITE.

Ce document doit être utilisé comme base avant tout audit ou développement.