import shutil

import pytest

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models.provenance import file_digest
from astra_pcb.simulation.corners import AudioFilterSweep, PowerSweep
from astra_pcb.simulation.models import ModelFile, flatten
from astra_pcb.simulation.workflow import SimulationJob


@pytest.fixture
def evidence():
    return DatasheetEvidence(
        document="Synthetic model definition",
        manufacturer="Project",
        revision="1",
        page="1",
        extracted_constraint="Ideal primitive circuit only",
        source_location="test",
    )


def test_model_resolution_hash_cycle_and_missing_section(tmp_path, evidence):
    top = tmp_path / "top.cir"
    model = tmp_path / "model.lib"
    top.write_text('Test\n.lib "model.lib" TT\n.end\n')
    model.write_text(".lib TT\n.model DTEST D(Is=1e-14)\n.endl TT\n")
    approved = ModelFile(
        path="model.lib",
        sha256=file_digest(model),
        sections=("TT",),
        license="Test",
        approved_by="Test",
        evidence=evidence,
    )
    content, _, hashes = flatten(top, (approved,))
    assert ".model DTEST" in content and len(hashes) == 2
    with pytest.raises(ValueError):
        flatten(top, ())
    model.write_text('.lib TT\n.include "model.lib"\n.endl TT\n')
    with pytest.raises(ValueError):
        flatten(top, (approved,))
    approved = approved.model_copy(update={"sha256": file_digest(model)})
    with pytest.raises(ValueError):
        flatten(top, (approved,))
    top.write_text('Test\n.include "../escape"\n.end\n')
    with pytest.raises(ValueError):
        flatten(top, (approved,))


def test_simulation_units_require_matching_dimensions():
    job = {
        "netlist": "x.cir",
        "description": "test",
        "assumptions": ["test"],
        "measurement_units": {"v": "V"},
        "assertions": {"v": {"min": 0, "max": 5000, "unit": "mV"}},
    }
    assert SimulationJob.model_validate(job).assertions["v"].unit == "mV"
    job["assertions"]["v"]["unit"] = "Hz"
    with pytest.raises(ValueError):
        SimulationJob.model_validate(job)


@pytest.mark.integration
def test_actual_audio_and_power_corners(tmp_path, evidence):
    if not shutil.which("ngspice"):
        pytest.skip("ngspice unavailable")
    audio = AudioFilterSweep(
        resistance_ohm=(990, 1010),
        capacitance_f=(7.5e-9, 8.4e-9),
        source_ohm=(10, 100),
        load_ohm=(10000, 100000),
        gain_min_db=-1.1,
        gain_max_db=0,
        cutoff_min_hz=17000,
        cutoff_max_hz=24000,
        evidence=evidence,
    )
    assert audio.run(tmp_path / "audio").exit_code == 0
    power = PowerSweep(
        source_v=(4.75, 5.25),
        source_resistance_ohm=(0.18, 0.22),
        capacitance_f=(80e-6, 120e-6),
        load_a=0.5,
        evidence=evidence,
    )
    result = power.run(tmp_path / "power")
    assert result.exit_code == 0, result.model_dump_json()
