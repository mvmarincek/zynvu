import json
import re
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SECRET_KEYS = re.compile(r"password|secret|token|api[_-]?key|authorization", re.I)
SECRET_VALUES = re.compile(
    r"(?i)(?:bearer\s+\S+|(?:sk-|ghp_|github_pat_|sk_live_|sk_test_)[A-Za-z0-9_-]{8,}"
    r"|(?:password|senha|secret|api[_-]?key|token)\s*[:=]\s*[^\s,;]+)"
)


def scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if SECRET_KEYS.search(k) and k != "context_tokens" else scrub(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, str):
        return SECRET_VALUES.sub("[REDACTED]", value)
    return value


def validate_blueprint(blueprint: dict[str, Any]) -> None:
    schema = json.loads(files("zynvu").joinpath("data/blueprint.schema.json").read_text("utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(blueprint)
    # Reject NaN/Infinity even in extensible fields.
    json.dumps(blueprint, allow_nan=False)


def report(blueprint: dict[str, Any]) -> str:
    lines = [
        "# ZYNVU — arquitetura recomendada",
        "",
        "Fase 1: planejamento, sem executar modelos.",
        "",
    ]
    hardware = blueprint["hardware"]
    lines += [
        f"Hardware: {hardware['os']} · {hardware['ram_gb']} GiB RAM · {hardware['source']}",
        "",
    ]
    names = {
        "balanced": "Equilibrado",
        "fastest": "Mais leve",
        "highest_quality": "Maior capacidade",
    }
    for item in blueprint["recommendations"]:
        lines += [f"## {names[item['profile']]} — {item['status']}", ""]
        for model in item["models"]:
            lines.append(f"- {model['role']}: {model['catalog_id']}")
        lines += [f"- {reason}" for reason in item["reasons"]]
        lines += [f"- Pico estimado de RAM: {item['estimated_peak_ram_gb']} GiB", ""]
    lines += ["## Observações", ""] + [f"- {warning}" for warning in blueprint["warnings"]]
    return "\n".join(lines) + "\n"
