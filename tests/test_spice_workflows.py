import shutil
from pathlib import Path

import pytest

from astra_pcb.config import load_yaml
from astra_pcb.simulation import measurements, simulate
from astra_pcb.simulation.workflow import SimulationJob, run_job

ROOT = Path(__file__).resolve().parents[1] / "examples/simulation"


def test_duplicate_measurements_and_unsafe_directives(tmp_path):
    with pytest.raises(ValueError, match="Duplicate"):
        measurements("gain = 1\ngain = 2\n")
    netlist = tmp_path / "unsafe.cir"
    netlist.write_text("Bad\n.control\nshell touch forbidden\n.endc\n.end\n")
    result = simulate(netlist, tmp_path / "log", executable="does-not-exist")
    assert result.error and not (tmp_path / "forbidden").exists()


@pytest.mark.integration
@pytest.mark.parametrize("name", ["rc-filter", "power-transient"])
def test_real_ngspice_assertions(tmp_path, name):
    if not shutil.which("ngspice"):
        pytest.skip("ngspice is not installed")
    job = SimulationJob.model_validate(load_yaml(ROOT / f"{name}.yaml"))
    assert run_job(job, ROOT, tmp_path / "pass.log").exit_code == 0
    assertions = dict(job.assertions)
    first = next(iter(assertions))
    assertions[first] = type(assertions[first])(min=100, max=101)
    failed = run_job(job.model_copy(update={"assertions": assertions}), ROOT, tmp_path / "fail.log")
    assert failed.exit_code == 1
    assert any(c.status == "FAIL" for c in failed.results)


@pytest.mark.integration
def test_ngspice_aborted_analysis_is_not_success(tmp_path):
    if not shutil.which("ngspice"):
        pytest.skip("ngspice is not installed")
    source = tmp_path / "broken.cir"
    source.write_text("Broken model\nV1 a 0 5\nD1 a 0 MISSING_MODEL\n.op\n.end\n")
    result = simulate(source, tmp_path / "failed.log")
    assert result.error or result.exit_code != 0
