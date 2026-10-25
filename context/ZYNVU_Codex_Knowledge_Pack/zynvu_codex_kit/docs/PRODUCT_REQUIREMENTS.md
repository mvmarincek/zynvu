# Product requirements

## Users and modes
- Nontechnical local user: describes in natural language what an agent should do; gets intelligible report and recommended architecture, tradeoffs, installation path.
- Developer: uses CLI, JSON contract and SDK to integrate advisor into an existing app.
- Organization: plans on-prem/VM/hybrid agent deployment with policies and connector requirements.
- Modes: **Advisor** (Phase 1), **Embedded SDK** (Phase 1), **Agent Runtime** (Phase 2).

## Onboarding / inputs
Natural-language intent; selectable capabilities; local-only or explicitly authorized hybrid; target OS; RAM/VRAM limits; priority (quality, speed, privacy, cost, energy); concurrency vs sequential model loading; required apps/connectors; execution mechanisms allowed/denied; autonomy and approval policy; memory retention and fine-tuning interest.

## Hardware profiler
Collect OS/architecture, CPU/cores, physical/available RAM, GPU vendor/model, discrete VRAM or shared memory, accelerators and drivers, disk available, runtime compatibility, optional battery/power constraints. Work on Windows first; Linux/macOS later. Virtual machines and CPU-only machines supported. Explicit confidence/provenance and unknown values. No hidden exfiltration; local by default. Never double-count unified/shared memory.

## Advisor pipeline
1. Parse user goal into a versioned structured requirements object; user can review/edit.
2. Gather real hardware facts and runtime availability.
3. Load local/offline versioned catalog, optionally update with consent.
4. Deterministic hard-filter by OS/ISA, memory, drivers, runtime, license, privacy, tool-calling requirements.
5. Build **combinations** of compatible chat/code/vision/ASR/embedding/decision models, connectors and executors, not just top LLM.
6. Estimate peak RAM/VRAM including weights, quantization, KV cache, context, runtime overhead, concurrent agents, OS safety margin. Distinguish sequential unload/load and concurrent use.
7. Rank by suitability, quality, latency, memory pressure, cost, energy and risk; empirical benchmarks take precedence over guesses.
8. Return balanced / fastest / highest quality alternatives and honest no-fit/degraded-mode outcomes.
9. Export report and versioned JSON Blueprint, including caveats and provenance.

## Model catalog candidates (verify, do not hardcode as truth)
- Text: Llama 3.2 1B; Qwen3 4B/8B and smaller variants where available.
- Code: Qwen2.5-Coder 1.5B/3B/7B.
- Vision: SmolVLM2 500M, Moondream, Qwen2.5-VL 7B.
- ASR: Whisper tiny/base/small; Parakeet variants where compatible.
- Embeddings: all-MiniLM-L6-v2, BGE-small/base; optional rerankers.
- Decisions: deterministic rules first, optional Laya/Jev structured decision engine; test decision accuracy/calibration.
- Runtimes: Ollama, llama.cpp, whisper.cpp and other verified supported runtimes.
- llmfit as potential external hardware/model fit reference or integration, subject to compatibility and license verification.

## Execution routing (Phase 2)
Priority is contextual, not rigid: API/MCP for structured supported services; Playwright/Selenium for browser UI; native OS or PyAutoGUI for desktop UI; vision-driven GUI where needed; USB HID where hardware-required. Use least privilege and validation. Connector tools dynamically exposed to avoid giant context. Explicit capability/policy gate before every action; no silent fallback to forbidden executor.

## Third-party connectors
Initial targets: GitHub, Slack, Linear, Render, Vercel, custom MCP; extensible to Google Drive/Gmail, Notion, PostgreSQL, arbitrary OpenAPI/REST. Each connector declares transport, OAuth/API key, read/write scopes, internet needs, schemas, rate limits, health checks, and action risk. Store secrets in OS secure storage or secret manager, never Blueprint/repo/logs. Offline degradation must be explained.

## Local agent memory and learning
One local root folder per agent; configuration, documents, SQLite episodic/semantic facts, vector indexes, procedural skills, screenshots and logs, training examples, model adapters. Short-term state distinct from persistent memory. Retrieval with citations/provenance, retention and deletion controls, encryption option, backup/migration, deduplication, secrets scrubbing. Learn reusable skills from validated actions, not brittle screen coordinates. Self-check/repair within authorization; human confirmation for destructive/external actions. Fine-tuning is optional and never confused with memory/RAG; local training only if resources and data justify it; remote training only with explicit permission.

## Phase 2 monitoring
Model tokens/sec, first-token latency, tool latency/success/error, CPU/RAM/GPU/VRAM, storage growth, costs, per-task trace, validation success, audit and feedback; no sensitive data leakage in telemetry.

## UX and distribution
Tauri 2 + React/TypeScript desktop candidate, Rust hardware detection/shared core, SQLite; Windows installer first; CLI and local API. These are proposals, not fixed requirements if Codex identifies a better well-justified implementation. PT-BR UI with internationalization-ready structure. Offline-first. Accessible and transparent about estimates.

## Non-goals
No guarantee that all capabilities fit every PC; no unsupported hardware claims; no automatic unsafe execution; no required cloud account; no VOKI-specific hardcoding; no checkout inside GitHub itself.
