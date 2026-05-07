# Skill: vivi-mvp-ui

## Purpose

Guide UI changes for the VIVI local-first MVP.

Use this skill when modifying:

- app/web/index.html
- app/web/style.css
- app/web/app.js
- tests/test_web_interface.py

The goal is to make the interface clear, accessible, stable and pleasant without expanding the MVP scope.

## Product context

VIVI is a local-first personal AI assistant.

Current MVP interface:

- vanilla HTML/CSS/JS;
- no frontend build step;
- no frontend framework;
- talks to the local FastAPI backend;
- displays runtime status;
- supports chat mode;
- supports document mode with lexical Obsidian RAG;
- displays visible sources;
- supports a simple local API key UI;
- keeps only the session id in sessionStorage;
- keeps the API key only in JS memory.

## Core UI principles

Prioritize:

- clarity over decoration;
- stable layout over novelty;
- readable hierarchy;
- short labels;
- explicit states;
- accessible controls;
- keyboard usability;
- responsive behavior for common desktop/tablet widths;
- deterministic rendering;
- minimal JavaScript.

Every UI change should preserve:

- chat functionality;
- document mode functionality;
- source rendering;
- runtime refresh;
- auth key behavior;
- session reset behavior;
- error handling;
- accessibility roles and labels.

## Visual style guidance

Use a simple local-app aesthetic:

- calm layout;
- clear spacing;
- readable font sizes;
- strong contrast;
- visible focus states;
- distinct user and assistant messages;
- source cards that are scannable;
- runtime status that is compact but understandable;
- warning/error states that are visible without being noisy.

Do not chase a marketing landing-page style.

Do not make VIVI look like a SaaS dashboard.

Do not add visual complexity unless it improves MVP usability.

## Accessibility requirements

Preserve or improve:

- explicit labels for inputs and controls;
- keyboard navigation;
- visible focus via `:focus-visible`;
- `aria-live` where dynamic status changes are announced;
- `role=status` for non-critical status updates;
- `role=alert` for important errors;
- semantic buttons instead of clickable divs;
- sufficient color contrast;
- readable text without relying only on color.

Do not remove existing accessibility attributes unless replacing them with a better equivalent.

## Error UX requirements

Errors must be:

- short;
- actionable;
- non-technical by default;
- safe;
- without secrets;
- without Authorization headers;
- without API key values.

When technical details are useful, show them as secondary details.

Important cases to keep understandable:

- auth required;
- invalid local API key;
- LM Studio unavailable;
- LM Studio model missing;
- LM Studio HTTP 401;
- backend/network unreachable;
- generic server error;
- document mode with no sources.

## Source rendering requirements

In document mode:

- show sources clearly;
- use explicit labels such as `Source 1`, `Source 2`;
- show title/path/excerpt/score only if already available;
- keep source cards readable;
- do not rely on implicit HTML list numbering;
- if no source is found, show a discreet non-blocking message.

Do not invent sources.

Do not hide sources when `rag_used=true` and sources are returned.

## State and storage rules

Allowed:

- keep current session id in JS state;
- store only session id in sessionStorage;
- keep API key only in JS memory.

Forbidden:

- localStorage for API keys;
- sessionStorage for API keys;
- cookies for API keys;
- persistent frontend preferences;
- database;
- login flow;
- multi-user state.

Reset conversation must:

- clear visible conversation;
- clear visible sources;
- forget the frontend session id;
- not clear the API key.

## Frontend architecture rules

Use only:

- vanilla HTML;
- vanilla CSS;
- vanilla JavaScript.

Do not add:

- React;
- Vue;
- Svelte;
- Tailwind;
- Bootstrap;
- shadcn/ui;
- Material UI;
- frontend router;
- frontend build tool;
- state manager;
- charting library;
- animation library.

Do not introduce a design system package.

Do not split the UI into many files unless there is a clear MVP maintainability reason.

## Responsive behavior

The interface should remain usable on:

- common desktop screens;
- laptop screens;
- tablet-width screens.

Use simple CSS:

- flexible containers;
- reasonable max-width;
- wrapping controls;
- readable spacing.

Do not implement a full mobile app layout.

Do not add app/mobile-specific behavior.

## Testing expectations

For UI changes, update `tests/test_web_interface.py`.

Tests should verify the presence and preservation of:

- main chat form;
- mode selector;
- runtime status area;
- auth key area;
- reset conversation button;
- error display area;
- source rendering area;
- accessibility attributes;
- help text if relevant.

Do not add Playwright, Selenium, Cypress, or heavy browser testing unless explicitly requested.

Prefer lightweight static HTML/JS checks consistent with the existing test style.

## Scope guard

For UI tasks, do not add:

- agents;
- orchestrator;
- provider registry;
- external providers;
- OpenAI;
- Mammouth;
- Ollama priority;
- vector database;
- embeddings;
- Open WebUI as primary interface;
- cockpit;
- advanced dashboard;
- login;
- multi-user;
- backend feature changes;
- Obsidian writes.

If a UI request seems to require backend changes, stop and report the required backend change instead of silently expanding scope.

## Completion criteria

A UI change is acceptable only if:

- `pytest -q tests/test_web_interface.py` passes;
- `pytest -q` passes;
- existing chat behavior is preserved;
- existing document mode behavior is preserved;
- existing auth behavior is preserved;
- existing session behavior is preserved;
- no secret is exposed;
- no forbidden dependency is added;
- no post-MVP feature is introduced.

## Rapport attendu

Créer ou mettre à jour uniquement :

- tmp/codex_last_report.md
- tmp/codex_report_YYYY-MM-DD_HH-mm-ss.md

Le rapport doit contenir :

- Summary
- Files changed
- Changes
- Tests
- Scope guard

## Validation attendue

- Le fichier `.agents/skills/vivi-mvp-ui/SKILL.md` existe.
- Le contenu est clair et strict.
- Aucune modification UI effective n’a été faite dans cette tâche.
- Aucun ajout post-MVP.
- Aucun commit.
- Aucun push.
