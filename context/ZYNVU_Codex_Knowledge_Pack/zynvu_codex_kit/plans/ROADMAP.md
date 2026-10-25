# Roadmap and implementation order

## Milestone 0 — Repo foundation
README, license decision, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, architecture docs, monorepo setup, CI lint/test/typecheck, config and fixture schemas, no real secrets. Name availability check separate.

## Milestone 1 — Advisor MVP (highest priority)
CLI with simulated and actual hardware detection (Windows first), typed requirements, offline catalog fixtures, deterministic compatibility filter, resource estimator, three ranked combinations, no-fit explanation, Blueprint JSON schema and human-readable report. Tests for 4/8/16/32GB RAM, CPU-only, 4/8/16GB GPU, shared memory, VM. Do **not** install models.

## Milestone 2 — Desktop UX + embedded API
Tauri/React frontend, user goal intake, capability selection, privacy policy, model comparison, Blueprint export. Stable local SDK/CLI and integration guide. Hardware permissions and error messages.

## Milestone 3 — Connector catalog + commerce
Connector metadata/requirements, API/MCP options and tool-calling fit, dynamic catalog. README service CTAs; independent Render/Postgres/Resend commerce backend; Asaas sandbox then Stripe sandbox; secure webhooks and email fulfillment; production gated by credentials, legal review and end-to-end tests.

## Milestone 4 — Agent Runtime (Phase 2)
Optional model installation/provisioning, execution router with strict policy gates, memory SQLite/RAG, connectors, Playwright/Selenium/PyAutoGUI/native/HID optional executors, tool result validation, monitoring. Local-only and hybrid modes with explicit consent.

## Milestone 5 — Learning and advanced customization
Validated procedural skills, feedback loops, fine-tuning suitability evaluator, LoRA/QLoRA optional integration with measurable evaluation, safe backup/migration. VOKI can integrate through generic SDK and HID-only execution policy.

## Acceptance criteria
- No hardcoded user's hardware.
- CPU-only and offline modes work.
- Recommendations include reasons, constraints, estimates, uncertainty and alternatives.
- VOKI HID-only policy cannot be bypassed by executor fallback.
- Secret values never exported to Blueprint or committed.
- Payment is not necessary for free advisor/SDK use.
- No webhook replay can create duplicate fulfillment or double charge.
- No unimplemented feature represented as complete.
