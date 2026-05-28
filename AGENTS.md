# AGENTS.md — VIVI Project Instructions

> Valid for Codex, Cursor, and any agent reading this file directly. **Claude Code** uses `CLAUDE.md` as primary entry point.

## 1. Project identity

You are working on the project VIVI.

VIVI is a personal local AI assistant — strictly personal. No commercialization, no legal structure, no marketing.

VIVI_IA is the legacy laboratory. Do not treat it as the active product. See Appendix A for legacy audit policy.

The active product is VIVI.

---

## 2. Product vision

VIVI is a **proactive** local personal AI assistant.

The first functional domain is **Repas** (meals):

- daily decision: "what are we having tonight?";
- weekend batch cooking planning;
- live shopping list.

Core behaviors:

- proactively prompts at 18:30 on weekdays and Saturday mornings;
- cooking for 2 people with identical preferences;
- supports batch cooking;
- uses an internal recipe catalogue as primary source; LLM is a complement, not the sole source.

Architecture principle: one conversational LLM core (local chat via Ollama) + specialized Python code modules. **Not a multi-LLM system.**

The LLM contains no business logic. Business logic lives in Python modules.

Everything else is post-MVP unless explicitly approved.

---

## 3. Source of truth

Product and architecture decisions made in Phase 0–4 are authoritative.

Phase documents are located in:

- `knowledge_vault/00_product/` — product framing
- `knowledge_vault/02_architecture/` — validated architecture
- `knowledge_vault/03_decisions/` — design decisions

Before any implementation task, read:

- AGENTS.md
- README.md
- the relevant product or architecture note
- `tmp/codex_last_report.md` if present

If the user request conflicts with Phase 0–4 scope, report the conflict before implementing.

---

## 4. Current repo policy

This repository is the clean VIVI repo.

Strategy:

- build a clean MVP;
- audit legacy only when useful;
- import concepts selectively;
- avoid legacy complexity.

Do not import VIVI_IA wholesale.

---

## 5. MVP priorities

First domain: Repas.

Priority order:

1. conversational LLM core (Ollama);
2. Repas module (daily decision, batch planning, shopping list);
3. internal recipe catalogue;
4. proactive scheduling (18:30 weekdays, Saturday morning);
5. simple session memory;
6. FastAPI backend with minimal endpoints;
7. SvelteKit PWA interface.

Control question before every feature:

> Is this required to support the Repas domain, talk to Ollama, and give a reliable answer?

If no, classify as post-MVP, backlog, or reject.

---

## 6. Outside MVP scope

Do not implement in the MVP:

- multi-LLM agents (several LLMs in dialogue);
- specialized LLM agents (DEV, PM, ARCH, QA, Finance, Home, etc.);
- auto-improvement agent;
- automatic skill creation;
- Codex calls from VIVI;
- native iOS/Android app (PWA is authorized — see §9);
- fallback to external providers (OpenAI, Mammouth, etc.);
- multi-provider routing;
- vector database;
- embeddings-based retrieval;
- complex orchestrator;
- runtime skills;
- advanced cockpit UI;
- multi-user support;
- automatic modification of source Obsidian notes;
- SQLCipher (post-MVP; use SQLite vanilla at MVP).

These topics may be documented as post-MVP, but must not complicate MVP implementation.

Note: the **Repas module** is authorized — it is a Python code module, not an agent.

Note: Ollama is now the active MVP provider since FEAT-16. LM Studio is no longer used.

---

## 7. Ollama provider rule

Ollama is the MVP provider since FEAT-16.

Allowed:

- Ollama local API;
- configurable base URL;
- configurable model;
- healthcheck;
- chat completion;
- safe provider errors;
- tests using mocks.

Default values:

- `VIVI_OLLAMA_BASE_URL=http://localhost:11434`
- `VIVI_LLM_TIMEOUT_SECONDS=60`

Do not add:

- ProviderRegistry;
- multi-provider fallback;
- OpenAI implementation;
- benchmark routing;
- automatic model selection.

---

## 8. Backend architecture

Stack: Python 3.12+ / FastAPI / monorepo monoprocess.

Tooling: `uv` + `ruff` + `pyright` + `pytest`.

Test coverage target: ≥70% on business modules (`meals/`, `llm/`, `knowledge/`).

Expected modules:

```text
app/
  api/
  llm/          # OllamaClient
  knowledge/
  meals/
    recettes/   # FEAT-18 — CRUD recettes
    stock/      # FEAT-19 — Batch + IngredientBase
  db/           # FEAT-17 — SQLite + Alembic
  sessions/
  runtime/
tests/
migrations/
```

Persistence:

- SQLite + SQLModel + Alembic at MVP;
- SQLCipher post-MVP;
- restic encrypted backups from MVP.

Active endpoints:

- `GET /health`
- `GET /runtime/info`
- `POST /chat`
- `GET /knowledge/search`
- `POST /obsidian/inbox`
- `POST /conversation/export`
- `/recettes` — 6 endpoints (FEAT-18)
- `/stock`    — 13 endpoints (FEAT-19)

Current test count: 329 passed (`pytest tests/ -q`)

