"""Manufacturing policy and measured-feature checks; no order/upload operations."""

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class Copper(StrictModel):
    outer: float = Field(gt=0)
    inner: float = Field(gt=0)


class Soldermask(StrictModel):
    color: str
    minimum_web_mm: float = Field(ge=0)


class ManufacturingProfile(StrictModel):
    name: str = Field(min_length=1)
    status: Literal["UNQUALIFIED", "QUALIFIED"] = "UNQUALIFIED"
    capabilities_checked_at: datetime | None = None
    source_url: str = Field(min_length=1)
    qualification_evidence: tuple[str, ...] = ()
    notice: str
    layer_count: int = Field(ge=2, le=32)
    board_thickness_mm: float = Field(gt=0)
    copper_oz: Copper
    minimum_trace_mm: float = Field(gt=0)
    minimum_spacing_mm: float = Field(gt=0)
    via_drill_mm: float = Field(gt=0)
    annular_ring_mm: float = Field(gt=0)
    copper_edge_clearance_mm: float = Field(gt=0)
    soldermask: Soldermask
    preferred_package: str
    bga_policy: Literal["forbidden", "requires_explicit_process_review", "allowed"]
    policy_0402: Literal["forbidden", "requires_assembly_review", "allowed"]
    single_sided_assembly_preferred: bool
    sourcing_preferences: tuple[str, ...]
    stackup: str = Field(min_length=1)

    @model_validator(mode="after")
    def qualification(self):
        if self.layer_count % 2:
            raise ValueError("Even layer count required by this profile model")
        if self.capabilities_checked_at and self.capabilities_checked_at.tzinfo is None:
            raise ValueError("Capability verification needs a timezone")
        if self.status == "QUALIFIED" and (
            not self.capabilities_checked_at or not self.qualification_evidence
        ):
            raise ValueError("Qualified profile needs dated capability evidence")
        return self

    def check(self, now: datetime | None = None) -> CheckResult:
        now = now or datetime.now(UTC)
        qualified = (
            self.status == "QUALIFIED"
            and self.capabilities_checked_at is not None
            and timedelta(0) <= now - self.capabilities_checked_at <= timedelta(days=90)
        )
        return CheckResult(
            check_id="manufacturing.profile",
            name="Manufacturing profile qualification",
            status=CheckStatus.PASS if qualified else CheckStatus.FAIL,
            message="Dated capability evidence present; independent DFM review still required"
            if qualified
            else "Unqualified, expired or future-dated manufacturing profile",
            evidence=(self.model_dump_json(),),
            source=self.source_url,
        )


class Feature(StrictModel):
    id: str = Field(min_length=1)
    kind: Literal["trace", "spacing", "via-drill", "annular-ring", "edge-clearance", "mask-web"]
    minimum_mm: float = Field(ge=0)
    source_object: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(min_length=1)


def check_dfm(
    profile: ManufacturingProfile,
    features: tuple[Feature, ...],
    *,
    layer_count: int,
    thickness_mm: float,
) -> VerificationReport:
    limits = {
        "trace": profile.minimum_trace_mm,
        "spacing": profile.minimum_spacing_mm,
        "via-drill": profile.via_drill_mm,
        "annular-ring": profile.annular_ring_mm,
        "edge-clearance": profile.copper_edge_clearance_mm,
        "mask-web": profile.soldermask.minimum_web_mm,
    }
    checks = [
        profile.check(),
        CheckResult(
            check_id="dfm.stackup",
            name="Declared stackup match",
            status=CheckStatus.PASS
            if layer_count == profile.layer_count
            and abs(thickness_mm - profile.board_thickness_mm) < 1e-6
            else CheckStatus.FAIL,
            message=f"Declared board: {layer_count} layers, {thickness_mm} mm",
        ),
    ]
    if len({f.id for f in features}) != len(features):
        raise ValueError("Duplicate feature IDs")
    for feature in features:
        limit = limits[feature.kind]
        checks.append(
            CheckResult(
                check_id=f"dfm.{feature.id}",
                name=f"{feature.kind} minimum",
                status=CheckStatus.PASS if feature.minimum_mm >= limit else CheckStatus.FAIL,
                message=f"Measured {feature.minimum_mm} mm; minimum {limit} mm",
                affected_objects=(feature.source_object,),
                evidence=feature.evidence,
            )
        )
    if not features:
        checks.append(
            CheckResult(
                check_id="dfm.features",
                name="Measured manufacturing features",
                status=CheckStatus.SKIP,
                message="No measured features; DRC and independent DFM review required",
            )
        )
    return VerificationReport(results=tuple(checks))
