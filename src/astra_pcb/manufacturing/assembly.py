"""Evidence-backed assembly declarations; never infer package geometry from its name."""

from typing import Literal

from pydantic import Field

from astra_pcb.manufacturing import ManufacturingProfile
from astra_pcb.models import CheckResult, StrictModel, VerificationReport


class AssemblyPart(StrictModel):
    reference: str = Field(min_length=1)
    package: str = Field(min_length=1)
    technology: Literal["BGA", "0402-imperial", "other"]
    side: Literal["top", "bottom"]
    process_review: tuple[str, ...] = ()
    courtyard_clearance_mm: float | None = None
    polarity_required: bool
    polarity_mark_verified: bool | None = None
    placement_rotation_verified: bool | None = None
    evidence: tuple[str, ...] = Field(min_length=1)


class AssemblyPlan(StrictModel):
    parts: tuple[AssemblyPart, ...]
    source_references: frozenset[str]
    fiducials_required: int = Field(ge=0)
    usable_fiducials: int = Field(ge=0)
    fiducial_evidence: tuple[str, ...] = Field(min_length=1)
    minimum_courtyard_clearance_mm: float = Field(ge=0)

    def audit(self, profile: ManufacturingProfile) -> VerificationReport:
        checks = []

        def add(key, status, message, evidence, affected=()):
            checks.append(
                CheckResult(
                    check_id="assembly." + key,
                    name="Assembly policy",
                    status=status,
                    message=message,
                    evidence=evidence,
                    affected_objects=affected,
                )
            )

        refs = [p.reference for p in self.parts]
        if len(refs) != len(set(refs)):
            raise ValueError("Duplicate assembly reference")
        add(
            "inventory",
            "PASS" if set(refs) == self.source_references and refs else "FAIL",
            "Assembly inventory must match fitted source references",
            (str(sorted(self.source_references)),),
        )
        add(
            "fiducials",
            "PASS" if self.usable_fiducials >= self.fiducials_required else "FAIL",
            f"Usable fiducials {self.usable_fiducials}; required {self.fiducials_required}",
            self.fiducial_evidence,
        )
        if profile.single_sided_assembly_preferred and len({p.side for p in self.parts}) > 1:
            add(
                "sides",
                "WARN",
                "Two-sided assembly needs cost/process review",
                self.fiducial_evidence,
            )
        for part in self.parts:
            policy = (
                profile.bga_policy
                if part.technology == "BGA"
                else profile.policy_0402
                if part.technology == "0402-imperial"
                else "allowed"
            )
            status = (
                "FAIL"
                if policy == "forbidden"
                else "WARN"
                if policy != "allowed" and not part.process_review
                else "PASS"
            )
            add(
                part.reference + ".package",
                status,
                f"Declared {part.technology}: {policy}",
                part.evidence + part.process_review,
                (part.reference,),
            )
            clearance = part.courtyard_clearance_mm
            add(
                part.reference + ".courtyard",
                "SKIP"
                if clearance is None
                else "PASS"
                if clearance >= self.minimum_courtyard_clearance_mm
                else "FAIL",
                f"Measured courtyard clearance {clearance}; "
                f"minimum {self.minimum_courtyard_clearance_mm} mm",
                part.evidence,
                (part.reference,),
            )
            for key, required, verified in (
                ("rotation", True, part.placement_rotation_verified),
                ("polarity", part.polarity_required, part.polarity_mark_verified),
            ):
                if required:
                    add(
                        part.reference + "." + key,
                        "SKIP" if verified is None else "PASS" if verified else "FAIL",
                        "Check placement/orientation against the assembly drawing",
                        part.evidence,
                        (part.reference,),
                    )
        return VerificationReport(results=tuple(checks))
