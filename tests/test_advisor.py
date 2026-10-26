import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from zynvu import advise, parse_goal
from zynvu.catalog import load_catalog
from zynvu.cli import main
from zynvu.contracts import HardwareProfile, Requirements
from zynvu.engine import estimate
from zynvu.export import validate_blueprint
from zynvu.policy import authorize_executor


def hardware(ram=16, **kwargs):
    return HardwareProfile(
        source="fixture",
        observed_at="2026-10-25T00:00:00Z",
        os="Windows",
        cpu="fixture",
        ram_gb=ram,
        disk_free_gb=100,
        **kwargs,
    )


@pytest.mark.parametrize("ram", [4, 8, 16, 32])
@pytest.mark.parametrize("vram", [None, 4, 8, 16])
def test_memory_matrix(ram, vram):
    result = advise(parse_goal("programar código"), hardware(ram, vram_gb=vram))
    validate_blueprint(result)
    assert len(result["recommendations"]) == 3
    for rec in result["recommendations"]:
        assert rec["status"] == "candidate"
        assert rec["estimated_peak_ram_gb"] <= ram
        assert rec["estimated_peak_vram_gb"] == 0
        assert {m["role"] for m in rec["models"]} == {"coding", "conversation"}


def test_shared_memory_does_not_expand_budget():
    req = parse_goal("conversar")
    baseline = advise(req, hardware(4))["recommendations"]
    assert baseline == advise(req, hardware(4, shared_memory=True, vram_gb=16))["recommendations"]


@pytest.mark.parametrize("ram,available", [(4, 2), (8, 3), (24, 7)])
def test_conversation_and_speech_fit_with_explicit_cpu_budgets(ram, available):
    req = Requirements("conversa e transcrição", capabilities=["conversation", "asr"])
    result = advise(req, hardware(ram, available_ram_gb=available))
    for rec in result["recommendations"]:
        assert rec["status"] == "candidate"
        assert {m["role"] for m in rec["models"]} == {"conversation", "asr"}
        assert rec["resource_budget"]["workload_ram_gb"] <= available - 0.5
    assert any("30 s" in warning for warning in result["warnings"])


def test_speech_budget_is_independent_of_chat_context_but_scales_with_agents():
    model = next(e for e in load_catalog()["entries"] if "asr" in e["roles"])
    short = Requirements("transcrever", capabilities=["asr"], context_tokens=4096)
    long = Requirements("transcrever", capabilities=["asr"], context_tokens=131072)
    assert estimate([model], hardware(), short) == estimate([model], hardware(), long)
    assert advise(long, hardware())["recommendations"][0]["status"] == "candidate"
    long.agents = 4
    assert (
        estimate([model], hardware(), long)["workload_ram_gb"]
        > estimate([model], hardware(), short)["workload_ram_gb"]
    )


def test_speech_respects_license_runtime_and_resource_filters():
    for req, hw in [
        (Requirements("voz", capabilities=["asr"], allowed_licenses=["apache-2.0"]), hardware()),
        (Requirements("voz", capabilities=["asr"], require_installed=True), hardware()),
        (Requirements("voz", capabilities=["asr"]), hardware(available_ram_gb=0.6)),
    ]:
        assert advise(req, hw)["recommendations"][0]["status"] == "not_feasible"
    no_disk = hardware()
    no_disk.disk_free_gb = 0
    assert (
        advise(Requirements("voz", capabilities=["asr"]), no_disk)["recommendations"][0]["status"]
        == "not_feasible"
    )
    req = Requirements("voz", capabilities=["asr"], require_installed=True)
    assert (
        advise(req, hardware(runtimes=["whisper.cpp"]))["recommendations"][0]["status"]
        == "candidate"
    )


def test_no_fit_is_not_a_fake_recommendation():
    for req, hw in [
        (parse_goal("conversar"), hardware(1)),
        (parse_goal("interpretar imagens e transcrever voz"), hardware(32)),
        (Requirements("chat", allowed_licenses=["mit"]), hardware()),
        (Requirements("chat", require_installed=True), hardware()),
        (Requirements("tools", requires_tool_calling=True), hardware()),
        (Requirements("chat", context_tokens=131072), hardware()),
        (Requirements("chat"), hardware(available_ram_gb=0.1)),
    ]:
        result = advise(req, hw)
        assert all(
            r["status"] == "not_feasible" and not r["models"] for r in result["recommendations"]
        )


def test_disk_arch_os_and_runtime_filters():
    hw = hardware()
    for field, value in [("disk_free_gb", 0.1), ("architecture", "mips"), ("os", "unknown")]:
        altered = copy.deepcopy(hw)
        setattr(altered, field, value)
        assert advise(parse_goal("chat"), altered)["recommendations"][0]["status"] == "not_feasible"
    hw.runtimes = ["llama.cpp"]
    assert advise(Requirements("chat", require_installed=True), hw)["recommendations"][0]["models"]


