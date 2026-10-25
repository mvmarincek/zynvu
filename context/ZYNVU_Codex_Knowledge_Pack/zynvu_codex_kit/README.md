# ZYNVU — AI Architecture Advisor & Runtime SDK

**Knowledge pack and Codex implementation instructions — 2026-10-25.**

ZYNVU is a universal, open-source, hardware-aware AI architecture advisor. Users describe the agent they want, ZYNVU inspects their actual PC/notebook/VM, recommends a compatible combination of LLM, coding, vision, voice, RAG/memory, decision models, tools, connectors and executors, and exports a versioned architecture blueprint. Future phases can provision and run the resulting agent. It is **not** built for VOKI; VOKI is just one optional consumer.

## Read first
1. `CODEX_MASTER_PROMPT.md` — single master prompt to paste into Codex.
2. `docs/DECISIONS_AND_SCOPE.md` — authoritative decisions and scope boundaries.
3. `docs/PRODUCT_REQUIREMENTS.md` — full product spec.
4. `architecture/ARCHITECTURE.md` — components and data flow.
5. `plans/ROADMAP.md` — staged delivery and acceptance gates.
6. `commerce/COMMERCE_SPEC.md` — complete GitHub-to-paid-service commercial workflow.
7. `schemas/blueprint.schema.json` and `examples/*.json` — machine-readable contracts.

This pack captures the **substantive decisions and requirements discussed in the chat**, reorganized as implementation-ready specifications. It is not a verbatim chat transcript, and contains no previously implemented source code. Proposed technical choices/prices are labeled as such. No actual hardware has been diagnosed; no real checkout, domain, brand clearance or GitHub publication has occurred.

**Language:** Product UI and customer-facing sales pages default to PT-BR; source code, schema keys, developer docs and API naming may use English.
