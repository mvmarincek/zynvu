"""Read-only hardware inventory. Never invokes a model/runtime."""

import json
import platform
import shutil
import subprocess
from datetime import UTC, datetime

import psutil

from zynvu.contracts import HardwareProfile

GIB = 1024**3


def diagnose() -> HardwareProfile:
    memory = psutil.virtual_memory()
    system = platform.system()
    profile = HardwareProfile(
        source="detected",
        observed_at=datetime.now(UTC).isoformat(),
        os=system,
        cpu=platform.processor() or "unknown",
        architecture=platform.machine(),
        ram_gb=round(memory.total / GIB, 3),
        available_ram_gb=round(memory.available / GIB, 3),
        disk_free_gb=round(shutil.disk_usage(".").free / GIB, 3),
        provenance={"ram": "psutil.virtual_memory", "disk": "cwd volume", "cpu": "platform"},
    )
    for runtime, executable in [("llama.cpp", "llama-cli"), ("ollama", "ollama")]:
        if shutil.which(executable):
            profile.runtimes.append(runtime)
    profile.provenance["runtimes"] = "PATH discovery only; versions not validated"
    if system != "Windows":
        profile.warnings.append(
            "Diagnóstico GPU/driver não implementado neste SO; perfil CPU básico."
        )
        return profile
    script = (
        "$ErrorActionPreference='Stop'; "
        "@(Get-CimInstance Win32_VideoController | "
        "Select-Object Name,DriverVersion) | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        devices = json.loads(result.stdout or "[]")
        if isinstance(devices, dict):
            devices = [devices]
        profile.gpu = "; ".join(item["Name"] for item in devices if item.get("Name")) or None
        profile.provenance["gpu"] = "Win32_VideoController.Name"
        profile.provenance["drivers"] = "; ".join(
            item.get("DriverVersion") or "unknown" for item in devices
        )
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError):
        profile.warnings.append("Consulta CIM indisponível; GPU/driver desconhecidos.")
    # AdapterRAM is a uint32 and unreliable for modern GPUs; never use it for budgets.
    profile.warnings.append(
        "VRAM/memória compartilhada não medidas; planejamento conservador em CPU."
    )
    return profile
