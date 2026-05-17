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
    assert 'class="panel conversation-panel"' in response.text
    assert 'class="panel help-panel"' in response.text
    assert 'class="panel runtime-panel"' in response.text
    assert 'class="panel memory-panel"' in response.text
    assert '<summary id="memory-title">Mémoire VIVI</summary>' in response.text
    assert '<summary id="help-title">Utiliser VIVI</summary>' in response.text
    assert '<summary id="runtime-title">État local</summary>' in response.text
    assert "<details" in response.text
    assert "<details open" not in response.text
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
    assert 'id="memory-info-btn"' in response.text
    assert 'id="memory-improvement-btn"' in response.text
    assert 'id="inbox-capture-form"' in response.text
    assert 'id="memory-info-fields"' in response.text
    assert 'id="memory-improvement-fields"' in response.text
    assert 'id="inbox-capture-status"' in response.text
    assert 'id="inbox-capture-error"' in response.text
    assert 'id="copy-inbox-path-btn"' in response.text
    assert "Mémoriser une information" in response.text
    assert "Proposer une amélioration" in response.text
    assert "Créer une note candidate dans Obsidian Inbox" in response.text
    assert 'role="log"' in response.text
    assert 'role="alert"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'aria-label="Envoyer le message"' in response.text
    assert 'aria-label="Rafraîchir le statut runtime"' in response.text
    assert "Aucune source trouvée pour cette question." in response.text


def test_web_layout_prioritizes_conversation_before_help_and_runtime() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/")
    html = response.text

    assert html.index('class="panel conversation-panel"') < html.index('class="panel help-panel"')
    assert html.index('class="panel conversation-panel"') < html.index('class="panel runtime-panel"')
    assert html.index('class="panel conversation-panel"') < html.index('class="panel memory-panel"')


def test_web_css_gives_conversation_more_room() -> None:
    client = TestClient(create_app(Settings()))
    css = client.get("/web/style.css")
    assert ".conversation-panel" in css.text
    assert "min-height: 360px;" in css.text
    assert "max-height: min(58vh, 620px);" in css.text
    assert ".help-panel summary" in css.text
    assert ".runtime-panel summary" in css.text
    assert ".memory-panel summary" in css.text
    assert ".inbox-capture-form" in css.text


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


def test_web_js_renders_readable_source_cards() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert 'document.createElement("article")' in js.text
    assert '"source-item"' in js.text
    assert 'item.setAttribute("aria-label"' in js.text
    assert 'title.className = "source-title"' in js.text
    assert 'pathEl.className = "source-path"' in js.text
    assert 'scoreLabel.className = "source-score"' in js.text
    assert 'excerptEl.className = "source-excerpt"' in js.text
    assert 'summary.textContent = "Afficher l\'extrait utilisé";' in js.text
    assert "src.chunk_text" in js.text
    assert "src.excerpt" in js.text
    assert "details.open = true;" not in js.text


def test_web_js_source_rendering_supports_multiple_sources() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "sources.forEach((src, index) => {" in js.text
    assert "const sourceNumber = index + 1;" in js.text
    assert "list.appendChild(item);" in js.text


def test_web_js_renders_assistant_markdown_without_raw_inner_html() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "function renderMarkdownLite(container, content)" in js.text
    assert 'if (role === "VIVI")' in js.text
    assert "renderMarkdownLite(body, content);" in js.text
    assert "body.textContent = content;" in js.text
    assert "block.innerHTML" not in js.text


def test_web_js_supports_simple_markdown_blocks() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "/^(#{1,3})\\s+(.+)$/" in js.text
    assert "appendMarkdownBlock(container, `h${heading[1].length + 2}`, heading[2]);" in js.text
    assert "/^[-*]\\s+(.+)$/" in js.text
    assert "/^\\d+\\.\\s+(.+)$/" in js.text
    assert 'document.createElement("hr")' in js.text


def test_web_js_supports_bold_markdown_with_text_nodes() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "function appendInlineMarkdown(parent, text)" in js.text
    assert "value.split" in js.text
    assert 'document.createElement("strong")' in js.text
    assert "strong.textContent = part.slice(2, -2);" in js.text
    assert "document.createTextNode(part)" in js.text


def test_web_js_falls_back_to_plain_text_if_markdown_rendering_fails() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    assert "} catch (err) {" in js.text
    assert 'container.textContent = String(content || "");' in js.text


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


def test_web_memory_panel_is_secondary_and_closed_by_default() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/")
    html = response.text

    assert '<details class="panel memory-panel" aria-labelledby="memory-title">' in html
    assert '<details class="panel memory-panel" open' not in html
    assert html.index('class="panel conversation-panel"') < html.index('class="panel memory-panel"')


def test_web_js_opens_memory_and_improvement_forms() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")

    assert "function openInboxCapture(type)" in js.text
    assert 'openInboxCapture("info")' in js.text
    assert 'openInboxCapture("improvement")' in js.text
    assert 'memoryFields.classList.toggle("hidden", type !== "info");' in js.text
    assert 'improvementFields.classList.toggle("hidden", type !== "improvement");' in js.text
    assert "lastUserMessage || currentDraft" in js.text


def test_web_js_builds_memory_payload_for_clarification_note() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")

    assert "function buildMemoryInfoBody(title, information, context)" in js.text
    assert 'note_type: "clarification_note"' in js.text
    assert 'status: "draft"' in js.text
    assert 'prompt_summary: "action explicite depuis Mémoire VIVI"' in js.text
    assert "## Information à mémoriser" in js.text
    assert "## Contexte" in js.text
    assert "- Indexation : désactivée" in js.text


def test_web_js_builds_improvement_payload_for_backlog_proposal() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")

    assert "function buildImprovementBody(title, problem, proposal, category, priority)" in js.text
    assert 'note_type: "backlog_proposal"' in js.text
    assert 'prompt_summary: "proposition d\'amélioration depuis Mémoire VIVI"' in js.text
    assert "## Problème observé" in js.text
    assert "## Amélioration proposée" in js.text
    assert "## Catégorie" in js.text
    assert "## Priorité proposée" in js.text


def test_web_js_inbox_capture_uses_existing_api_key_and_endpoint() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")

    assert 'fetch("/obsidian/inbox", {' in js.text
    assert 'headers: authHeaders({ "Content-Type": "application/json" }),' in js.text
    assert "body: JSON.stringify(built.payload)," in js.text
    assert "LMStudioClient" not in js.text


def test_web_js_inbox_capture_shows_success_and_copy_path() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")

    assert "function showInboxCaptureSuccess(relativePath)" in js.text
    assert "Note créée dans ${lastInboxPath}" in js.text
    assert "function copyInboxPath()" in js.text
    assert "navigator.clipboard.writeText(lastInboxPath)" in js.text


def test_web_js_inbox_capture_errors_are_safe_and_keep_form() -> None:
    client = TestClient(create_app(Settings()))
    js = client.get("/web/app.js")
    body = js.text.split("async function submitInboxCapture(event)", 1)[1].split("async function copyInboxPath()", 1)[0]

    assert "showInboxCaptureError" in body
    assert "normalizeUiError" in body
    assert "form.classList.add(\"hidden\")" not in body
    assert "Le titre est obligatoire." in js.text
    assert "L'information à mémoriser est obligatoire." in js.text
    assert "Le problème observé et l'amélioration proposée sont obligatoires." in js.text
