"""Mechanical constraints and revision-bound STEP verification."""

from pathlib import Path

from pydantic import Field

from astra_pcb.layout import Point, Region
from astra_pcb.models import CheckResult, CheckStatus, StrictModel
from astra_pcb.models.provenance import Digest, file_digest
from astra_pcb.verification.process import ProcessResult


class MountingHole(StrictModel):
    reference: str
    center: Point
    drill_mm: float = Field(gt=0)
    fastener_clearance_mm: float = Field(ge=0)


class ConnectorPosition(StrictModel):
    reference: str
    center: Point
    tolerance_mm: float = Field(ge=0)
    mating_direction_degrees: float


class MechanicalConstraints(StrictModel):
    outline_points: tuple[Point, ...] = Field(min_length=3)
    keepouts: tuple[Region, ...] = ()
    mounting_holes: tuple[MountingHole, ...] = ()
    connectors: tuple[ConnectorPosition, ...] = ()
    maximum_component_height_mm: float = Field(gt=0)
    enclosure_references: dict[str, Digest]
    coordinate_frame: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(min_length=1)


def check_step(process: ProcessResult, step: Path) -> CheckResult:
    passed = not process.error and process.exit_code == 0 and step.is_file()
    reason = process.error or "Missing STEP export"
    if passed:
        data = step.read_text(errors="replace")
        digest = process.artifact_hashes.get(str(step.resolve()))
        passed = (
            digest is not None
            and digest == file_digest(step)
            and "ISO-10303-21;" in data[:200]
            and "END-ISO-10303-21;" in data[-500:]
            and bool(process.input_digest)
        )
        reason = (
            "STEP envelope and source/export identity match"
            if passed
            else "Invalid or changed STEP artifact"
        )
    return CheckResult(
        check_id="export.step",
        name="STEP export integrity",
        status=CheckStatus.PASS if passed else CheckStatus.ERROR,
        message=reason,
        evidence=(process.model_dump_json(),),
        source="kicad-cli STEP",
    )
