"""Fail-closed policy aggregation with optional externally authenticated attestations."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.release.attestations import Attestation, TrustedSigner


class ReleaseGate(StrictModel):
    check_id: str = Field(min_length=1)
    mode: Literal["AUTOMATED", "MANUAL"]
    mandatory: bool = True
    allow_human_waiver: bool = False


class GateConfig(StrictModel):
    gates: tuple[ReleaseGate, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [g.check_id for g in self.gates]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate gate IDs")
        if not any(g.mandatory for g in self.gates):
            raise ValueError("at least one mandatory gate required")
        return self


def evaluate(
    config: GateConfig,
    report: VerificationReport,
    *,
    expected_digest: str | None = None,
    attestations: tuple[Attestation, ...] = (),
    trusted: dict[str, TrustedSigner] | None = None,
    now: datetime | None = None,
) -> VerificationReport:
    ids = [r.check_id for r in report.results]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate result IDs")
    if expected_digest is not None and report.input_digest != expected_digest:
        raise ValueError("Verification input identity does not match current design")
    by_id = {r.check_id: r for r in report.results}
    decisions = {}
    for attestation in attestations:
        if not expected_digest:
            raise ValueError("Attestations require an independently computed input identity")
        attestation.verify(
            trusted or {},
            now=now or datetime.now(UTC),
            digest=expected_digest,
            design_author=report.design_author,
        )
        if attestation.check_id in decisions:
            raise ValueError("Duplicate/conflicting attestations")
        decisions[attestation.check_id] = attestation
    gate_ids = {g.check_id for g in config.gates}
    if set(decisions) - gate_ids:
        raise ValueError("Attestation targets unknown gate")
    results = []
    for gate in config.gates:
        result = by_id.get(gate.check_id)
        attestation = decisions.get(gate.check_id)
        passed = (
            gate.mode == "AUTOMATED" and result is not None and result.status == CheckStatus.PASS
        )
        message = (
            "Gate satisfied"
            if passed
            else (f"Unsatisfied gate: {result.status if result else 'missing result/approval'}")
        )
        evidence = result.evidence if result else ()
        if attestation:
            if attestation.purpose == "waiver" and gate.allow_human_waiver:
                passed = True
                message = f"Human waiver by {attestation.issuer}: {attestation.reason}"
            elif attestation.purpose == "approval" and gate.mode == "MANUAL":
                passed = True
                message = f"Independent approval by {attestation.issuer}"
            else:
                raise ValueError("Attestation purpose is not allowed by gate policy")
            evidence += (*attestation.evidence, attestation.model_dump_json())
        results.append(
            CheckResult(
                check_id=gate.check_id,
                name=gate.check_id,
                status=CheckStatus.PASS
                if passed
                else (CheckStatus.FAIL if gate.mandatory else CheckStatus.WARN),
                message=message,
                evidence=evidence,
                source="release-gate",
            )
        )
    return VerificationReport(
        results=tuple(results),
        input_digest=report.input_digest,
        design_author=report.design_author,
        tool_versions=report.tool_versions,
    )
