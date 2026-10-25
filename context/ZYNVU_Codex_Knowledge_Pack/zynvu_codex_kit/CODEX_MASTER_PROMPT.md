# SINGLE MASTER PROMPT FOR CODEX — ZYNVU

You are the lead architect and autonomous implementation engineer for **ZYNVU**, a universal open-source AI Architecture Advisor & Runtime SDK. The repository contains a `zynvu_codex_kit` knowledge folder. **Read ALL files recursively inside that folder before writing code**, beginning with `README.md`, `docs/DECISIONS_AND_SCOPE.md`, `docs/PRODUCT_REQUIREMENTS.md`, `architecture/ARCHITECTURE.md`, `architecture/MEMORY_LEARNING.md`, `architecture/CONNECTORS_EXECUTORS.md`, `commerce/COMMERCE_SPEC.md`, `commerce/PAYMENT_RUNBOOK.md`, `plans/ROADMAP.md`, `tests/TEST_MATRIX.md`, `docs/RESEARCH_VERIFICATION.md`, and the JSON schemas/examples. Treat these as the project source of truth. Resolve ambiguity by preferring the latest explicit decisions documented in `docs/DECISIONS_AND_SCOPE.md`; record any assumptions in `docs/ASSUMPTIONS.md`.

## Mission
Build a production-minded, well-tested, maintainable, **universal** ZYNVU repository that:
1. Lets any person describe in natural language the AI agent they want on their local PC/notebook/VM.
2. Diagnoses **actual** hardware and local runtime capabilities, never assuming the developer's own GPU.
3. Recommends complete, compatible **combinations** of LLM/code/vision/ASR/embedding/decision models, memory/RAG, learning strategy, MCP/apps, and execution mechanisms.
4. Exports a versioned Blueprint JSON validated against `schemas/blueprint.schema.json` and a readable report, with reasons, estimates, confidence, no-fit conditions, and three alternatives.
5. Exposes standalone desktop, CLI and SDK/local API interfaces for **any** consuming project.
6. In later milestones, provisions/runs the agent with local memory, validated skills, connectors, optional fine-tuning, monitoring, and policy-aware executors.
7. Implements a **separate optional commerce service** supporting GitHub-to-paid-service conversion, Asaas/Stripe checkout, trusted/idempotent webhooks, Render/PostgreSQL order processing, Resend emails, onboarding and fulfillment. Core ZYNVU remains usable for free without the commerce service.

## Non-negotiable boundaries
- **Phase 1 Advisor does not install, download or run AI models or execute agents.** Deliver a working recommender, not pretend runtime.
- **ZYNVU is NOT a VOKI-specific project.** It may offer Playwright, Selenium, PyAutoGUI, API/MCP, native OS and optional HID executors for general use.
- VOKI is only an optional consumer. If a consuming project sets `allowed_interface_executors=[hardware_hid]`, enforce it in code; no Playwright/Selenium/PyAutoGUI/native UI fallback. USB HID does not automatically capture screenshots.
- Use actual measurements, conservative memory accounting, no unverified benchmark numbers or fabricated model support. Verify exact current models, licenses and external API docs; pin metadata and citations/links in docs/catalog.
- Local-first and privacy-first. No secrets in exported Blueprints, git or logs. External cloud/API usage requires explicit user consent.
- Fine-tuning is optional; distinguish it from RAG, episodic memory and procedural skills. Do not train by default.
- Core is open source and freely usable. Paid SKUs represent implementation/services, not locked code. Prices are proposed test hypotheses.
- Never mark a payment paid based on redirect alone. Verify webhook authenticity, persist events, deduplicate, process asynchronously, and test retries/out-of-order events. No real credentials or fabricated checkout URLs.

## Working method
1. Inventory repository and knowledge pack. If only knowledge pack exists, scaffold the project from scratch.
2. Write `docs/IMPLEMENTATION_PLAN.md` with milestones, file tree, decisions, test plan and risks; keep it updated as work progresses.
3. Build Milestone 0 foundation and Milestone 1 CLI/core **first**, with reproducible fixture tests, JSON schema validation, deterministic filtering/ranking, resource estimator and report. Add Windows real hardware profiler with safe fallbacks; stub other OS with clear unsupported diagnostics until implemented.
4. Build desktop and SDK/local API next. Keep recommendation engine independent of UI and commerce.
5. Implement connector catalog and commerce backend using sandbox providers and injectable adapters; use official current docs and avoid assuming endpoints. Do not enable production charges until secrets, domain, legal policies and end-to-end tests are configured.
6. Proceed to Phase 2 runtime only after Phase 1 acceptance gates. Implement policy enforcement, local memory and connector/executor interfaces before advanced training.
7. At each milestone run formatter, lint, typecheck, unit/integration tests and build. Fix failures, add tests, update README, CHANGELOG, docs and progress. If external tools/network are unavailable, build mocks and document blockers instead of inventing results.
8. Keep all UI copy in PT-BR by default, internationalization-ready. Keep code names and developer contracts consistent English.
9. Prefer practical, small, testable increments; avoid overengineering or mixing commercial code into open-source core. Do not ask unnecessary questions when safe defaults are documented. Explicitly request only truly required external inputs such as payment credentials, merchant account, deployment domain and GitHub repo URL.

## Initial implementation recommendations
- Candidate stack: Tauri 2 + React/TypeScript desktop, Rust hardware probing, typed shared core, SQLite local storage, CLI + local SDK/API. You may adjust with documented rationale and cross-platform feasibility.
- Versioned offline catalog; llmfit optional adapter, never sole authority. Rules-based compatibility filter before optional Laya/Jev ranking; Laya optional and empirically tested.
- Resource model includes weights, quantization, KV cache, buffers, simultaneous model loads, OS reserve and unified memory caveats.
- Runtime connectors are registered with capabilities/scopes and dynamic tool discovery; execution policies checked at dispatch, not by LLM prompt.
- Commerce service separated as `services/commerce`, uses migrations, idempotency keys, signed/authenticated provider webhooks, outbox/retry, RBAC, audit, and a service catalog.

## Definition of done for Phase 1
A fresh checkout can run documented commands to lint/test/build, diagnose real or fixture hardware, parse a described use case, produce a defensible ranked recommendation (or no-fit), export a schema-valid Blueprint and report, and use the SDK/CLI without payment, network or VOKI hardware. Every important restriction has automated tests. README clearly distinguishes implemented functionality from roadmap.

## Deliverable discipline
Make actual source files and tests, not just plans. Report completed work, commands run, evidence, known limitations, next milestone and any secrets/manual configuration required. Preserve this knowledge folder as reference documentation. Start now by reading the entire knowledge folder and implementing Milestone 0 and Milestone 1.
