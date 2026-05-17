# AGENTS.md — VIVI Project Instructions

## 1. Project identity

You are working on the project VIVI.

VIVI is a new clean project, separate from the legacy VIVI_IA repository.

VIVI_IA is considered:

- a laboratory;
- a legacy archive;
- a source of inspiration;
- a source for selective audit only.

Do not treat VIVI_IA as the active product.

Do not copy legacy code from VIVI_IA unless explicitly requested.

The active product is VIVI.

---

## 2. Product vision

VIVI is a local personal AI assistant.

Its first and most important function is simple:

> I talk to VIVI, VIVI answers.

The MVP must remain strict:

- dedicated simple web interface;
- local chat via LM Studio;
- Obsidian RAG;
- visible sources;
- runtime status;
- simple session memory;
- simple security;
- local-first behavior.

Everything else is post-MVP unless explicitly approved.

---

## 3. Source of truth

The main product source of truth is:

- knowledge_vault/00_product/VIVI_MVP_CADRAGE_v0.1.md

The backend MVP technical source of truth is:

- knowledge_vault/02_architecture/VIVI_BACKEND_MVP_SPEC_v0.1.md

Before any implementation task, read:

- AGENTS.md
- README.md
- the relevant product or architecture note
- tmp/codex_last_report.md if present

If the user request conflicts with the MVP scope, report the conflict before implementing.

---

## 4. Current repo policy

This repository is a clean VIVI repo.

It is not a fork cleanup repo.

It is not the legacy VIVI_IA repo.

The current strategy is:

- build a clean MVP;
- audit legacy only when useful;
- import concepts selectively;
- avoid legacy complexity.

Do not import the old project wholesale.

---

## 5. MVP priorities

Priority order:

1. local discussion assistant;
2. dedicated simple web interface;
3. LM Studio as local provider;
4. local chat;
5. Obsidian RAG;
6. visible sources;
7. runtime status;
8. simple security;
9. simple session memory.

Control question before every feature:

> Is this required to open VIVI, talk to LM Studio, query Obsidian, see sources, and get a reliable answer?

If no, classify it as post-MVP, backlog, archive, or reject it.

---

## 6. Explicitly outside MVP

Do not implement in the MVP:

- specialized agents;
- DEV agent;
- PM agent;
- ARCH agent;
- QA agent;
- nutrition agent;
- finance agent;
- home assistant agent;
- auto-improvement agent;
- automatic skill creation;
- Codex calls from VIVI;
- fallback to external providers;
- OpenAI external provider;
- Mammouth external provider;
- Ollama as primary provider;
- provider registry;
- multi-provider routing;
- vector database requirement;
- embeddings requirement;
- complex orchestrator;
- runtime skills;
- advanced cockpit UI;
- mobile app;
- VPN;
- multi-user support;
- automatic modification of source Obsidian notes.

These topics may be documented as post-MVP, but must not complicate the MVP implementation.

---

## 7. LM Studio provider rule

LM Studio is the MVP provider.

Allowed:

- LM Studio local OpenAI-compatible API;
- configurable base URL;
- configurable model;
- healthcheck;
- chat completion;
- safe provider errors;
- tests using mocks.

Default values:

- VIVI_LMSTUDIO_BASE_URL=<http://localhost:1234/v1>
- VIVI_LLM_TIMEOUT_SECONDS=60

Do not add:

- ProviderRegistry;
- multi-provider fallback;
- Ollama implementation;
- OpenAI implementation;
- Mammouth implementation;
- benchmark routing;
- automatic model selection.

The code may be kept compatible with future providers, but must not implement them now.

---

## 8. Backend MVP architecture

The backend should stay simple.

Expected modules may include:

- app/api/
- app/llm/
- app/knowledge/
- app/sessions/
- app/runtime/
- tests/
- scripts/
- data/runtime/

Core endpoints for the MVP:

- GET /health
- GET /runtime/info
- POST /chat
- GET /sessions
- GET /sessions/{session_id}
- DELETE /sessions/{session_id}
- GET /knowledge/search

Implement them progressively by FEAT.

