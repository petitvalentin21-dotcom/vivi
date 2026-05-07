from fastapi.testclient import TestClient

from app.api.server import create_app
from app.config import Settings


def test_root_serves_web_interface() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "VIVI" in response.text
    assert 'id="message"' in response.text
    assert 'id="mode"' in response.text
    assert 'value="chat"' in response.text
    assert 'value="document"' in response.text
    assert 'id="send-btn"' in response.text
    assert 'id="chat-log"' in response.text
    assert 'id="sources-panel"' in response.text
    assert 'id="sources-list"' in response.text
    assert 'id="runtime-status"' in response.text
    assert 'id="refresh-runtime-btn"' in response.text
    assert "Utiliser VIVI" in response.text
    assert "Mode chat" in response.text
    assert "Mode document" in response.text
    assert "LM Studio" in response.text
    assert "Sources" in response.text
    assert 'id="help-list"' in response.text
    assert 'id="security-state"' in response.text
    assert 'id="auth-panel"' in response.text
    assert 'id="api-key-input"' in response.text
    assert 'type="password"' in response.text
    assert 'for="api-key-input"' in response.text
    assert 'id="api-key-help"' in response.text
    assert 'aria-describedby="api-key-help"' in response.text
    assert 'id="apply-api-key-btn"' in response.text
    assert 'id="clear-api-key-btn"' in response.text
    assert 'id="session-status"' in response.text
    assert 'id="reset-conversation-btn"' in response.text
    assert 'role="log"' in response.text
    assert 'role="alert"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'aria-label="Envoyer le message"' in response.text
    assert 'aria-label="Rafraîchir le statut runtime"' in response.text
    assert "Aucune source trouvée pour cette question." in response.text


def test_web_static_assets_are_accessible() -> None:
    client = TestClient(create_app(Settings()))

    css = client.get("/web/style.css")
    js = client.get("/web/app.js")

    assert css.status_code == 200
    assert js.status_code == 200


def test_web_js_has_explicit_source_numbering_label() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "Source ${sourceNumber}" in js.text


def test_web_js_handles_session_id_and_reset() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "let currentSessionId" in js.text
    assert "session_id: currentSessionId || null" in js.text
    assert "function resetConversation()" in js.text


def test_web_js_handles_local_api_key_without_localstorage() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "let localApiKey = \"\";" in js.text
    assert "function applyApiKey()" in js.text
    assert "function clearApiKey()" in js.text
    assert "headers.Authorization = `Bearer ${localApiKey}`;" in js.text
    assert "normalizeUiError" in js.text
    assert "Clé API locale invalide." in js.text
    assert "Authentification locale requise." in js.text
    assert "localStorage" not in js.text


def test_web_js_reset_conversation_does_not_clear_api_key() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "function resetConversation()" in js.text
    assert "setCurrentSessionId(\"\");" in js.text
    assert "Conversation réinitialisée localement." in js.text


def test_web_js_reset_conversation_function_does_not_call_clear_api_key() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    body = js.text.split("function resetConversation()", 1)[1].split("window.addEventListener", 1)[0]
    assert "clearApiKey(" not in body
    assert "localApiKey = """ not in body


def test_web_js_clear_api_key_is_explicit_action() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "function clearApiKey()" in js.text
    assert "localApiKey = \"\";" in js.text
    assert 'document.getElementById("clear-api-key-btn").addEventListener("click", clearApiKey);' in js.text


def test_web_js_maps_lmstudio_model_missing_error_to_readable_message() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "function toReadableBackendError(payload, status)" in js.text
    assert "lmstudio_model_missing" in js.text
    assert "VIVI_LMSTUDIO_MODEL" in js.text
    assert "Modèle LM Studio non configuré." in js.text
    assert "Configure VIVI_LMSTUDIO_MODEL avant d'envoyer une requête." in js.text


def test_web_js_maps_lmstudio_http_401_error_to_readable_message() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "lmstudio_http_error" in js.text
    assert "LM Studio returned HTTP 401" in js.text
    assert "LM Studio refuse la requête." in js.text
    assert "VIVI_LMSTUDIO_API_KEY" in js.text


def test_web_js_has_uniform_error_labels_for_mvp() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "Authentification locale requise." in js.text
    assert "Clé API locale invalide." in js.text
    assert "LM Studio est indisponible." in js.text
    assert "Modèle LM Studio non configuré." in js.text
    assert "LM Studio refuse la requête." in js.text
    assert "Impossible de joindre VIVI." in js.text
    assert "Erreur serveur VIVI." in js.text


def test_web_js_preserves_secondary_technical_details_without_secrets() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "request_id=" in js.text
    assert "Authorization: Bearer" not in js.text
    assert "sk-super-secret" not in js.text


def test_web_js_chat_uses_authorization_header_when_api_key_is_set() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "headers: authHeaders({ \"Content-Type\": \"application/json\" })," in js.text
    assert "headers.Authorization = `Bearer ${localApiKey}`;" in js.text
