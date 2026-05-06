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
    assert "toReadableAuthError" in js.text
    assert "Clé API locale invalide." in js.text
    assert "Authentification locale activée : renseigne la clé API." in js.text
    assert "localStorage" not in js.text