Do not add an orchestrator layer until the basic chat + RAG MVP is validated.

---

## 9. Obsidian vault policy

The Obsidian vault is located at:

- knowledge_vault/

Central rule:

> AI-generated writes go only to generated/, runtime/, or inbox/, never directly into source notes.

Recommended zones:

- 00_product/ : product framing
- 01_user_docs/ : user documentation
- 02_architecture/ : validated architecture
- 03_decisions/ : project decisions
- 04_backlog/ : backlog and ideas
- 05_runs/ : run logs if explicitly requested
- 90_generated/ : generated content
- 91_runtime/ : runtime data, indexes, logs
- 92_inbox/ : proposals to validate
- 99_archive/ : archives

Do not automatically modify:

- product framing notes;
- validated architecture;
- decision notes;
- human documentation;
- README.md;
- source notes.

For normal Codex implementation tasks, write the execution report to tmp/.

Only update Obsidian project memory when explicitly requested or when the task is specifically documentary.

---

## 10. Run history policy

The canonical run history lives in `knowledge_vault/05_runs/`.

After each significant FEAT or improvement, create a note:

- filename: `YYYY-MM-DD_FEAT-short-name.md`
- frontmatter: `doc_type: run`, `llm_index: false`, `llm_priority: low`
- content: résumé, fichiers modifiés, validation (tests), résultat, note méthode si pertinent

`llm_index: false` is the default for run logs — execution detail must not pollute RAG responses. Set `llm_index: true` only if the run contains a decision worth surfacing in retrieval.

`tmp/` is scratch space only — transient, never committed, overwritten freely. It is not the historical record.

---

## 11. Development workflow

The workflow must remain controlled.

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

## 12. Git workflow

The user currently controls commits between tasks unless explicitly stated otherwise.

Default behavior for Codex:

- do not commit automatically;
- do not push automatically;
- do not create branches automatically;
- do not create PRs automatically;
- do not merge automatically.

Allowed only when explicitly requested:

- commit;
- push;
- branch creation;
- PR creation;
- merge.

Before any commit, if requested:

- inspect git status;
- inspect modified files;
- never use git add . blindly;
- stage only relevant files;
- run relevant tests;
- never commit secrets;
- never commit .env;
- never commit tmp/ unless explicitly requested.

Normal reports must state:

- commit: not created
- push: not pushed
- reason if not pushed: not requested

This replaces the old VIVI_IA main-first auto-push policy.

---

## 13. Branch and PR policy

Branches and PRs are allowed for parallel or risky work, but not automatic.

Use branches only if:

- the user explicitly asks;
- the task is parallel;
- the task is experimental;
- the task is risky;
- the task is a large refactor;
- conflict isolation is useful.

Suggested branch names:

- feat/short-name
- fix/short-name
- refactor/short-name
- experiment/short-name

Do not create branches without explicit approval.

---

## 14. Testing policy

Run relevant tests for every code change.

For backend changes, prefer:

- pytest -q

For focused changes, a smaller subset is allowed first, but the final report must say exactly what was run.

Never claim tests passed if they were not run.

Use one of these labels:

- passed
- failed
- not run: reason

Tests must not require a real LM Studio instance unless the task is explicitly a manual smoke test.

Automated tests should use mocks, fake clients, or dependency injection.

---

## 15. Security policy

VIVI is local-first, but must not be careless.

Rules:

- no external provider by default;
- no external fallback by default;
- no secrets in logs;
- no API keys in responses;
- no stack traces in API responses;
- safe errors only;
- simple local auth must be supported;
- if VIVI_API_KEY is set, protected endpoints must require auth;
- if VIVI_API_KEY is empty, report auth_enabled=false in runtime info.

Never expose:

- VIVI_API_KEY;
- .env values;
- tokens;
- credentials;
- local private paths beyond what is useful and safe.

---

## 16. Error policy

API errors should be safe and understandable.

Preferred shape:

- error.code
- error.message
- error.recovery_hint
- request_id if available
- status_code

Do not return:

- raw stack traces;
- secrets;
- oversized raw provider payloads;
- confusing internal exceptions.

