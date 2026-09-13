"""Rule-driven decoupling, connector protection and test-point coverage audits."""

from pydantic import Field

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class Capacitor(StrictModel):
    reference: str
    rail: str
    local_to: str
    effective_f: float = Field(gt=0)
    distance_mm: float | None = Field(default=None, ge=0)
    evidence: DatasheetEvidence


class DecouplingRule(StrictModel):
    component: str
    power_pin: str
    rail: str
    minimum_effective_f: float = Field(gt=0)
    minimum_count: int = Field(default=1, ge=1)
    maximum_distance_mm: float | None = Field(default=None, gt=0)
    evidence: DatasheetEvidence


def check_decoupling(
    rules: tuple[DecouplingRule, ...],
    capacitors: tuple[Capacitor, ...],
    available_references: frozenset[str],
) -> VerificationReport:
    results = []
    if len({c.reference for c in capacitors}) != len(capacitors):
        raise ValueError("Duplicate capacitor references")
    for rule in rules:
        local = [
            c
            for c in capacitors
            if c.rail == rule.rail
            and c.local_to == rule.component
            and c.reference in available_references
        ]
        known = [
            c
            for c in local
            if rule.maximum_distance_mm is None
            or (c.distance_mm is not None and c.distance_mm <= rule.maximum_distance_mm)
        ]
        unknown = any(c.distance_mm is None for c in local) and rule.maximum_distance_mm is not None
        passed = (
            rule.component in available_references
            and len(known) >= rule.minimum_count
            and sum(c.effective_f for c in known) >= rule.minimum_effective_f
        )
        status = CheckStatus.PASS if passed else CheckStatus.SKIP if unknown else CheckStatus.FAIL
        results.append(
            CheckResult(
                check_id=f"decoupling.{rule.component}.{rule.power_pin}",
                name="Local decoupling rule",
                status=status,
                message=(
                    f"{len(known)} qualifying capacitors; {sum(c.effective_f for c in known):.6g} F"
                ),
                evidence=(
                    rule.evidence.model_dump_json(),
                    *(c.evidence.model_dump_json() for c in local),
                ),
                affected_objects=(rule.component, rule.power_pin, rule.rail),
                source="declared decoupling",
            )
        )
    if not results:
        results.append(
            CheckResult(
                check_id="decoupling",
                name="Decoupling",
                status=CheckStatus.SKIP,
                message="No rules supplied",
            )
        )
    return VerificationReport(results=tuple(results))


class Protection(StrictModel):
    reference: str
    feature: str
    nets: tuple[str, ...] = Field(min_length=1)
    evidence: DatasheetEvidence


class ConnectorRule(StrictModel):
    reference: str
    interface: str
    required: dict[str, tuple[str, ...]] = Field(min_length=1)


def check_protection(
    rules: tuple[ConnectorRule, ...],
    devices: tuple[Protection, ...],
    available_references: frozenset[str],
) -> VerificationReport:
    results = []
    for rule in rules:
        for feature, required_nets in rule.required.items():
            covered = {
                net
                for d in devices
                if d.feature == feature and d.reference in (available_references)
                for net in d.nets
            }
            missing = set(required_nets) - covered
            passed = not missing and rule.reference in available_references
            results.append(
                CheckResult(
                    check_id=f"protection.{rule.reference}.{feature}",
                    name=f"{rule.interface} {feature}",
                    status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                    message=f"Uncovered nets: {sorted(missing)}; connector present: "
                    f"{rule.reference in available_references}",
                    evidence=tuple(
                        d.evidence.model_dump_json() for d in devices if d.feature == feature
                    ),
                    affected_objects=(rule.reference, *required_nets),
                    source="declared protection topology",
                )
            )
    return VerificationReport(results=tuple(results))


class TestPoint(StrictModel):
    __test__ = False
    reference: str
    net: str
    accessible: bool | None = None
    probe_clearance_mm: float | None = Field(default=None, ge=0)


def check_testpoints(
    required: dict[str, float], points: tuple[TestPoint, ...]
) -> VerificationReport:
    results = []
    for net, clearance in required.items():
        if clearance <= 0:
            raise ValueError("Positive probe clearance required")
        candidates = [p for p in points if p.net == net]
        good = any(
            p.accessible
            and p.probe_clearance_mm is not None
            and (p.probe_clearance_mm >= clearance)
            for p in candidates
        )
        unknown = any(p.accessible is None or p.probe_clearance_mm is None for p in candidates)
        status = CheckStatus.PASS if good else CheckStatus.SKIP if unknown else CheckStatus.FAIL
        results.append(
            CheckResult(
                check_id=f"testpoint.{net}",
                name="Test-point coverage",
                status=status,
                message=f"Requires accessible point with {clearance} mm clearance",
                affected_objects=(net, *(p.reference for p in candidates)),
                evidence=tuple(p.model_dump_json() for p in candidates),
            )
        )
    return VerificationReport(results=tuple(results))
