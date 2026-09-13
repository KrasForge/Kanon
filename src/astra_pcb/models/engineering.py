"""Versioned review and hardware decision records with stable finding identities."""

import json
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import Digest


class Finding(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    severity: Literal["blocker", "major", "minor", "observation"]
    evidence: tuple[str, ...] = Field(min_length=1)
    affected_subsystems: tuple[str, ...] = ()
    affected_nets: tuple[str, ...] = ()
    affected_components: tuple[str, ...] = ()
    explanation: str = Field(min_length=1)
    suggested_remediation: str = Field(min_length=1)
    status: Literal["open", "in_progress", "resolved", "accepted"] = "open"
    resolution_evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def require_resolution(self):
        if self.status in {"resolved", "accepted"} and not self.resolution_evidence:
            raise ValueError("Resolution or risk acceptance evidence required")
        return self

    def transition(self, status: str, evidence: tuple[str, ...] = ()) -> "Finding":
        legal = {
            "open": {"in_progress", "accepted"},
            "in_progress": {"open", "resolved", "accepted"},
            "resolved": {"open"},
            "accepted": {"open"},
        }
        if status not in legal[self.status]:
            raise ValueError(f"Illegal finding transition: {self.status} -> {status}")
        return Finding.model_validate(
            {**self.model_dump(), "status": status, "resolution_evidence": evidence}
        )


class Review(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    reviewer: str = Field(min_length=1)
    design_revision: str = Field(min_length=1)
    snapshot_sha256: Digest
    scope: tuple[str, ...] = Field(min_length=1)
    findings: tuple[Finding, ...]
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def unique_findings(self):
        ids = [f.id for f in self.findings]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate finding IDs")
        return self

    @property
    def has_blockers(self) -> bool:
        return bool(self.limitations) or any(
            f.severity in {"blocker", "major"} and f.status != "resolved" for f in self.findings
        )


class Decision(StrictModel):
    id: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    context: str = Field(min_length=1)
    alternatives: tuple[str, ...] = Field(min_length=1)
    evidence: tuple[DatasheetEvidence, ...] = Field(min_length=1)
    calculations: tuple[str, ...]
    risks: tuple[str, ...]
    chosen_solution: str = Field(min_length=1)
    consequences: tuple[str, ...]
    invalidated_by: tuple[str, ...] = Field(min_length=1)

    def to_markdown(self) -> str:
        # The canonical JSON block is authoritative; prose is rendered for human review.
        sections = "\n\n".join(
            f"## {key.replace('_', ' ').title()}\n\n{value}"
            for key, value in self.model_dump(mode="json").items()
        )
        return f"# {self.id}\n\n{sections}\n\n```json\n{self.model_dump_json(indent=2)}\n```\n"

    @classmethod
    def from_markdown(cls, text: str) -> "Decision":
        blocks = text.split("```json\n")
        if len(blocks) != 2:
            raise ValueError("Exactly one canonical JSON block required")
        return cls.model_validate(json.loads(blocks[1].split("\n```", 1)[0]))