Implement progressively by FEAT. Do not add an orchestrator layer until basic chat + Repas MVP is validated.

---

## 9. Frontend architecture

Client: SvelteKit PWA + Tailwind CSS.

Deployment topology:

- primary: Windows desktop PC (on H24);
- secondary (2–3 months): Linux mini-PC;
- mobile access: Tailscale + iPhone (PWA in browser).

Authorized:

- SvelteKit + Tailwind;
- Web Push API (push notifications via FastAPI backend);
- Tailscale for mobile network access.

Not authorized:

- native iOS app;
- native Android app;
- Tauri desktop wrapper;
- Swift or Kotlin native code.

Auth at MVP: permissive — Tailscale acts as network-level auth. FastAPI middleware pre-equipped for Bearer token post-MVP, inactive at MVP.

---

## 10. Tool calling policy

Format: OpenAI function calling standard (compatible with Ollama).

Rules:

- central dispatcher in `backend/app/core/tools/`;
- maximum 5 tool calls per conversation turn;
- read-only tools: execute without user confirmation;
- write or destructive tools: require explicit user confirmation before execution;
- all tool definitions versioned in Git.

---

## 11. Prompts policy

All prompts versioned in Git. Never hard-code prompts in Python source.

Location: `backend/app/core/prompts/`
Format: Markdown files.

Three levels:

1. **System** — base personality, global constraints;
2. **Contextual** — domain-specific framing (Repas, etc.);
3. **Tools** — tool-use instructions.

---

## 12. Obsidian vault policy

The Obsidian vault is located at: `knowledge_vault/`

Central rule:

> AI-generated writes go only to `generated/`, `runtime/`, or `inbox/`, never directly into source notes.

Vault zones:

- `00_product/` — product framing
- `01_user_docs/` — user documentation
- `02_architecture/` — validated architecture
- `03_decisions/` — project decisions
- `04_backlog/` — backlog and ideas
- `05_runs/` — run logs if explicitly requested
- `90_generated/` — generated content
- `91_runtime/` — runtime data, indexes, logs
- `92_inbox/` — proposals to validate
- `99_archive/` — archives

Do not automatically modify: product framing notes, validated architecture, decision notes, human documentation, README.md, source notes.

For normal implementation tasks, write execution reports to `tmp/`.

---

## 13. Run history policy

The canonical run history lives in `knowledge_vault/05_runs/`.

After each significant FEAT, create a note:

- filename: `YYYY-MM-DD_FEAT-short-name.md`
- frontmatter: `doc_type: run`, `llm_index: false`, `llm_priority: low`
- content: summary, modified files, test validation, result, method note if relevant.

`tmp/` is scratch space only — transient, never committed, overwritten freely.

Codex creates the run log automatically after each FEAT without waiting to be asked.

Steps:

1. Create `knowledge_vault/05_runs/YYYY-MM-DD_FEAT-NN-slug.md` with standard frontmatter
2. Stage it: `git add knowledge_vault/05_runs/...`
3. Report: "Run log created and staged: `knowledge_vault/05_runs/...`"

The commit-msg hook blocks any `FEAT*` commit without a staged run log.

---

## 14. Development workflow

Rules:

- one FEAT = one clear intent;
- keep changes small and reviewable;
- do not perform opportunistic refactors;
- do not add abstractions for future features;
- do not add dependencies unless justified by MVP needs;
- do not introduce post-MVP features during MVP tasks;
- do not modify unrelated files;
- do not hide failures;
- do not invent project state.

If a task becomes too large, stop and propose a split.

---

## 15. Git workflow

The user controls commits between tasks unless explicitly stated otherwise.

Default behavior for agents:

- do not commit automatically;
- do not push automatically;
- do not create branches automatically;
- do not create PRs automatically;
- do not merge automatically.

Allowed only when explicitly requested: commit, push, branch creation, PR creation, merge.

Before any commit, if requested:

- inspect git status and modified files;
- never use `git add .` blindly;
- stage only relevant files;
- run relevant tests;
- never commit secrets, `.env`, or `tmp/` unless explicitly requested.

Normal reports must state:

- commit: not created
- push: not pushed
- reason if not pushed: not requested

---

## 16. Branch and PR policy

Use branches only if:

- the user explicitly asks;
- the task is parallel, experimental, or risky;
- the task is a large refactor;
- conflict isolation is useful.

Suggested names: `feat/`, `fix/`, `refactor/`, `experiment/`.

Do not create branches without explicit approval.

---

## 17. Testing policy

Run relevant tests for every code change.

For backend changes: `pytest -q`

Coverage target: ≥70% on business modules.

Use one of these labels:

- `passed`
- `failed`
- `not run: reason`

Never claim tests passed if they were not run.

Automated tests must use mocks or dependency injection — no real Ollama instance required.

---

## 18. Security policy

VIVI operates under zero-knowledge and privacy-by-default principles.

Principles: zero-knowledge by design, privacy by default, data minimization, state-of-the-art crypto, auditable.

Rules:

- no external provider by default;
- no secrets in logs;
- no API keys in responses;
- no stack traces in API responses;
- restic encrypted backups from MVP;
- Tailscale for network-level auth at MVP.

