"""Deterministic architecture planner; contains no model execution/network code."""

import itertools
import math
from typing import Any

from zynvu.catalog import load_catalog
from zynvu.contracts import HardwareProfile, Requirements
from zynvu.export import scrub, validate_blueprint
from zynvu.policy import allowed_executors

GIB = 1024**3
PROFILES = ("balanced", "fastest", "highest_quality")
MODEL_ROLES = {"conversation", "coding", "vision", "asr", "tts"}


def model_memory(model: dict[str, Any], context: int) -> dict[str, float]:
    weights = model["weight_bytes"] / GIB
    if model.get("memory_estimator") == "published_asr":
        # Upstream MB converted as decimal; margin and input reserve are assumptions.
        total = max(weights, model["published_memory_mb"] * 1_000_000 / GIB) * 1.5 + 0.25
        return {
            "weights_gb": weights,
            "kv_gb": 0.0,
            "buffers_gb": total - weights,
            "total_gb": total,
        }
    kv = 2 * model["layers"] * model["kv_heads"] * model["head_dim"] * context * 2 / GIB
    buffers = max(0.25, weights * 0.20)
    return {
        "weights_gb": weights,
        "kv_gb": kv,
        "buffers_gb": buffers,
        "total_gb": weights + kv + buffers,
    }


def estimate(
    models: list[dict[str, Any]], hardware: HardwareProfile, requirements: Requirements
) -> dict[str, Any]:
    # One load per unique model; separate KV per agent. Weights shared within a process.
    unique = {model["id"]: model for model in models}
    components = {
        key: model_memory(model, requirements.context_tokens) for key, model in unique.items()
    }
    stages = [
        c["weights_gb"]
        + c["buffers_gb"]
        * (requirements.agents if unique[key].get("memory_estimator") == "published_asr" else 1)
        + c["kv_gb"] * requirements.agents
        for key, c in components.items()
    ]
    model_peak = sum(stages) if requirements.concurrent else max(stages, default=0)
    overhead = 0.5 + (0.25 if "memory" in requirements.capabilities else 0)
    reserve = max(2.0, hardware.ram_gb * 0.20)
    workload = model_peak + overhead
    # Available memory already excludes current allocations; leave an additional 0.5 GiB margin.
    budget = max(0.0, hardware.ram_gb - reserve)
    if hardware.available_ram_gb is not None:
        budget = min(budget, max(0.0, hardware.available_ram_gb - 0.5))
    disk = sum(model["weight_bytes"] / GIB for model in unique.values()) * 1.1 + 0.5
    return {
        "peak_ram_gb": round(workload + reserve, 3),
        "workload_ram_gb": round(workload, 3),
        "os_reserve_gb": round(reserve, 3),
        "available_budget_gb": round(budget, 3),
        "disk_required_gb": round(disk, 3),
        "components": components,
        "fits_ram": workload <= budget,
        "fits_disk": hardware.disk_free_gb is None or disk <= hardware.disk_free_gb,
        "mode": "concurrent" if requirements.concurrent else "sequential",
    }


def incompatibilities(
    model: dict[str, Any], hardware: HardwareProfile, req: Requirements
) -> list[str]:
    reasons = []
    if hardware.os not in model["os"]:
        reasons.append("SO incompatível")
    if hardware.architecture not in model["architectures"]:
        reasons.append("arquitetura incompatível")
    if model["license"] not in req.allowed_licenses:
        reasons.append("licença não permitida")
    if model["max_context"] is not None and req.context_tokens > model["max_context"]:
        reasons.append("contexto excede limite do modelo")
    if (
        req.requires_tool_calling
        and set(model["roles"]) & {"conversation", "coding"}
        and not model["tool_calling_verified"]
    ):
        reasons.append("tool calling não verificado")
    if req.require_installed and model["runtime"] not in hardware.runtimes:
        reasons.append("runtime ausente")
    return reasons


