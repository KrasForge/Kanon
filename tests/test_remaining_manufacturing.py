import json
from pathlib import Path

import pytest

from astra_pcb.config import load_yaml
from astra_pcb.manufacturing import ManufacturingProfile
from astra_pcb.manufacturing.assembly import AssemblyPart, AssemblyPlan
from astra_pcb.mechanical import check_step
from astra_pcb.mechanical.mcp import FreeCADTools
from astra_pcb.mechanical.models import model_inventory
from astra_pcb.models.provenance import file_digest
from astra_pcb.release.artifacts import check_export
from astra_pcb.verification.process import ProcessResult


def receipt(*paths, command=("fixture",)):
    return ProcessResult(
        command=command,
        exit_code=0,
        input_digest="a" * 64,
        artifacts=tuple(str(p) for p in paths),
        artifact_hashes={str(p.resolve()): file_digest(p) for p in paths},
    )


def test_exact_export_inventory(tmp_path):
    pth, npth = tmp_path / "board-PTH.drl", tmp_path / "board-NPTH.drl"
    pth.write_text("M48\n; #@! TF.FileFunction,Plated,1,2,PTH\n%\nM30\n")
    npth.write_text("M48\n; #@! TF.FileFunction,NonPlated,1,2,NPTH\n%\nM30\n")
    assert (
        check_export("drill", receipt(pth, npth), expected_drills=("PTH", "NPTH")).status == "PASS"
    )
    assert check_export("drill", receipt(pth), expected_drills=("PTH", "NPTH")).status == "ERROR"
    assert (
        check_export("drill", receipt(pth, npth), expected_drills=("combined",)).status == "ERROR"
    )
    npth.write_text(pth.read_text())
    assert (
        check_export("drill", receipt(pth, npth), expected_drills=("PTH", "NPTH")).status == "ERROR"
    )
    front, extra = tmp_path / "board-F_Cu.gbr", tmp_path / "board-B_Cu.gbr"
    front.write_text("%FSLAX46Y46*%\n%MOMM*%\n%TF.FileFunction,Copper,L1,Top*%\nM02*\n")
    extra.write_text(front.read_text())
    assert check_export("gerbers", receipt(front), expected_layers=("F.Cu",)).status == "PASS"
    assert (
        check_export("gerbers", receipt(front, extra), expected_layers=("F.Cu",)).status == "ERROR"
    )
    assert (
        check_export("gerbers", receipt(front, front), expected_layers=("F.Cu",)).status == "ERROR"
    )


def test_step_units_origin_and_missing_model(tmp_path):
    step = tmp_path / "test.step"
    step.write_text("ISO-10303-21;\n#1=SI_UNIT(.MILLI.,.METRE.);\nEND-ISO-10303-21;\n")
    valid = receipt(step, command=("kicad-cli", "pcb", "export", "step", "--user-origin", "0x0mm"))
    assert check_step(valid, step, require_frame=True).status == "PASS"
    assert check_step(receipt(step), step, require_frame=True).status == "ERROR"
    assert (
        check_step(valid.model_copy(update={"stderr": "Unable to load model"}), step).status
        == "ERROR"
    )
    step.write_text(step.read_text().replace("MILLI", "CENTI"))
    assert (
        check_step(receipt(step, command=valid.command), step, require_frame=True).status == "ERROR"
    )
    board = tmp_path / "board.kicad_pcb"
    board.write_text('(kicad_pcb (footprint "R" (property "Reference" "R1")))')
    assert model_inventory(board).exit_code == 1
    assert (
        model_inventory(board, exemptions={"R1": "Explicit fixture-only omitted model"}).exit_code
        == 0
    )
    with pytest.raises(ValueError):
        model_inventory(board, exemptions={"R2": "wrong reference"})
    board.write_text(
        '(kicad_pcb (footprint "R" (property "Reference" "R1") (model "missing.step")))'
    )
    assert model_inventory(board).exit_code == 1


def test_declared_assembly_controls():
    profile = ManufacturingProfile.model_validate(
        load_yaml(Path("config/manufacturing/jlcpcb-4layer.yaml"))
    )
    part = AssemblyPart(
        reference="U1",
        package="synthetic",
        technology="BGA",
        side="top",
        polarity_required=True,
        polarity_mark_verified=False,
        placement_rotation_verified=True,
        courtyard_clearance_mm=-0.1,
        evidence=("Synthetic assembly inspection",),
    )
    plan = AssemblyPlan(
        parts=(part,),
        source_references=frozenset({"U1"}),
        fiducials_required=3,
        usable_fiducials=2,
        fiducial_evidence=("Synthetic placement drawing",),
        minimum_courtyard_clearance_mm=0,
    )
    statuses = {c.check_id: c.status for c in plan.audit(profile).results}
    assert statuses["assembly.U1.courtyard"] == "FAIL"
    assert statuses["assembly.U1.polarity"] == "FAIL"
    assert statuses["assembly.fiducials"] == "FAIL"
    approved = part.model_copy(
        update={
            "technology": "other",
            "courtyard_clearance_mm": 0.2,
            "polarity_mark_verified": True,
        }
    )
    assert (
        plan.model_copy(update={"parts": (approved,), "usable_fiducials": 3})
        .audit(profile)
        .exit_code
        == 0
    )
    unknown = approved.model_copy(update={"placement_rotation_verified": None})
    assert (
        plan.model_copy(update={"parts": (unknown,), "usable_fiducials": 3})
        .audit(profile)
        .exit_code
        == 2
    )


def test_freecad_missing_or_wrong_readback_is_error():
    class FakeTools:
        value = None

        def call(self, operation, arguments, **kwargs):
            return {"content": [{"type": "text", "text": json.dumps(self.value)}]}

    fake = FakeTools()
    facade = FreeCADTools(fake)
    with pytest.raises(ValueError, match="Missing"):
        facade.read_object("D", "Box")
    fake.value = {
        "Name": "Box",
        "Properties": {"Length": "10 mm", "Width": "10 mm", "Height": "1 mm"},
    }
    with pytest.raises(ValueError, match="readback"):
        facade.create_box("D", "Box", length_mm=10, width_mm=10, height_mm=2, allow_write=True)
    assert (
        facade.create_box("D", "Box", length_mm=10, width_mm=10, height_mm=1, allow_write=True)[
            "Name"
        ]
        == "Box"
    )
