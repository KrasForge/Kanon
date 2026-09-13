"""Small real-tool probes, not complete board integration qualification."""

import shutil
from pathlib import Path

import pytest

from astra_pcb.kicad import KiCadCLI
from astra_pcb.simulation import assert_limit, measurements, simulate
from astra_pcb.verification.process import run


@pytest.mark.integration
@pytest.mark.skipif(not shutil.which("kicad-cli"), reason="KiCad CLI is not installed")
def test_kicad_version_and_invalid_input(tmp_path):
    version = run(["kicad-cli", "version"])
    assert version.exit_code == 0 and version.stdout.strip()
    result = KiCadCLI().check("drc", tmp_path / "missing.kicad_pcb", tmp_path / "drc.json")
    assert result.exit_code != 0
    assert not result.artifacts


@pytest.mark.integration
@pytest.mark.skipif(not shutil.which("ngspice"), reason="ngspice is not installed")
def test_real_ngspice_divider(tmp_path):
    netlist = tmp_path / "divider.cir"
    netlist.write_text("""Resistive divider
V1 in 0 DC 2
R1 in out 1k
R2 out 0 1k
.tran 1u 10u
.measure tran output_voltage FIND v(out) AT=5u
.end
""")
    output = tmp_path / "simulation.log"
    result = simulate(netlist, output)
    assert result.exit_code == 0 and result.error is None
    assert str(output) in result.artifacts
    values = measurements(Path(output).read_text())
    assert assert_limit("output_voltage", values, 0.999, 1.001).status == "PASS"