---

## 17. RAG policy

The MVP RAG is lexical and explainable.

Allowed MVP behavior:

- Markdown loading;
- frontmatter parsing;
- title/path/tag/heading/content search;
- simple chunking;
- top-k retrieval;
- visible sources;
- /knowledge/search endpoint.

Not MVP:

- embeddings requirement;
- vector database;
- reranker;
- complex hybrid retrieval;
- autonomous vault rewriting.

Every document-based answer must eventually expose sources.

If no source is found, VIVI must say so clearly.

---

## 18. Session memory policy

MVP memory is simple.

Allowed:

- short session memory;
- session_id;
- user and assistant messages;
- created_at and updated_at;
- inspectable session store;
- deletion endpoint.

Not allowed in MVP:

- agent memory;
- autonomous long-term memory;
- vector memory;
- opaque memory;
- automatic summarization as durable truth.

---

## 19. Legacy VIVI_IA audit policy

When analyzing the legacy VIVI_IA repo:

- do not modify it;
- do not copy files from it;
- do not import code automatically;
- produce an audit report only;
- classify items as KEEP_MVP, KEEP_POST_MVP, ARCHIVE, DELETE, REWRITE, or UNKNOWN.

The legacy may inspire:

- API patterns;
- safe errors;
- session memory;
- auth;
- runtime status;
- tests;
- markdown chunking.

The legacy must not reintroduce:

- multi-agent orchestration;
- runtime skills;
- provider registry;
- Open WebUI-first design;
- vector complexity;
- old Obsidian structure;
- old project-state conventions.

---

## 20. Documentation policy

Keep documentation short and useful.

README.md should contain:

- project purpose;
- basic installation;
- basic launch;
- basic tests;
- current MVP status.

The vault contains:

- product framing;
- architecture;
- decisions;
- backlog;
- runs if requested;
- generated/inbox/archive content.

Avoid duplication.

Do not update root legacy snapshots such as:

- PROJECT_STATE.md
- CHANGELOG_AI.md
- NEXT_STEPS.md

These files should not exist in the new repo unless explicitly introduced for a clear reason.

---

## 21. Markdown generation policy

When asked to generate Markdown content:

- generate the full content immediately;
- do not ask for confirmation;
- make it directly usable;
- avoid unnecessary escaping;
- avoid placeholders unless unavoidable;
- keep structure clean.

If the Markdown is meant to be copied into a file, provide it in one complete Markdown block.

Do not split a file into fragments unless explicitly requested.

---

## 22. Context management policy

Monitor context size and project drift.

Recommend starting a new conversation when:

- more than 6 to 8 FEATs have been chained;
- the scope exceeds a coherent functional block;
- repeated state reminders are needed;
- answers become less precise;
- project state becomes hard to summarize.

Standard alert:

The context is becoming large. Recommendation: start a new conversation with a summarized prompt to reset the context.

Then provide:

- a compact project-state summary;
- the next FEAT ready to execute.

Do not replay full history.

Keep only critical invariants.

---

## 23. Output minimization policy

Default final output should be concise.

After normal Codex tasks, use:

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

Do not include long implementation narratives unless requested.

---

## 24. Critical prohibitions

Never:

- treat VIVI as VIVI_IA;
- import the legacy repo wholesale;
- copy legacy code without explicit instruction;
- add agents during the MVP;
- add a complex orchestrator during the MVP;
- add runtime skills during the MVP;
- add provider registry during the MVP;
- add external provider fallback during the MVP;
- add vector DB during the MVP;
- modify Obsidian source notes automatically;
- auto-commit;
- auto-push;
- create PRs automatically;
- commit tmp/ unless explicitly requested;
- claim tests passed if not run;
- expose secrets;
- hide a dirty working tree;
- rewrite Git history;
- perform unrelated refactors.

---

## 25. Final principle

VIVI MVP must stay simple:

- I launch VIVI;
- I open the interface;
- I talk to a local LM Studio model;
- VIVI can query Obsidian;
- VIVI shows its sources;
- VIVI answers clearly;
- VIVI stays local-first.

Everything else comes later.
