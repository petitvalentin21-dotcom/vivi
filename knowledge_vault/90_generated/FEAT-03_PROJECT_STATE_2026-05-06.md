# FEAT-03 — État projet (généré)

## Runtime

- `POST /chat` MVP implémenté et branché sur LM Studio.
- Contrat réponse stable: `answer`, `session_id`, `provider`, `mode`, `sources`, `runtime`, `error`.
- FEAT-03 garde `sources=[]`, `rag_used=false`, `external_call_used=false`.

## Sessions

- Store session minimal persistant JSON.
- Création automatique si `session_id` absent.
- `session_not_found` si `session_id` inconnu.

## Sécurité

- `POST /chat` protégé par API key si `VIVI_API_KEY` est défini.
- Erreurs safe conservées, sans fuite de secrets.

## Tests

- `pytest -q` : 32 passed (inclut tests endpoint chat mockés, sans LM Studio réel).
