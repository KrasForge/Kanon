"""Evidence-backed alternate qualification, separate from permission to substitute."""

from typing import Literal

from pydantic import Field

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel


class Compatibility(StrictModel):
    criterion: Literal[
        "pinout", "electrical", "footprint", "thermal", "firmware", "assembly", "lifecycle"
    ]
    compatible: bool | None
    explanation: str = Field(min_length=1)
    evidence: tuple[DatasheetEvidence, ...] = Field(min_length=1)


class Alternate(StrictModel):
    original_mpn: str = Field(min_length=1)
    original_manufacturer: str = Field(min_length=1)
    candidate_mpn: str = Field(min_length=1)
    candidate_manufacturer: str = Field(min_length=1)
    assessments: tuple[Compatibility, ...]
    design_context: str = Field(min_length=1)

    def check(self) -> CheckResult:
        by_criterion = {a.criterion: a for a in self.assessments}
        if len(by_criterion) != len(self.assessments):
            raise ValueError("Duplicate alternate criteria")
        required = {
            "pinout",
            "electrical",
            "footprint",
            "thermal",
            "firmware",
            "assembly",
            "lifecycle",
        }
        missing = required - by_criterion.keys()
        failures = [a.criterion for a in self.assessments if a.compatible is False]
        unknown = [a.criterion for a in self.assessments if a.compatible is None]
        return CheckResult(
            check_id="bom.alternate",
            name="Alternate compatibility evidence",
            status=CheckStatus.FAIL
            if failures
            else CheckStatus.SKIP
            if missing or unknown
            else CheckStatus.PASS,
            message=f"Incompatible: {failures}; unassessed: {sorted(set(missing) | set(unknown))}. "
            "This assessment does not authorize component substitution.",
            evidence=(self.model_dump_json(),),
            affected_objects=(self.original_mpn, self.candidate_mpn),
        )
