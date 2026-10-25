# Memory, skills and fine-tuning

## Per-agent local layout
```text
ZYNVU/agents/<agent-id>/
  config/agent.yaml, models.json
  memory/profile.json, facts.db, episodes.db, vectors.db
  knowledge/documents/, indexes/
  skills/learned/, validated/
  training/examples/, datasets/, adapters/
  executions/logs/, screenshots/
  metrics/performance.db
```

Memory tiers: working context; episodic (tasks/outcomes); semantic (facts/preferences); documentary RAG; procedural skills; visual evidence; operational metrics. SQLite with FTS/vector extension as appropriate; files for originals and reproducible artifacts. Do not assume vector search is necessary for every workload.

## Learning loop
Execute authorized action -> collect minimal evidence -> verify objective -> classify error -> safe retry if appropriate -> extract reusable skill -> store versioned skill with prerequisites, confidence and tests -> retrieve/adapt for future tasks. Require confirmations for risky writes, messages, deployments, deletions. Audit and rollback where possible.

## Fine-tuning decision policy
Recommend prompt refinement, RAG and procedural skills first. Offer LoRA/QLoRA only if training data quality, license, privacy and GPU/RAM constraints justify it. Explain that model inference fitting does not imply training fitting. Full fine-tuning is generally out of scope for consumer PCs. Training on VM/cloud requires explicit opt-in and data governance. Measure improvement against holdout evals before adopting adapters.
