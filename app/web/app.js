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
  block.innerHTML = `<strong>${role}</strong><div>${content}</div>`;
  log.appendChild(block);
  log.scrollTop = log.scrollHeight;
}

function showError(text) {
  const box = document.getElementById("error-box");
  box.textContent = text;
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

function toReadableAuthError(status, payload) {
  const code = payload?.error?.code || payload?.detail?.error?.code || "";
  if (status === 401 || status === 403 || code === "auth_required") {
    if (!localApiKey) {
      return "Authentification locale activée : renseigne la clé API.";
    }
    return "Clé API locale invalide.";
  }
  return null;
}

function toReadableBackendError(payload) {
  const err = payload?.error || {};
  const code = String(err.code || "");
  const message = String(err.message || "");
  const hint = String(err.recovery_hint || "");
  const haystack = `${code} ${message} ${hint}`;

  if (
    haystack.includes("lmstudio_model_missing") ||
    haystack.includes("LM Studio model is not configured") ||
    haystack.includes("VIVI_LMSTUDIO_MODEL")
  ) {
    return "Modèle LM Studio non configuré. Vérifie VIVI_LMSTUDIO_MODEL puis relance le backend.";
  }
  if (
    haystack.includes("lmstudio_http_error") &&
    haystack.includes("LM Studio returned HTTP 401")
  ) {
    return "LM Studio refuse la requête avec une erreur 401. Vérifie la configuration d'auth LM Studio et ne confonds pas VIVI_API_KEY avec une clé LM Studio.";
  }

  return null;
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
    const item = document.createElement("div");
    item.className = "source-item";
    const label = src.title || src.section || src.path || "source";
    const path = src.path || "";
    const excerpt = src.excerpt || "";
    const score = typeof src.score === "number" ? `score=${src.score.toFixed(2)}` : "score=n/a";
    const sourceNumber = index + 1;
    item.innerHTML = `
      <div class="source-head">
        <span class="source-index">Source ${sourceNumber}</span>
        <strong>${label}</strong>
        <span class="source-score">${score}</span>
      </div>
      <div class="source-path">${path}</div>
      <div class="source-excerpt">${excerpt}</div>
    `;
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
      showError("Provider LM Studio indisponible. Vérifie que LM Studio est lancé avec un modèle chargé.");
    }
  } catch (err) {
    authEnabled = false;
    updateAuthPanelVisibility();
    setText("runtime-status", "Runtime indisponible");
    setText("backend-state", "erreur");
    setText("vault-state", "-");
    setText("vault-notes", "-");
    showError(`Erreur runtime: ${err.message || "backend indisponible"}`);
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
      const authMessage = toReadableAuthError(res.status, payload);
      if (authMessage) {
        throw new Error(authMessage);
      }
      const backendMessage = toReadableBackendError(payload);
      if (backendMessage) {
        const backendCode = payload?.error?.code ? ` [${payload.error.code}]` : "";
        throw new Error(`${backendMessage}${backendCode}`);
      }
      const err = payload.error || {};
      const code = err.code || "backend_error";
      const msg = err.message || `HTTP ${res.status}`;
      const hint = err.recovery_hint ? ` (${err.recovery_hint})` : "";
      throw new Error(`${code}: ${msg}${hint}`);
    }

    appendMessage("VIVI", payload.answer || "(réponse vide)");
    setCurrentSessionId(payload.session_id || "");
    renderSources(payload.sources || []);
    messageEl.value = "";
  } catch (err) {
    appendMessage("VIVI", "Erreur lors de la requête.");
    showError(err.message || "Erreur réseau ou backend indisponible.");
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
