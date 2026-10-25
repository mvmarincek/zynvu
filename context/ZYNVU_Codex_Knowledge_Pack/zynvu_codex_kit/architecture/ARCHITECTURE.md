# Technical architecture

```text
User goal + selected capabilities + policies
                 |
        Requirements Analyzer
                 |
Hardware Profiler + Runtime Checker ---- Catalog (versioned/offline)
                 |                         |
                 +-- Hard Compatibility Filter
                              |
                   Combination Generator
                              |
                Resource / Quality Estimator
                              |
                Deterministic Ranker (+ optional Laya)
                              |
               Architecture Blueprint JSON + report
                              |
          +-------------------+---------------------+
          |                                         |
  Standalone Advisor/CLI                      Consumer SDK/API
                                                    |
                                       Optional Agent Runtime (Phase 2)
                                                    |
                      +-----------------------------+------------------+
                      |                 |                |             |
                 Local Memory      Connectors       Executors     Monitoring
                 SQLite/RAG        API/MCP         Web/OS/HID     Feedback
```

## Packages / boundaries
- `apps/desktop`: GUI; no direct secrets.
- `apps/cli`: machine-readable outputs, exit codes, scripting.
- `packages/core`: requirements, model catalog types, hard filtering, ranking, estimates, Blueprint contract.
- `packages/hardware`: OS-specific detection; mock profiles for tests.
- `packages/connectors`: metadata/registry in Phase 1; authenticated runtime adapters in Phase 2.
- `packages/executors`: policy-aware executor interfaces; implementations Phase 2.
- `packages/memory`: local agent workspace and RAG strategy/implementation.
- `packages/learning`: skills, feedback, optional training.
- `services/commerce`: independent paid-service ordering backend; never required to use core ZYNVU.
- `docs/`: installation, architecture, privacy, pricing, payments, operations.

## Stable contracts
- `Requirements`: goals, capabilities, hard restrictions, privacy, apps, learning choices.
- `HardwareProfile`: facts with source and confidence, timestamp, unknown fields.
- `CatalogEntry`: model/runtime/connector license, versions, verified benchmarks, hardware and tool capability requirements.
- `Recommendation`: model assignments, executor options, memory topology, resource budget, alternatives, reasons.
- `Blueprint`: versioned export and provenance, safe to share after secret scrubbing.

## Execution policy examples
General: `allowed: [api_mcp, playwright, selenium, pyautogui, native_os, hardware_hid]` filtered by platform and permissions.
VOKI consumer: `allowed_interface_executors: [hardware_hid]`, `denied_interface_executors: [playwright, selenium, pyautogui, native_os]`. This policy is enforced in runtime before invoking an executor; it is not a ZYNVU default.

## Data architecture
Local agent root, e.g. `~/ZYNVU/agents/<agent-id>/` with config, memory SQLite, knowledge files/indexes, skills learned/validated, training examples/adapters, execution logs/screenshots, metrics. Make paths configurable and safe on Windows/Linux/macOS. Keep embeddings/index metadata versioned and rebuildable. Never put API tokens in these folders by default.

## Resource estimation
Peak resident memory = model weights + KV cache + inference buffers + other simultaneously loaded models + tool/runtime overhead + OS reserve. Account for unified memory; show assumptions, confidence, and degradation plan. For sequential model swaps, compute per-stage peak and switching cost. Benchmark when Phase 2 runtime exists.
