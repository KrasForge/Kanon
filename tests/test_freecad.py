"""Optional actual FreeCAD native-document and STEP round-trip qualification."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_actual_freecad_native_and_step_roundtrip(tmp_path):
    executable = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    if not executable:
        pytest.skip("Optional FreeCAD command-line runtime unavailable")
    output = tmp_path / "outputs"
    script = Path("scripts/qualify_freecad.py").resolve()
    result = subprocess.run(
        [
            executable,
            "--safe-mode",
            "-u",
            str(tmp_path / "user.cfg"),
            "-s",
            str(tmp_path / "system.cfg"),
            str(script),
        ],
        env={**os.environ, "KANON_FREECAD_SMOKE_ROOT": str(output)},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # FreeCAD can print a Python exception and exit zero; require the success artifact too.
    receipt = json.loads((output / "qualification.json").read_text())
    assert receipt["native_roundtrip"] and abs(receipt["step_volume_mm3"] - 160) < 1e-6
    assert (output / "envelope.FCStd").stat().st_size > 0
    assert "ISO-10303-21" in (output / "envelope.step").read_text()


@pytest.mark.integration
def test_actual_optional_freecad_mcp(tmp_path):
    provider = Path(
        os.environ.get(
            "KANON_FREECAD_MCP_ROOT",
            str(Path.home() / ".local/share/kanon/integrations/freecad-mcp"),
        )
    )
    if (
        not shutil.which("FreeCAD")
        or not shutil.which("Xvfb")
        or not (provider / ".venv/bin/freecad-mcp").exists()
    ):
        pytest.skip("Optional pinned FreeCAD/MCP GUI qualification runtime unavailable")
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/qualify_freecad_mcp.py", str(provider), str(tmp_path / "probe")],
        capture_output=True,
        text=True,
        timeout=110,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads((tmp_path / "probe/qualification.json").read_text())
    assert receipt["native"]["valid"] and abs(receipt["native"]["volume_mm3"] - 160) < 1e-8
    assert len(receipt["calls"]) == 6
