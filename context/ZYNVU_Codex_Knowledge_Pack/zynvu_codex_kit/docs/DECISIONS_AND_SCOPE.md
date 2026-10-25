# Decisions, invariants and provenance

## Final product identity
- Product name **ZYNVU** (also referred to phonetically as Zinvu). Short, international, five letters. **Name/domain/trademark availability not legally verified**; do not claim exclusivity.
- Public, universal open-source repository; optional Apache-2.0 proposal subject to final license decision. Do not introduce mandatory subscriptions or paywalls for core advisor/SDK.
- Works standalone as an Architecture Advisor, or embedded into **any** developer project via CLI/SDK/local API. VOKI is one illustrative consumer, not a privileged or hard-coded integration.
- Phase 1 is **recommendation only**: detect hardware, interpret needs, recommend combinations, estimate feasibility, output report and versioned JSON manifest. **No model download/install/run/agent execution** in this phase.
- Phase 2 adds agent runtime, installation/provisioning, model routing, connectors, execution, monitoring, local learning, and optional fine-tuning pipelines.
- Recommendations must be grounded in **actual machine diagnostics** and explicit preferences. Never assume the user's GTX 1650 or any specific machine.

## Essential capabilities
1. Conversation/text generation
2. Programming/code assistance
3. Vision/screen interpretation
4. Speech transcription and voice commands; optional TTS
5. MCP tools and third-party apps (GitHub, Slack, Linear, Render, Vercel, etc.)
6. Local folder-based memory, RAG, documents and learned skills
7. Optional Jev/Laya decision/routing models (verify suitability and current repository APIs)
8. UI automation executors: API/MCP, Playwright, Selenium, PyAutoGUI, native OS, optional USB HID
9. User-described goals -> requirements -> architecture blueprint
10. Optional LoRA/QLoRA if supported; distinguish from memory and RAG.

## ZYNVU vs VOKI — non-negotiable distinction
- Standalone ZYNVU **may include** Playwright, Selenium, PyAutoGUI, native OS automation, API/MCP and optional hardware HID executors.
- **VOKI** is a separate project; its interface interaction (mouse, keyboard, dragging/drawing) is **exclusively physical USB HID hardware**. When consuming ZYNVU recommendations, VOKI declares an execution policy denying Playwright/Selenium/PyAutoGUI/native software UI automation. Enforce in code, not prompt only.
- Ordinary USB HID mouse/keyboard does **not** provide screenshots. VOKI must have a separate, explicit screenshot acquisition channel; do not claim it exists automatically.
- VOKI Phase 1 is hardware + MCP, one-time Stripe purchase, individual device-bound firmware-enforced license where feasible, open-source software; no Pro subscription. Its Phase 2 consumes ZYNVU as an external universal advisor/runtime capability, without making ZYNVU responsible for VOKI licensing.
- API/MCP access in VOKI may be allowed for non-UI data interactions subject to the VOKI policy; **UI actions** must remain physical HID.

## Commercial decisions
- GitHub README/Release as discovery and free-download funnel.
- Paid **services** (assisted setup, configured agent, B2B integrations/enterprise), not paywall on core source.
- Proposed test prices (BRL): setup 497 one-time; configured agent 2,490; developer integration from 7,900; enterprise from 19,900. Optional support 99/490/1,490 per month depending scope. These are hypotheses, **not validated market prices**.
- Checkout through Asaas (Brazil, Pix/card/boleto) and/or Stripe (international). Render backend, PostgreSQL, Resend emails. Webhooks authoritative, signed/secret validated, idempotent, async processing, audit log.
- No GitHub repo exists/published yet as far as this chat established; no live checkout configured.

## Implementation caution
- Example model families, runtimes, specs and repository claims in the discussion are **candidates**, not validated current compatibilities. Verify source licenses, versions, context, quantization, hardware requirements and supported tools before adding to production catalog.
- Do not imply the product exists or features are implemented; this pack is a specification for Codex to build.