def test_concurrent_and_multiagent_budget():
    models = [load_catalog()["entries"][1], load_catalog()["entries"][4]]
    req = Requirements("chat e código")
    sequential = estimate(models, hardware(), req)
    req.concurrent = True
    simultaneous = estimate(models, hardware(), req)
    assert simultaneous["peak_ram_gb"] > sequential["peak_ram_gb"]
    req.agents = 4
    assert estimate(models, hardware(), req)["peak_ram_gb"] > simultaneous["peak_ram_gb"]


def test_determinism_and_catalog_order():
    catalog = load_catalog()
    first = advise(parse_goal("programar"), hardware(), catalog=catalog)
    catalog["entries"].reverse()
    assert first == advise(parse_goal("programar"), hardware(), catalog=catalog)


def test_voki_denies_every_software_fallback():
    req = Requirements(
        "voki",
        allowed_interface_executors=["hardware_hid"],
        denied_interface_executors=["playwright", "selenium", "pyautogui", "native_os"],
    )
    authorize_executor("hardware_hid", req)
    for executor in ["playwright", "selenium", "pyautogui", "native_os", "api_mcp", "unknown"]:
        with pytest.raises(PermissionError):
            authorize_executor(executor, req)
    req.allowed_interface_executors.append("playwright")
    with pytest.raises(PermissionError):
        authorize_executor("playwright", req)
    result = advise(req, hardware())
    assert result["policy"]["allowed_interface_executors"] == ["hardware_hid"]
    assert any("captura" in warning for warning in result["warnings"])


def test_secret_scrubbing():
    secret = "sk-" + "sensitivevalue" * 3
    result = advise(parse_goal(f"chat api_key={secret}"), hardware())
    assert secret not in json.dumps(result)
    assert result["requirements"]["context_tokens"] == 4096


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, "16"])
def test_invalid_hardware(value):
    with pytest.raises(ValueError):
        hardware(value)


def test_cli_export_roundtrip(tmp_path):
    fixture = tmp_path / "hardware.json"
    fixture.write_text(json.dumps(hardware().to_dict()), encoding="utf-8")
    blueprint = tmp_path / "blueprint.json"
    report = tmp_path / "report.md"
    assert (
        main(
            [
                "advise",
                "--goal",
                "programar",
                "--hardware",
                str(fixture),
                "--out",
                str(blueprint),
                "--report",
                str(report),
            ]
        )
        == 0
    )
    assert main(["validate", str(blueprint)]) == 0
    assert "Pico estimado" in report.read_text(encoding="utf-8")
    assert main(["advise", "--goal", "vision", "--hardware", str(fixture)]) == 3


def test_invalid_input_does_not_echo_secrets(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text('{"api_key":"secret-value"}', encoding="utf-8")
    assert main(["advise", "--requirements", str(path), "--hardware", str(path)]) == 2
    assert "secret-value" not in capsys.readouterr().err


def test_pack_schema_unchanged():
    root = Path(__file__).resolve().parents[1]
    original = (
        root / "context/ZYNVU_Codex_Knowledge_Pack/zynvu_codex_kit/schemas/blueprint.schema.json"
    )
    assert json.loads(original.read_text()) == json.loads(
        (root / "src/zynvu/data/blueprint.schema.json").read_text()
    )


def test_cli_runs_as_module():
    result = subprocess.run(
        [sys.executable, "-m", "zynvu", "catalog"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert len(json.loads(result.stdout)["entries"]) == 9


def test_cli_json_is_utf8_with_legacy_pipe_encoding():
    result = subprocess.run(
        [sys.executable, "-m", "zynvu", "parse", "Assistente para português e 日本語"],
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "ascii"},
    )
    assert result.returncode == 0
    assert "日本語" in json.loads(result.stdout.decode("utf-8"))["user_goal"]


def test_offline_sdk_vm_fixture(monkeypatch):
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("Advisor must not access the network")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    root = Path(__file__).resolve().parents[1]
    profile = HardwareProfile(**json.loads((root / "examples/hardware-cpu-8gb.json").read_text()))
    result = advise(parse_goal("conversar e programar"), profile)
    assert result["recommendations"][0]["status"] == "candidate"


@pytest.mark.parametrize(
    "overrides",
    [
        {"capabilities": "coding"},
        {"allowed_interface_executors": "hardware_hid"},
        {"agents": True},
        {"context_tokens": 0},
        {"privacy": []},
    ],
)
def test_rejects_malformed_requirements(overrides):
    with pytest.raises(ValueError):
        Requirements("chat", **overrides)


@pytest.mark.parametrize("timestamp", ["2026-10-25", "20261025T000000Z", "2026-10-25T00:00:00"])
def test_hardware_requires_schema_compatible_timestamp(timestamp):
    profile = hardware().to_dict()
    profile["observed_at"] = timestamp
    with pytest.raises(ValueError):
        HardwareProfile(**profile)
