let currentSessionId = sessionStorage.getItem("vivi_session_id") || "";
let localApiKey = "";
let authEnabled = false;
let lastUserMessage = "";
let activeInboxCaptureType = "";
let lastInboxPath = "";
let conversationLog = [];

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
}

function sessionLabel(sessionId) {
  if (!sessionId) {
    return "Session : nouvelle";
  }
  return `Session : ${sessionId.slice(0, 8)}...`;
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
  const parts = value.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
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
    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      const code = document.createElement("code");
      code.textContent = part.slice(1, -1);
      parent.appendChild(code);
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

function flushMarkdownTable(container, tableState) {
  if (!tableState.rows.length) {
    return;
  }
  const table = document.createElement("table");
  const rows = tableState.rows;
  let bodyStart = 0;

  if (rows.length >= 2 && rows[1].isSep) {
    const thead = document.createElement("thead");
    const tr = document.createElement("tr");
    rows[0].cells.forEach((cell) => {
      const th = document.createElement("th");
      appendInlineMarkdown(th, cell);
      tr.appendChild(th);
    });
    thead.appendChild(tr);
    table.appendChild(thead);
    bodyStart = 2;
  }

  const dataRows = rows.slice(bodyStart).filter((r) => !r.isSep);
  if (dataRows.length) {
    const tbody = document.createElement("tbody");
    dataRows.forEach((row) => {
      const tr = document.createElement("tr");
      row.cells.forEach((cell) => {
        const td = document.createElement("td");
        appendInlineMarkdown(td, cell);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
  }

  container.appendChild(table);
  tableState.rows = [];
}

function renderMarkdownLite(container, content) {
  try {
    const text = String(content || "");
    const lines = text.replace(/\r\n/g, "\n").split("\n");
    const paragraphLines = [];
    const listState = { element: null, type: "" };
    const tableState = { rows: [] };
    let inCodeBlock = false;
    const codeLines = [];

    const TABLE_ROW_RE = /^\|(.+)\|$/;
    const TABLE_SEP_RE = /^\|[\-:\|\s]+\|$/;

    function flushParagraph() {
      if (!paragraphLines.length) {
        return;
      }
      flushMarkdownList(container, listState);
      flushMarkdownTable(container, tableState);
      appendMarkdownBlock(container, "p", paragraphLines.join(" "));
      paragraphLines.length = 0;
    }

    lines.forEach((rawLine) => {
      if (inCodeBlock) {
        if (rawLine.trimStart().startsWith("```")) {
          inCodeBlock = false;
          const pre = document.createElement("pre");
          const codeEl = document.createElement("code");
          codeEl.textContent = codeLines.join("\n");
          pre.appendChild(codeEl);
          container.appendChild(pre);
          codeLines.length = 0;
        } else {
          codeLines.push(rawLine);
        }
        return;
      }

      const line = rawLine.trim();

      if (line.startsWith("```")) {
        flushParagraph();
        flushMarkdownList(container, listState);
        flushMarkdownTable(container, tableState);
        inCodeBlock = true;
        return;
      }

      if (!line) {
        flushParagraph();
        flushMarkdownList(container, listState);
        flushMarkdownTable(container, tableState);
        return;
      }

      if (line === "---" || line === "***") {
        flushParagraph();
        flushMarkdownList(container, listState);
        flushMarkdownTable(container, tableState);
        container.appendChild(document.createElement("hr"));
        return;
      }

      const heading = /^(#{1,3})\s+(.+)$/.exec(line);
      if (heading) {
        flushParagraph();
        flushMarkdownList(container, listState);
        flushMarkdownTable(container, tableState);
        appendMarkdownBlock(container, `h${heading[1].length + 2}`, heading[2]);
        return;
      }

      if (TABLE_ROW_RE.test(line)) {
        flushParagraph();
        flushMarkdownList(container, listState);
        if (TABLE_SEP_RE.test(line)) {
          tableState.rows.push({ isSep: true, cells: [] });
        } else {
          const cells = line.slice(1, -1).split("|").map((c) => c.trim());
          tableState.rows.push({ isSep: false, cells });
        }
        return;
      }

      flushMarkdownTable(container, tableState);

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

    if (inCodeBlock && codeLines.length) {
      const pre = document.createElement("pre");
      const codeEl = document.createElement("code");
      codeEl.textContent = codeLines.join("\n");
      pre.appendChild(codeEl);
      container.appendChild(pre);
    }

    flushParagraph();
    flushMarkdownList(container, listState);
    flushMarkdownTable(container, tableState);

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

function clearInboxCaptureMessages() {
  const status = document.getElementById("inbox-capture-status");
  const error = document.getElementById("inbox-capture-error");
  const copyBtn = document.getElementById("copy-inbox-path-btn");
  if (status) {
    status.textContent = "";
    status.classList.add("hidden");
  }
  if (error) {
    error.textContent = "";
    error.classList.add("hidden");
  }
  if (copyBtn) {
    copyBtn.classList.add("hidden");
  }
  lastInboxPath = "";
}

function showInboxCaptureError(text) {
  const error = document.getElementById("inbox-capture-error");
  error.textContent = text;
  error.classList.remove("hidden");
}

function showInboxCaptureSuccess(relativePath) {
  const status = document.getElementById("inbox-capture-status");
  const copyBtn = document.getElementById("copy-inbox-path-btn");
  lastInboxPath = relativePath || "";
  status.textContent = `Note créée dans ${lastInboxPath}`;
  status.classList.remove("hidden");
  if (copyBtn && lastInboxPath && navigator.clipboard) {
    copyBtn.classList.remove("hidden");
  }
}

function defaultInboxTitle(prefix) {
  const source = lastUserMessage || String(document.getElementById("message")?.value || "").trim();
  if (!source) {
    return prefix;
  }
  const compact = source.replace(/\s+/g, " ").slice(0, 56).trim();
  return compact ? `${prefix} - ${compact}` : prefix;
}

function openInboxCapture(type) {
  activeInboxCaptureType = type;
  clearInboxCaptureMessages();

  const form = document.getElementById("inbox-capture-form");
  const title = document.getElementById("inbox-title");
  const memoryFields = document.getElementById("memory-info-fields");
  const improvementFields = document.getElementById("memory-improvement-fields");
  const currentDraft = String(document.getElementById("message")?.value || "").trim();
  const seed = lastUserMessage || currentDraft;

  form.classList.remove("hidden");
  memoryFields.classList.toggle("hidden", type !== "info");
  improvementFields.classList.toggle("hidden", type !== "improvement");

  if (type === "info") {
    title.value = defaultInboxTitle("Information à mémoriser");
    document.getElementById("memory-info-content").value = seed;
    document.getElementById("memory-info-context").value = seed
      ? "Information issue d'un échange utilisateur dans VIVI."
      : "";
  } else {
    title.value = defaultInboxTitle("Amélioration proposée");
    document.getElementById("improvement-problem").value = "";
    document.getElementById("improvement-proposal").value = "";
    document.getElementById("improvement-category").value = "UX";
    document.getElementById("improvement-priority").value = "moyenne";
  }

  title.focus();
}

function cancelInboxCapture() {
  activeInboxCaptureType = "";
  clearInboxCaptureMessages();
  document.getElementById("inbox-capture-form").classList.add("hidden");
  document.getElementById("memory-info-fields").classList.add("hidden");
  document.getElementById("memory-improvement-fields").classList.add("hidden");
}

function buildMemoryInfoBody(title, information, context) {
  const resolvedContext = context || "Information issue d'un échange utilisateur dans VIVI.";
  return [
    `# ${title}`,
    "",
    "> Proposition générée par VIVI. À relire avant toute intégration dans les notes sources.",
    "",
    "## Information à mémoriser",
    "",
    information,
    "",
    "## Contexte",
    "",
    resolvedContext,
    "",
    "## Validation",
    "",
    "- Statut : brouillon",
    "- Indexation : désactivée",
    "- Relecture humaine requise",
  ].join("\n");
}

function buildImprovementBody(title, problem, proposal, category, priority) {
  return [
    `# ${title}`,
    "",
    "> Proposition générée par VIVI. À relire avant toute intégration au backlog.",
    "",
    "## Problème observé",
    "",
    problem,
    "",
    "## Amélioration proposée",
    "",
    proposal,
    "",
    "## Catégorie",
    "",
    category,
    "",
    "## Priorité proposée",
    "",
    priority,
    "",
    "## Validation",
    "",
    "- Statut : brouillon",
    "- Indexation : désactivée",
    "- Relecture humaine requise",
  ].join("\n");
}

function buildInboxCapturePayload() {
  const title = String(document.getElementById("inbox-title")?.value || "").trim();
  if (!title) {
    return { error: "Le titre est obligatoire." };
  }

  if (activeInboxCaptureType === "info") {
    const information = String(document.getElementById("memory-info-content")?.value || "").trim();
    const context = String(document.getElementById("memory-info-context")?.value || "").trim();
    if (!information) {
      return { error: "L'information à mémoriser est obligatoire." };
    }
    return {
      payload: {
        title,
        body: buildMemoryInfoBody(title, information, context),
        note_type: "clarification_note",
        status: "draft",
        prompt_summary: "action explicite depuis Mémoire VIVI",
      },
    };
  }

  if (activeInboxCaptureType === "improvement") {
    const problem = String(document.getElementById("improvement-problem")?.value || "").trim();
    const proposal = String(document.getElementById("improvement-proposal")?.value || "").trim();
    const category = String(document.getElementById("improvement-category")?.value || "Autre").trim();
    const priority = String(document.getElementById("improvement-priority")?.value || "moyenne").trim();
    if (!problem || !proposal) {
      return { error: "Le problème observé et l'amélioration proposée sont obligatoires." };
    }
    return {
      payload: {
        title,
        body: buildImprovementBody(title, problem, proposal, category, priority),
        note_type: "backlog_proposal",
        status: "draft",
        prompt_summary: "proposition d'amélioration depuis Mémoire VIVI",
      },
    };
  }

  return { error: "Choisis une action Mémoire VIVI." };
}

async function submitInboxCapture(event) {
  event.preventDefault();
  clearInboxCaptureMessages();

  const built = buildInboxCapturePayload();
  if (built.error) {
    showInboxCaptureError(built.error);
    return;
  }

  const submitBtn = document.getElementById("submit-inbox-capture-btn");
  const form = document.getElementById("inbox-capture-form");
  submitBtn.disabled = true;
  form.setAttribute("aria-busy", "true");

  try {
    const res = await fetch("/obsidian/inbox", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(built.payload),
    });
    const payload = await res.json().catch(() => ({}));

    if (!res.ok) {
      const normalized = normalizeUiError({ status: res.status, payload });
      showInboxCaptureError(normalized.detail ? `${normalized.primary} ${normalized.detail}` : normalized.primary);
      return;
    }

    showInboxCaptureSuccess(payload.relative_path || `92_inbox/${payload.filename || ""}`);
  } catch (err) {
    const normalized = normalizeUiError({ networkError: err });
    showInboxCaptureError(`${normalized.primary} ${normalized.detail}`);
  } finally {
    submitBtn.disabled = false;
    form.setAttribute("aria-busy", "false");
  }
}

async function copyInboxPath() {
  if (!lastInboxPath || !navigator.clipboard) {
    return;
  }
  await navigator.clipboard.writeText(lastInboxPath);
  const status = document.getElementById("inbox-capture-status");
  status.textContent = `Chemin copié : ${lastInboxPath}`;
  status.classList.remove("hidden");
}

function renderSources(sources) {
  const panel = document.getElementById("sources-panel");
  const list = document.getElementById("sources-list");
  const title = document.getElementById("sources-title");
  list.innerHTML = "";

  if (!sources || sources.length === 0) {
    panel.classList.add("hidden");
    return;
  }

  sources.forEach((src, index) => {
    const item = document.createElement("article");
    const isLow = Boolean(src.is_low_confidence);
    item.className = isLow ? "source-item source-item--low" : "source-item";
    const label = src.title || src.section || src.path || "source";
    const path = src.path || "";
    const sourceText = src.chunk_text || src.content || src.full_text || src.excerpt || "";
    const score = typeof src.score === "number" ? `score=${src.score.toFixed(2)}` : "score=n/a";
    const sourceNumber = index + 1;

    item.setAttribute("aria-label", `Source ${sourceNumber}: ${label}${isLow ? " (confiance faible)" : ""}`);

    const header = document.createElement("div");
    header.className = "source-head";

    const indexLabel = document.createElement("span");
    indexLabel.className = "source-index";
    indexLabel.textContent = `Source ${sourceNumber}`;

    const titleEl = document.createElement("strong");
    titleEl.className = "source-title";
    titleEl.textContent = label;

    const scoreLabel = document.createElement("span");
    scoreLabel.className = "source-score";
    scoreLabel.textContent = score;

    if (isLow) {
      const badge = document.createElement("span");
      badge.className = "source-badge-low";
      badge.title = "Cette source a un score de pertinence faible.";
      badge.textContent = "faible";
      header.append(indexLabel, titleEl, scoreLabel, badge);
    } else {
      header.append(indexLabel, titleEl, scoreLabel);
    }

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

  if (title) title.textContent = `Sources (${sources.length})`;
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
    setText("provider-name", payload.provider?.name || "-");
    setText("provider-model", payload.provider?.model || "(non configuré)");
    const providerAvailable = Boolean(payload.provider?.available);
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
    showNormalizedError(normalizeUiError({ networkError: err }));
  }
}

async function sendChat(event) {
  event.preventDefault();
  clearError();

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
  lastUserMessage = message;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ message, use_rag: true, mode: "chat", session_id: currentSessionId || null }),
    });

    const payload = await res.json().catch(() => ({}));

    if (!res.ok) {
      showNormalizedError(normalizeUiError({ status: res.status, payload }));
      appendMessage("VIVI", "Erreur lors de la requête.");
      return;
    }

    const answer = payload.answer || "(réponse vide)";
    appendMessage("VIVI", answer);
    conversationLog.push({ role: "user", content: message });
    conversationLog.push({ role: "assistant", content: answer });
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

function exportConversation() {
  const messages = conversationLog.slice();
  if (!messages.some((m) => m.role === "user")) return;
  conversationLog = [];
  const body = JSON.stringify({ session_id: currentSessionId || null, messages });
  try {
    fetch("/conversation/export", {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body,
    });
  } catch (_) {}
}

function resetConversation() {
  exportConversation();
  document.getElementById("chat-log").innerHTML = "";
  document.getElementById("sources-list").innerHTML = "";
  const sourcesPanel = document.getElementById("sources-panel");
  sourcesPanel.classList.add("hidden");
  sourcesPanel.removeAttribute("open");
  const sourcesTitle = document.getElementById("sources-title");
  if (sourcesTitle) sourcesTitle.textContent = "Sources";
  setCurrentSessionId("");
  showError("Conversation réinitialisée — export dans Obsidian Inbox.");
}

window.addEventListener("beforeunload", () => {
  if (!conversationLog.some((m) => m.role === "user")) return;
  const data = JSON.stringify({ session_id: currentSessionId || null, messages: conversationLog });
  navigator.sendBeacon("/conversation/export", new Blob([data], { type: "application/json" }));
  conversationLog = [];
});

window.addEventListener("DOMContentLoaded", () => {
  setCurrentSessionId(currentSessionId);
  updateAuthPanelVisibility();
  loadRuntime();
  document.getElementById("chat-form").addEventListener("submit", sendChat);
  document.getElementById("refresh-runtime-btn").addEventListener("click", loadRuntime);
  document.getElementById("reset-conversation-btn").addEventListener("click", resetConversation);
  document.getElementById("apply-api-key-btn").addEventListener("click", applyApiKey);
  document.getElementById("clear-api-key-btn").addEventListener("click", clearApiKey);
  document.getElementById("memory-info-btn").addEventListener("click", () => openInboxCapture("info"));
  document.getElementById("memory-improvement-btn").addEventListener("click", () => openInboxCapture("improvement"));
  document.getElementById("inbox-capture-form").addEventListener("submit", submitInboxCapture);
  document.getElementById("cancel-inbox-capture-btn").addEventListener("click", cancelInboxCapture);
  document.getElementById("copy-inbox-path-btn").addEventListener("click", copyInboxPath);
});