def advise(
    requirements: Requirements, hardware: HardwareProfile, *, catalog: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return a schema-valid, shareable Blueprint. No disk writes or network calls."""
    catalog = catalog if catalog is not None else load_catalog()
    roles = sorted(set(requirements.capabilities) & MODEL_ROLES)
    pools: list[list[dict[str, Any]]] = []
    rejected: dict[str, list[str]] = {}
    missing = []
    for role in roles:
        candidates = []
        for model in catalog["entries"]:
            if role not in model["roles"]:
                continue
            issues = incompatibilities(model, hardware, requirements)
            if issues:
                rejected[model["id"]] = issues
            else:
                candidates.append(model)
        if not candidates:
            missing.append(role)
        pools.append(sorted(candidates, key=lambda model: model["id"]))
    combinations: list[dict[str, Any]] = []
    if math.prod(len(pool) for pool in pools) > 10000:
        raise ValueError("Catálogo produz mais de 10000 combinações; reduza os candidatos")
    if not missing:
        for combination in itertools.product(*pools):
            models = list(combination)
            budget = estimate(models, hardware, requirements)
            if budget["fits_ram"] and budget["fits_disk"]:
                capacity = sum(math.log1p(model["parameters_b"]) for model in models)
                combinations.append({"models": models, "budget": budget, "capacity": capacity})
    recommendations: list[dict[str, Any]] = []
    for profile in PROFILES:
        if not combinations:
            reasons = (
                ["Sem candidato compatível para: " + ", ".join(missing)]
                if missing
                else ["Nenhuma combinação cabe no orçamento de RAM/disco com margem de segurança."]
            )
            recommendations.append(
                {
                    "profile": profile,
                    "models": [],
                    "reasons": reasons,
                    "status": "not_feasible",
                    "estimated_peak_ram_gb": None,
                    "estimated_peak_vram_gb": None,
                }
            )
            continue

        def rank(item: dict[str, Any], profile: str = profile) -> tuple[float, str]:
            peak = float(item["budget"]["workload_ram_gb"])
            capacity = float(item["capacity"])
            score = -peak if profile == "fastest" else capacity
            if profile == "balanced":
                score = capacity - 0.4 * peak
            return -score, ",".join(m["id"] for m in item["models"])

        chosen = min(combinations, key=rank)
        budget = chosen["budget"]
        reasons = [
            "Filtros de SO, arquitetura, licença, contexto e política satisfeitos.",
            f"Carga {budget['workload_ram_gb']} GiB / "
            f"orçamento {budget['available_budget_gb']} GiB.",
            "Execução planejada em CPU; não presume driver ou aceleração GPU.",
        ]
        if not requirements.concurrent and len(chosen["models"]) > 1:
            reasons.append(
                "Troca sequencial exige descarregar modelos; latência de troca não medida."
            )
        required_runtimes = sorted(
            {m["runtime"] for m in chosen["models"]} - set(hardware.runtimes)
        )
        if required_runtimes:
            reasons.append("Instalação futura necessária: " + ", ".join(required_runtimes))
        for model in {m["id"]: m for m in chosen["models"]}.values():
            reasons.extend(model.get("planning_notes", []))
        recommendations.append(
            {
                "profile": profile,
                "models": [
                    {
                        "role": role,
                        "catalog_id": m["id"],
                        "source": m["source"],
                        "revision": m["revision"],
                    }
                    for role, m in zip(roles, chosen["models"], strict=True)
                ],
                "status": "candidate",
                "reasons": reasons,
                "estimated_peak_ram_gb": budget["peak_ram_gb"],
                "estimated_peak_vram_gb": 0,
                "resource_budget": budget,
            }
        )
    warnings = [
        "Estimativas conservadoras, sem benchmark local; não garantem velocidade ou qualidade.",
        "Perfis fastest/highest_quality usam memória/tamanho como heurísticas, não medições.",
        "Requisitos extraídos do texto devem ser revisados; use entrada estruturada para precisão.",
        "Nenhum modelo é baixado, instalado ou executado pelo Advisor.",
    ] + hardware.warnings
    if "asr" in requirements.capabilities:
        warnings.append(
            "Áudio: RAM publicada pelo whisper.cpp acrescida de 50% e 0,25 GiB por entrada; "
            "hipótese de planejamento em blocos de até 30 s, sem benchmark local. "
            "A janela de contexto de conversa não se aplica à transcrição."
        )
    if hardware.disk_free_gb is None:
        warnings.append("Disco livre desconhecido: confirmar espaço antes de provisionar.")
    if "mcp" in requirements.capabilities:
        warnings.append(
            "MCP é arquitetura planejada; autenticação e execução de conectores são Fase 2."
        )
    if requirements.privacy == "hybrid_opt_in":
        warnings.append(
            "Opt-in híbrido registrado; catálogo atual considera somente modelos locais."
        )
    if "hardware_hid" in allowed_executors(requirements):
        warnings.append("HID requer dispositivo; captura de tela exige canal separado.")
    ids = [tuple(m["catalog_id"] for m in rec["models"]) for rec in recommendations]
    if combinations and len(set(ids)) < 3:
        warnings.append(
            "Alguns perfis coincidem: não há três escolhas distintas para estes critérios."
        )
    blueprint: dict[str, Any] = {
        "schema_version": "1.0.0",
        "project": {"name": "local-agent", "description": "ZYNVU Advisor"},
        "hardware": hardware.to_dict(),
        "requirements": requirements.to_dict(),
        "recommendations": recommendations,
        "policy": {
            "allowed_interface_executors": allowed_executors(requirements),
            "denied_interface_executors": sorted(set(requirements.denied_interface_executors)),
        },
        "catalog_version": catalog["version"],
        "warnings": warnings,
        "rejected_candidates": rejected,
        "memory_plan": {
            "enabled": "memory" in requirements.capabilities,
            "strategy": "SQLite FTS + documentos locais; embeddings opcionais após avaliação",
            "implemented": False,
        },
        "decision_plan": "deterministic rules",
        "training_plan": "disabled; avaliar RAG e skills antes de fine-tuning",
    }
    blueprint = scrub(blueprint)
    validate_blueprint(blueprint)
    return blueprint