Primary threat model:

- T1: opportunistic attacker;
- T6: user themselves (accidental data loss or exposure);
- T7: LLM hallucination and prompt injection.

Accepted residual risks: physical theft (no BitLocker), disk end-of-life, warranty service access, secondary Windows user account.

If `VIVI_API_KEY` is set, protected endpoints must require auth.
If `VIVI_API_KEY` is empty, report `auth_enabled=false` in runtime info.

Never expose: API keys, `.env` values, tokens, credentials, local private paths.

---

## 19. Error policy

API errors should be safe and understandable.

Preferred shape:

- `error.code`
- `error.message`
- `error.recovery_hint`
- `request_id` if available
- `status_code`

Do not return: raw stack traces, secrets, oversized raw provider payloads.

---

## 20. RAG policy

The MVP RAG is lexical and explainable.

Allowed:

- Markdown loading;
- frontmatter parsing;
- title/path/tag/heading/content search;
- simple chunking;
- top-k retrieval;
- visible sources.

Not MVP:

- embeddings;
- vector database;
- reranker;
- hybrid retrieval;
- autonomous vault rewriting.

Every document-based answer must expose sources. If no source found, VIVI must say so.

---

## 21. Session memory policy

MVP memory is simple.

Allowed:

- short session memory;
- session_id;
- user and assistant messages;
- created_at and updated_at;
- inspectable session store;
- deletion endpoint.

Not allowed at MVP:

- agent memory;
- autonomous long-term memory;
- vector memory;
- opaque memory;
- automatic summarization as durable truth.

---

## 22. Documentation policy

README.md should contain: project purpose, installation, launch, tests, MVP status.

The vault contains: product framing, architecture, decisions, backlog, runs if requested.

Avoid duplication. Do not create legacy snapshot files (PROJECT_STATE.md, CHANGELOG_AI.md, NEXT_STEPS.md).

---

## 23. Markdown generation policy

When asked to generate Markdown:

- generate the full content immediately;
- do not ask for confirmation;
- make it directly usable;
- keep structure clean.

If meant for a file, provide it in one complete Markdown block. Do not split unless explicitly requested.

---

## 24. Context management policy

Recommend starting a new conversation when:

- more than 6–8 FEATs have been chained;
- answers become less precise;
- project state becomes hard to summarize.

Standard alert: *"The context is becoming large. Recommendation: start a new conversation with a summarized prompt."*

Provide: compact project-state summary + next FEAT ready to execute. Do not replay full history.

---

## 25. Output minimization policy

After normal tasks, use:

```markdown
## Summary
- Files changed: X
- Tasks impacted: FEAT-XX

## Changes
- file: change

## State
- project_state: updated | no
- backlog: updated | no
- run_log: updated | no
- decision: updated | no

## Tests
- command: passed | failed | not run

## Git
- commit: hash and message | not created
- push: pushed | not pushed
- reason if not pushed: short reason

## Next
- FEAT-XX
```

Do not include long implementation narratives unless requested.

---

## 26. Critical prohibitions

Never:

- treat VIVI as VIVI_IA;
- import the legacy repo wholesale;
- copy legacy code without explicit instruction;
- implement multi-LLM agents at MVP;
- add a complex orchestrator at MVP;
- add runtime skills at MVP;
- add provider registry at MVP;
- add external provider fallback at MVP;
- add vector DB at MVP;
- modify Obsidian source notes automatically;
- auto-commit;
- auto-push;
- create PRs automatically;
- commit `tmp/` unless explicitly requested;
- claim tests passed if not run;
- expose secrets;
- hide a dirty working tree;
- rewrite Git history;
- perform unrelated refactors;
- put business logic in the LLM core;
- hard-code prompts in Python source.

---

## 27. Evolutionary trajectory

For context only — not for implementation now.

- **Phase 2 (post-MVP)**: progressive addition of domains (Memory, Reminders, Agenda, Finance). No architecture change.
- **Phase 3 (if dev capacity)**: multi-model routing — one router core + several specialized LLMs. NOT dialogue between LLMs.
- **Phase 4 (hypothetical)**: true multi-agents only for legitimate long autonomous task use cases.

---

## 28. Final principle

VIVI MVP must stay simple:

- I launch VIVI;
- I open the interface;
- I ask what we're eating tonight;
- VIVI suggests a meal from the recipe catalogue;
- VIVI updates the shopping list;
- VIVI stays local-first.

Everything else comes later.

---

## Appendix A — Legacy VIVI_IA audit policy

When analyzing the legacy VIVI_IA repo:

- do not modify it;
- do not copy files from it;
- do not import code automatically;
- produce an audit report only;
- classify items as KEEP_MVP, KEEP_POST_MVP, ARCHIVE, DELETE, REWRITE, or UNKNOWN.

The legacy may inspire: API patterns, safe errors, session memory, auth, runtime status, tests, markdown chunking.

The legacy must not reintroduce: multi-agent orchestration, runtime skills, provider registry, Open WebUI-first design, vector complexity, old Obsidian structure.
