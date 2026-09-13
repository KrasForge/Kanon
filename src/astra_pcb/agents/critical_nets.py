"""Critical-net inventory and explicit class-appropriate independent review coverage."""

from enum import StrEnum

from pydantic import Field

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.models.provenance import Digest


class NetClass(StrEnum):
    POWER = "power"
    CLOCK = "clock"
    DIFFERENTIAL = "differential"
    HIGH_SPEED = "high-speed"
    ANALOG_INPUT = "analog-input"
    ANALOG_OUTPUT = "analog-output"
    REFERENCE = "reference"
    SWITCH_NODE = "switch-node"
    FEEDBACK = "feedback"
    DIGITAL = "ordinary-digital"
    CONTROL = "control"


TOPICS = {
    NetClass.POWER: {"current", "voltage-drop", "thermal", "return-path"},
    NetClass.CLOCK: {"timing", "termination", "return-path", "jitter"},
    NetClass.DIFFERENTIAL: {"pair-assignment", "impedance", "skew", "return-path"},
    NetClass.HIGH_SPEED: {"timing", "impedance", "return-path"},
    NetClass.ANALOG_INPUT: {"noise", "headroom", "return-path", "protection"},
    NetClass.ANALOG_OUTPUT: {"load", "stability", "headroom", "return-path"},
    NetClass.REFERENCE: {"noise", "decoupling", "return-path"},
    NetClass.SWITCH_NODE: {"loop-geometry", "coupling", "voltage-stress"},
    NetClass.FEEDBACK: {"loop-geometry", "stability", "noise"},
    NetClass.DIGITAL: set(),
    NetClass.CONTROL: {"voltage-domain", "reset-boot"},
}


class Net(StrictModel):
    name: str = Field(min_length=1)
    classes: tuple[NetClass, ...] = Field(min_length=1)
    rationale: str = Field(min_length=1)


class NetReview(StrictModel):
    net: str
    reviewer: str = Field(min_length=1)
    input_digest: Digest
    topics: tuple[str, ...]
    evidence: tuple[str, ...] = Field(min_length=1)
    unresolved: tuple[str, ...] = ()


def check_critical_nets(
    nets: tuple[Net, ...],
    reviews: tuple[NetReview, ...],
    *,
    input_digest: Digest,
    designer: str,
    source_nets: frozenset[str],
) -> VerificationReport:
    names = [n.name for n in nets]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate net classification")
    checks = []
    unclassified = source_nets - set(names)
    unknown = set(names) - source_nets
    checks.append(
        CheckResult(
            check_id="critical-nets.inventory",
            name="Net classification completeness",
            status=CheckStatus.FAIL if unclassified or unknown else CheckStatus.PASS,
            message=(
                f"Unclassified: {sorted(unclassified)}; unknown declared nets: {sorted(unknown)}"
            ),
        )
    )
    for net in nets:
        topics = set().union(*(TOPICS[c] for c in net.classes))
        if not topics:
            continue
        evidence = [
            r
            for r in reviews
            if r.net == net.name and r.input_digest == input_digest and r.reviewer != designer
        ]
        covered = set().union(*(set(r.topics) for r in evidence))
        unresolved = any(r.unresolved for r in evidence)
        passed = topics <= covered and not unresolved
        checks.append(
            CheckResult(
                check_id=f"critical-nets.{net.name}",
                name="Critical net review coverage",
                status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                message=(
                    f"Missing topics: {sorted(topics - covered)}; unresolved findings: {unresolved}"
                ),
                affected_objects=(net.name,),
                evidence=tuple(r.model_dump_json() for r in evidence),
            )
        )
    if not source_nets:
        checks.append(
            CheckResult(
                check_id="critical-nets.empty",
                name="Source net inventory",
                status=CheckStatus.SKIP,
                message="No source nets; classification cannot establish coverage",
            )
        )
    return VerificationReport(
        results=tuple(checks), input_digest=input_digest, design_author=designer
    )
