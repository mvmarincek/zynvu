import subprocess
from unittest.mock import patch

from zynvu.hardware import diagnose


def test_windows_cim_failure_is_explicit():
    with (
        patch("zynvu.hardware.platform.system", return_value="Windows"),
        patch("zynvu.hardware.platform.processor", return_value="fixture-cpu"),
        patch("zynvu.hardware.platform.machine", return_value="AMD64"),
        patch("zynvu.hardware.subprocess.run", side_effect=subprocess.TimeoutExpired("CIM", 15)),
    ):
        result = diagnose()
    assert result.ram_gb > 0
    assert result.source == "detected"
    assert result.vram_gb is None
    assert any("CIM" in item for item in result.warnings)


def test_other_os_has_clear_limitations():
    with patch("zynvu.hardware.platform.system", return_value="Darwin"):
        result = diagnose()
    assert result.os == "Darwin"
    assert any("não implementado" in warning for warning in result.warnings)
