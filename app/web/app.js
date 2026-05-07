let currentSessionId = sessionStorage.getItem("vivi_session_id") || "";
let localApiKey = "";
let authEnabled = false;

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
}

function sessionLabel(sessionId) {
  if (!sessionId) {
    return "Session locale : nouvelle";
  }
  return `Session locale : ${sessionId.slice(0, 8)}...`;
}

function setCurrentSessionId(sessionId) {
  currentSessionId = sessionId || "";
  if (currentSessionId) {
    sessionStorage.setItem("vivi_session_id", currentSessionId);
  } else {
    sessionStorage.removeItem("vivi_session_id");
  }
  setText("session-status", sessionLabel(currentSessionId));
}

function appendMessage(role, content) {
  const log = document.getElementById("chat-log");
  const block = document.createElement("div");
  const roleClass = role === "Utilisateur" ? "msg-user" : "msg-assistant";
  block.className = `msg ${roleClass}`;

  const label = document.createElement("strong");
  label.textContent = role;

  const body = document.createElement("div");
  body.className = "msg-content";
  if (role === "VIVI") {
    renderMarkdownLite(body, content);
  } else {
    body.textContent = content;
  }

  block.append(label, body);
  log.appendChild(block);
  log.scrollTop = log.scrollHeight;
}

function appendInlineMarkdown(parent, text) {
  const value = String(text || "");
  const parts = value.split(/(\*\*[^*]+\*\*)/g);
  parts.forEach((part) => {
    if (!part) {
      return;
    }
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      const strong = document.createElement("strong");
      strong.textContent = part.slice(2, -2);
      parent.appendChild(strong);
      return;
    }
    parent.appendChild(document.createTextNode(part));
  });
}

function appendMarkdownBlock(container, tagName, text) {
  const el = document.createElement(tagName);
  appendInlineMarkdown(el, text);
  container.appendChild(el);
}

function flushMarkdownList(container, listState) {
  if (!listState.element) {
    return;
  }
  container.appendChild(listState.element);
  listState.element = null;
  listState.type = "";
}

