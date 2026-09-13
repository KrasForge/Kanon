"""Declared clock topology, load/fanout, termination and domain expectations."""

from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class ClockNode(StrictModel):
    id: str
    source: str | None = None
    frequency_hz: float = Field(gt=0)
    ratio: float = Field(default=1, gt=0)
    maximum_fanout: int = Field(default=1, ge=1)
    domain: str
    domain_relation: Literal["same", "derived"] = "same"
    termination: str | None = None
    expected_termination: str | None = None
    jitter_ps_rms: float | None = Field(default=None, ge=0)
    jitter_limit_ps_rms: float | None = Field(default=None, ge=0)
    evidence: DatasheetEvidence


class ClockTree(StrictModel):
    nodes: tuple[ClockNode, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def graph(self):
        nodes = {n.id: n for n in self.nodes}
        if len(nodes) != len(self.nodes):
            raise ValueError("Duplicate clock nodes")
        for node in self.nodes:
            visited = set()
            current = node
            while current.source:
                if current.id in visited:
                    raise ValueError("Clock cycle")
                visited.add(current.id)
                if current.source not in nodes:
                    raise ValueError("Unknown clock source")
                current = nodes[current.source]
        return self

    def audit(self) -> VerificationReport:
        nodes = {n.id: n for n in self.nodes}
        results = []
        for node in self.nodes:
            failures = []
            unknown = []
            fanout = sum(n.source == node.id for n in self.nodes)
            if fanout > node.maximum_fanout:
                failures.append("Fanout exceeds declared drive limit")
            if node.source:
                if node.domain_relation not in {"same", "derived"}:
                    failures.append("Unrecognized clock-domain relation")
                if node.domain_relation == "same" and nodes[node.source].domain != node.domain:
                    failures.append("Undeclared clock-domain transition")
                expected = nodes[node.source].frequency_hz * node.ratio
                if abs(node.frequency_hz - expected) > max(1e-9, expected * 1e-9):
                    failures.append("Frequency/ratio mismatch")
            if node.expected_termination is None:
                unknown.append("Termination expectation unknown")
            elif node.termination != node.expected_termination:
                failures.append("Termination mismatch")
            if node.jitter_limit_ps_rms is not None:
                if node.jitter_ps_rms is None:
                    unknown.append("Jitter observation unknown")
                elif node.jitter_ps_rms > node.jitter_limit_ps_rms:
                    failures.append("Jitter budget exceeded")
            results.append(
                CheckResult(
                    check_id=f"clock.{node.id}",
                    name="Clock topology",
                    status=CheckStatus.FAIL
                    if failures
                    else CheckStatus.SKIP
                    if unknown
                    else CheckStatus.PASS,
                    message="; ".join(failures + unknown)
                    or f"Declared clock topology matches domain {node.domain}",
                    affected_objects=(node.id,),
                    evidence=(node.model_dump_json(),),
                )
            )
        return VerificationReport(results=tuple(results))
