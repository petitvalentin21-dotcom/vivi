function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, mode }),
    });

    const payload = await res.json().catch(() => ({}));

    if (!res.ok) {
      const err = payload.error || {};
      const code = err.code || "backend_error";
      const msg = err.message || `HTTP ${res.status}`;
      const hint = err.recovery_hint ? ` (${err.recovery_hint})` : "";
      throw new Error(`${code}: ${msg}${hint}`);
    }

    appendMessage("VIVI", payload.answer || "(réponse vide)");
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

window.addEventListener("DOMContentLoaded", () => {
  loadRuntime();
  document.getElementById("chat-form").addEventListener("submit", sendChat);
  document.getElementById("refresh-runtime-btn").addEventListener("click", loadRuntime);
});
