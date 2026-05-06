function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
}

function appendMessage(role, content) {
  const log = document.getElementById("chat-log");
  const block = document.createElement("div");
  block.className = "msg";
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
  list.innerHTML = "";

  if (!sources || sources.length === 0) {
    panel.classList.add("hidden");
    return;
  }

  for (const src of sources) {
    const item = document.createElement("li");
    item.className = "source-item";
    const titleOrPath = src.title || src.path || "source";
    const path = src.path || "";
    const excerpt = src.excerpt || "";
    const score = typeof src.score === "number" ? `score=${src.score.toFixed(2)}` : "score=n/a";
    item.innerHTML = `<div><strong>${titleOrPath}</strong> (${score})</div><div>${path}</div><div>${excerpt}</div>`;
    list.appendChild(item);
  }

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
    setText("provider-available", String(payload.provider?.available));
  } catch (err) {
    setText("runtime-status", "Runtime indisponible");
    setText("backend-state", "erreur");
    showError(`Erreur runtime: ${err.message}`);
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
  button.disabled = true;
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
    showError(err.message);
  } finally {
    button.disabled = false;
    loading.classList.add("hidden");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadRuntime();
  document.getElementById("chat-form").addEventListener("submit", sendChat);
});