function renderMarkdownLite(container, content) {
  try {
    const text = String(content || "");
    const lines = text.replace(/\r\n/g, "\n").split("\n");
    const paragraphLines = [];
    const listState = { element: null, type: "" };

    function flushParagraph() {
      if (!paragraphLines.length) {
        return;
      }
      flushMarkdownList(container, listState);
      appendMarkdownBlock(container, "p", paragraphLines.join(" "));
      paragraphLines.length = 0;
    }

    lines.forEach((rawLine) => {
      const line = rawLine.trim();
      if (!line) {
        flushParagraph();
        flushMarkdownList(container, listState);
        return;
      }

      if (line === "---" || line === "***") {
        flushParagraph();
        flushMarkdownList(container, listState);
        container.appendChild(document.createElement("hr"));
        return;
      }

      const heading = /^(#{1,3})\s+(.+)$/.exec(line);
      if (heading) {
        flushParagraph();
        flushMarkdownList(container, listState);
        appendMarkdownBlock(container, `h${heading[1].length + 2}`, heading[2]);
        return;
      }

      const unordered = /^[-*]\s+(.+)$/.exec(line);
      const ordered = /^\d+\.\s+(.+)$/.exec(line);
      if (unordered || ordered) {
        flushParagraph();
        const type = ordered ? "ol" : "ul";
        if (!listState.element || listState.type !== type) {
          flushMarkdownList(container, listState);
          listState.element = document.createElement(type);
          listState.type = type;
        }
        const item = document.createElement("li");
        appendInlineMarkdown(item, (ordered || unordered)[1]);
        listState.element.appendChild(item);
        return;
      }

      paragraphLines.push(line);
    });

    flushParagraph();
    flushMarkdownList(container, listState);

    if (!container.childNodes.length && text) {
      container.textContent = text;
    }
  } catch (err) {
    container.textContent = String(content || "");
  }
}

function showError(text) {
  const box = document.getElementById("error-box");
  box.textContent = text;
  box.classList.remove("hidden");
}

function showNormalizedError(normalized) {
  const box = document.getElementById("error-box");
  const primary = String(normalized?.primary || "").trim();
  const detail = String(normalized?.detail || "").trim();
  box.textContent = detail ? `${primary} ${detail}` : primary;
  box.classList.remove("hidden");
}

function setSecurityState() {
  if (!authEnabled) {
    setText("security-state", "auth désactivée");
    return;
  }
  if (localApiKey) {
    setText("security-state", "clé API locale renseignée");
    return;
  }
  setText("security-state", "clé API locale requise");
}

function updateAuthPanelVisibility() {
  const panel = document.getElementById("auth-panel");
  if (!panel) {
    return;
  }
  if (authEnabled) {
    panel.classList.remove("hidden");
  } else {
    panel.classList.add("hidden");
  }
  setSecurityState();
}

function applyApiKey() {
  const input = document.getElementById("api-key-input");
  const value = String(input?.value || "").trim();
  localApiKey = value;
  if (input) {
    input.value = "";
  }
  setSecurityState();
  clearError();
}

function clearApiKey() {
  localApiKey = "";
  const input = document.getElementById("api-key-input");
  if (input) {
    input.value = "";
  }
  setSecurityState();
}

function authHeaders(baseHeaders = {}) {
  const headers = { ...baseHeaders };
  if (localApiKey) {
    headers.Authorization = `Bearer ${localApiKey}`;
  }
  return headers;
}

function toReadableBackendError(payload, status) {
  const err = payload?.error || {};
  const code = String(err.code || "");
  const message = String(err.message || "");
  const hint = String(err.recovery_hint || "");
  const haystack = `${code} ${message} ${hint}`;

  if (status === 401 || status === 403 || code === "auth_required") {
    if (!localApiKey) {
      return {
        primary: "Authentification locale requise.",
        detail: "Renseigne la clé API VIVI configurée pour ce backend.",
      };
    }
    return {
      primary: "Clé API locale invalide.",
      detail: "Vérifie la clé VIVI saisie dans l'interface.",
    };
  }

  if (haystack.includes("lmstudio_unavailable") || haystack.includes("lmstudio_timeout")) {
    return {
      primary: "LM Studio est indisponible.",
      detail: "Vérifie que LM Studio est lancé, que le serveur local est actif et que l'endpoint est correct.",
    };
  }

  if (
    haystack.includes("lmstudio_model_missing") ||
    haystack.includes("LM Studio model is not configured") ||
    haystack.includes("VIVI_LMSTUDIO_MODEL")
  ) {
    return {
      primary: "Modèle LM Studio non configuré.",
      detail: "Configure VIVI_LMSTUDIO_MODEL avant d'envoyer une requête.",
      technical: code ? `[${code}]` : "",
    };
  }
  if (
    haystack.includes("lmstudio_http_error") &&
    haystack.includes("LM Studio returned HTTP 401")
  ) {
    return {
      primary: "LM Studio refuse la requête.",
      detail: "Si LM Studio demande une clé, configure uniquement VIVI_LMSTUDIO_API_KEY. Ne pas utiliser VIVI_API_KEY pour LM Studio.",
    };
  }

  if (status >= 500) {
    return {
      primary: "Erreur serveur VIVI.",
      detail: "Réessaie ou consulte les logs backend si le problème persiste.",
    };
  }

  return null;
}

function normalizeUiError({ status = 0, payload = null, networkError = null } = {}) {
  if (networkError) {
    return {
      primary: "Impossible de joindre VIVI.",
      detail: "Vérifie que le backend local est lancé.",
    };
  }

  const mapped = toReadableBackendError(payload, status);
  if (mapped) {
    return mapped;
  }

  const err = payload?.error || {};
  const code = String(err.code || "backend_error");
  const message = String(err.message || `HTTP ${status || "?"}`);
  const hint = String(err.recovery_hint || "").trim();
  const requestId = String(err.request_id || "").trim();
  const detailBits = [code, message];
  if (hint) {
    detailBits.push(hint);
  }
  if (requestId) {
    detailBits.push(`request_id=${requestId}`);
  }
  return {
    primary: "Erreur serveur VIVI.",
    detail: detailBits.join(" | "),
  };
}

function clearError() {
  const box = document.getElementById("error-box");
  box.textContent = "";
  box.classList.add("hidden");
}

function renderSources(sources) {
  const panel = document.getElementById("sources-panel");
  const list = document.getElementById("sources-list");
  const empty = document.getElementById("sources-empty");
  list.innerHTML = "";
  empty.classList.add("hidden");

  const mode = document.getElementById("mode").value;
  if (!sources || sources.length === 0) {
    if (mode === "document") {
      panel.classList.remove("hidden");
      empty.classList.remove("hidden");
      return;
    }
    panel.classList.add("hidden");
    return;
  }

  sources.forEach((src, index) => {
    const item = document.createElement("article");
    item.className = "source-item";
    const label = src.title || src.section || src.path || "source";
    const path = src.path || "";
    const sourceText = src.chunk_text || src.content || src.full_text || src.excerpt || "";
    const score = typeof src.score === "number" ? `score=${src.score.toFixed(2)}` : "score=n/a";
    const sourceNumber = index + 1;

    item.setAttribute("aria-label", `Source ${sourceNumber}: ${label}`);

    const header = document.createElement("div");
    header.className = "source-head";

    const indexLabel = document.createElement("span");
    indexLabel.className = "source-index";
    indexLabel.textContent = `Source ${sourceNumber}`;

    const title = document.createElement("strong");
    title.className = "source-title";
    title.textContent = label;

    const scoreLabel = document.createElement("span");
    scoreLabel.className = "source-score";
    scoreLabel.textContent = score;

    header.append(indexLabel, title, scoreLabel);

    const pathEl = document.createElement("div");
    pathEl.className = "source-path";
    pathEl.textContent = path || "chemin non fourni";

    const details = document.createElement("details");
    details.className = "source-details";

    const summary = document.createElement("summary");
    summary.textContent = "Afficher l'extrait utilisé";

    const excerptEl = document.createElement("div");
    excerptEl.className = "source-excerpt";
    excerptEl.textContent = sourceText || "Aucun contenu complet fourni.";

    details.append(summary, excerptEl);
    item.append(header, pathEl, details);
    list.appendChild(item);
  });

  panel.classList.remove("hidden");
}

async function loadRuntime() {
  setText("runtime-status", "Chargement runtime...");
  try {
    const res = await fetch("/runtime/info");
    if (!res.ok) {
      throw new Error(`runtime info HTTP ${res.status}`);
    }
      const payload = await res.json();
    authEnabled = Boolean(payload.auth_enabled);
    updateAuthPanelVisibility();
    setText("runtime-status", "Runtime OK");
    setText("backend-state", "ok");
    setText("provider-name", payload.provider?.name || "-");
    setText("provider-model", payload.provider?.model || "(non configuré)");
    const providerAvailable = Boolean(payload.provider?.available);
    setText("provider-available", String(providerAvailable));
    setText("vault-state", payload.vault?.exists ? "ok" : "absent");
    setText("vault-notes", String(payload.vault?.notes_count ?? "-"));
    if (!providerAvailable) {
      showNormalizedError({
        primary: "LM Studio est indisponible.",
        detail: "Vérifie que LM Studio est lancé, que le serveur local est actif et que l'endpoint est correct.",
      });
    }
  } catch (err) {
    authEnabled = false;
    updateAuthPanelVisibility();
    setText("runtime-status", "Runtime indisponible");
    setText("backend-state", "erreur");
    setText("vault-state", "-");
    setText("vault-notes", "-");
    showNormalizedError(normalizeUiError({ networkError: err }));
  }
}

async function sendChat(event) {
  event.preventDefault();
  clearError();

  const mode = document.getElementById("mode").value;
  const messageEl = document.getElementById("message");
  const message = messageEl.value.trim();

  if (!message) {
    showError("Le message ne peut pas être vide.");
    return;
  }

  const button = document.getElementById("send-btn");
  const loading = document.getElementById("loading");
  const form = document.getElementById("chat-form");
  button.disabled = true;
  form.setAttribute("aria-busy", "true");
  loading.classList.remove("hidden");

  appendMessage("Utilisateur", message);

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ message, mode, session_id: currentSessionId || null }),
    });

    const payload = await res.json().catch(() => ({}));

    if (!res.ok) {
      showNormalizedError(normalizeUiError({ status: res.status, payload }));
      appendMessage("VIVI", "Erreur lors de la requête.");
      return;
    }

    appendMessage("VIVI", payload.answer || "(réponse vide)");
    setCurrentSessionId(payload.session_id || "");
    renderSources(payload.sources || []);
    messageEl.value = "";
  } catch (err) {
    appendMessage("VIVI", "Erreur lors de la requête.");
    showNormalizedError(normalizeUiError({ networkError: err }));
  } finally {
    button.disabled = false;
    form.setAttribute("aria-busy", "false");
    loading.classList.add("hidden");
  }
}

function resetConversation() {
  document.getElementById("chat-log").innerHTML = "";
  document.getElementById("sources-list").innerHTML = "";
  document.getElementById("sources-panel").classList.add("hidden");
  document.getElementById("sources-empty").classList.add("hidden");
  setCurrentSessionId("");
  showError("Conversation réinitialisée localement.");
}

window.addEventListener("DOMContentLoaded", () => {
  setCurrentSessionId(currentSessionId);
  updateAuthPanelVisibility();
  loadRuntime();
  document.getElementById("chat-form").addEventListener("submit", sendChat);
  document.getElementById("refresh-runtime-btn").addEventListener("click", loadRuntime);
  document.getElementById("reset-conversation-btn").addEventListener("click", resetConversation);
  document.getElementById("apply-api-key-btn").addEventListener("click", applyApiKey);
  document.getElementById("clear-api-key-btn").addEventListener("click", clearApiKey);
});
