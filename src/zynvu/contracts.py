"""Validated, explicit inputs. Unknown facts stay unknown."""

import math
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from jsonschema import FormatChecker

CAPABILITIES = {"conversation", "coding", "vision", "asr", "tts", "memory", "mcp", "decision"}
EXECUTORS = {"api_mcp", "playwright", "selenium", "pyautogui", "native_os", "hardware_hid"}


def string_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{name}: lista de textos esperada")


def number(value: float | None, name: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name}: número esperado")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name}: valor finito não negativo esperado")


@dataclass
class HardwareProfile:
    source: str
    observed_at: str
    os: str
    cpu: str
    ram_gb: float
    architecture: str = "AMD64"
    available_ram_gb: float | None = None
    gpu: str | None = None
    vram_gb: float | None = None
    shared_memory: bool | None = None
    disk_free_gb: float | None = None
    runtimes: list[str] = field(default_factory=list)
    provenance: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name in ["source", "observed_at", "os", "cpu", "architecture"]:
            if not isinstance(getattr(self, name), str):
                raise ValueError(f"{name}: texto esperado")
        timestamp = datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
        if timestamp.tzinfo is None or not FormatChecker().conforms(self.observed_at, "date-time"):
            raise ValueError("observed_at deve ser RFC3339 com timezone")
        if self.source not in {"detected", "fixture"}:
            raise ValueError("source deve ser detected ou fixture")
        for name in ["ram_gb", "available_ram_gb", "vram_gb", "disk_free_gb"]:
            number(getattr(self, name), name, nullable=name != "ram_gb")
        if self.available_ram_gb is not None and self.available_ram_gb > self.ram_gb:
            raise ValueError("RAM disponível não pode exceder RAM física")
        if self.shared_memory is not None and type(self.shared_memory) is not bool:
            raise ValueError("shared_memory deve ser booleano ou desconhecido")
        if self.gpu is not None and not isinstance(self.gpu, str):
            raise ValueError("gpu deve ser texto ou desconhecida")
        string_list(self.runtimes, "runtimes")
        string_list(self.warnings, "warnings")
        if not isinstance(self.provenance, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) for k, v in self.provenance.items()
        ):
            raise ValueError("provenance deve mapear textos")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.shared_memory is None:
            result.pop("shared_memory")
        return result


@dataclass
class Requirements:
    user_goal: str
    capabilities: list[str] = field(default_factory=lambda: ["conversation"])
    privacy: str = "local_only"
    context_tokens: int = 4096
    concurrent: bool = False
    agents: int = 1
    require_installed: bool = False
    allowed_licenses: list[str] = field(default_factory=lambda: ["apache-2.0", "mit"])
    requires_tool_calling: bool = False
    allowed_interface_executors: list[str] = field(default_factory=lambda: ["api_mcp"])
    denied_interface_executors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name in [
            "capabilities",
            "allowed_licenses",
            "allowed_interface_executors",
            "denied_interface_executors",
        ]:
            string_list(getattr(self, name), name)
        if not isinstance(self.user_goal, str) or not self.user_goal.strip():
            raise ValueError("Descreva o objetivo do agente")
        if len(self.user_goal) > 10000:
            raise ValueError("Objetivo excede 10000 caracteres")
        if not self.capabilities or set(self.capabilities) - CAPABILITIES:
            raise ValueError("Capacidades inválidas")
        self.capabilities = sorted(set(self.capabilities))
        if not isinstance(self.privacy, str) or self.privacy not in {"local_only", "hybrid_opt_in"}:
            raise ValueError("Política de privacidade inválida")
        for name, maximum in [("context_tokens", 131072), ("agents", 32)]:
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"{name} fora dos limites")
        for name in ["concurrent", "require_installed", "requires_tool_calling"]:
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} deve ser booleano")
        for name in ["allowed_interface_executors", "denied_interface_executors"]:
            if set(getattr(self, name)) - EXECUTORS:
                raise ValueError("Executor desconhecido")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
