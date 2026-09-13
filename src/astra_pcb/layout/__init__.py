"""Quantified placement constraints over explicit board geometry, in millimetres."""

import math
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.models.provenance import Digest


class Point(StrictModel):
    x_mm: float
    y_mm: float

    def distance(self, other: "Point") -> float:
        return math.hypot(self.x_mm - other.x_mm, self.y_mm - other.y_mm)


class Region(StrictModel):
    id: str = Field(min_length=1)
    function: Literal[
        "power",
        "logic",
        "converter",
        "analog-input",
        "analog-output",
        "connectors",
        "memory",
        "clocks",
        "other",
    ]
    minimum: Point
    maximum: Point

    @model_validator(mode="after")
    def ordered(self):
        if self.minimum.x_mm >= self.maximum.x_mm or self.minimum.y_mm >= self.maximum.y_mm:
            raise ValueError("Region must have positive area")
        return self

    def contains(self, p: Point) -> bool:
        return (
            self.minimum.x_mm <= p.x_mm <= self.maximum.x_mm
            and self.minimum.y_mm <= p.y_mm <= self.maximum.y_mm
        )


class Placement(StrictModel):
    reference: str = Field(min_length=1)
    point: Point
    region: str
    side: Literal["top", "bottom"] = "top"


class Floorplan(StrictModel):
    input_digest: Digest
    regions: tuple[Region, ...] = Field(min_length=1)
    placements: tuple[Placement, ...]
    outline: Region | None = (
        None  # Only a declared rectangular board envelope, not arbitrary Edge.Cuts.
    )

    @model_validator(mode="after")
    def references(self):
        names = {r.id for r in self.regions}
        if len(names) != len(self.regions):
            raise ValueError("Duplicate region IDs")
        if len({p.reference for p in self.placements}) != len(self.placements):
            raise ValueError("Duplicate placement references")
        if any(p.region not in names for p in self.placements):
            raise ValueError("Unknown functional region")
        return self

    def audit(self) -> VerificationReport:
        regions = {r.id: r for r in self.regions}
        checks = []
        for placement in self.placements:
            within = regions[placement.region].contains(placement.point)
            if self.outline:
                within &= self.outline.contains(placement.point)
            checks.append(
                CheckResult(
                    check_id=f"placement.region.{placement.reference}",
                    name="Functional floorplan placement",
                    status=CheckStatus.PASS if within else CheckStatus.FAIL,
                    message="Component anchor inside declared region/outline"
                    if within
                    else "Anchor outside region/outline",
                    affected_objects=(placement.reference, placement.region),
                    evidence=(placement.model_dump_json(),),
                )
            )
        if not checks:
            checks.append(
                CheckResult(
                    check_id="placement.empty",
                    name="Placement inventory",
                    status=CheckStatus.SKIP,
                    message="No placement anchors supplied",
                )
            )
        return VerificationReport(results=tuple(checks), input_digest=self.input_digest)


class DistanceRule(StrictModel):
    id: str = Field(min_length=1)
    reference: str
    other: str | None = None
    maximum_mm: float = Field(gt=0)
    rationale: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(min_length=1)
    metric: Literal["anchor-distance", "rectangular-edge-distance"] = "anchor-distance"


def check_distances(floorplan: Floorplan, rules: tuple[DistanceRule, ...]) -> VerificationReport:
    points = {p.reference: p.point for p in floorplan.placements}
    if len({r.id for r in rules}) != len(rules):
        raise ValueError("Duplicate placement rule IDs")
    checks = []
    for rule in rules:
        point = points.get(rule.reference)
        distance = None
        if point and rule.metric == "anchor-distance" and rule.other in points:
            distance = point.distance(points[rule.other])
        if point and rule.metric == "rectangular-edge-distance" and floorplan.outline:
            outline = floorplan.outline
            if outline.contains(point):
                distance = min(
                    point.x_mm - outline.minimum.x_mm,
                    outline.maximum.x_mm - point.x_mm,
                    point.y_mm - outline.minimum.y_mm,
                    outline.maximum.y_mm - point.y_mm,
                )
        checks.append(
            CheckResult(
                check_id=f"placement.distance.{rule.id}",
                name=rule.rationale,
                status=CheckStatus.SKIP
                if distance is None
                else CheckStatus.PASS
                if distance <= rule.maximum_mm
                else CheckStatus.FAIL,
                message=f"{rule.metric}: {distance} mm; maximum {rule.maximum_mm} mm",
                evidence=rule.evidence,
                affected_objects=tuple(x for x in (rule.reference, rule.other) if x),
            )
        )
    if not checks:
        checks.append(
            CheckResult(
                check_id="placement.rules",
                name="Placement constraints",
                status=CheckStatus.SKIP,
                message="No quantified rules supplied",
            )
        )
    return VerificationReport(results=tuple(checks), input_digest=floorplan.input_digest)


def placements_from_snapshot(snapshot, assignments: dict[str, str]) -> tuple[Placement, ...]:
    """Read native footprint anchors; these are not pad/loop/courtyard distances."""
    placements = []
    for footprint in snapshot.objects("footprint"):
        fields = [item for item in footprint if isinstance(item, list)]
        reference = next(
            (
                f[2]
                for f in fields
                if len(f) > 2 and f[:2] in (["property", "Reference"], ["fp_text", "reference"])
            ),
            None,
        )
        if reference not in assignments:
            continue
        position = next((f for f in fields if f and f[0] == "at"), None)
        layer = next((f[1] for f in fields if len(f) > 1 and f[0] == "layer"), None)
        if position is None or len(position) < 3 or layer not in {"F.Cu", "B.Cu"}:
            raise ValueError("Footprint anchor or copper side unavailable")
        placements.append(
            Placement(
                reference=reference,
                region=assignments[reference],
                point=Point(x_mm=float(position[1]), y_mm=float(position[2])),
                side="top" if layer == "F.Cu" else "bottom",
            )
        )
    if {p.reference for p in placements} != set(assignments):
        raise ValueError("Assigned component absent from snapshot")
    if len(placements) != len(assignments):
        raise ValueError("Ambiguous references across boards")
    return tuple(placements)
