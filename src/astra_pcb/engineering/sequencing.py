"""Evidence-backed ramp, discharge and partial-power observations, not inferred waveforms."""

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.engineering.power import Sequence
from astra_pcb.models import CheckResult, StrictModel, VerificationReport


class RampRule(StrictModel):
    minimum_ramp_ms: float = Field(ge=0)
    maximum_ramp_ms: float = Field(gt=0)
    maximum_discharge_ms: float = Field(ge=0)
    maximum_off_voltage_v: float = Field(ge=0)
    partial_power_allowed: bool
    maximum_off_injection_a: float | None = Field(default=None, ge=0)
    threshold_definition: str = Field(min_length=1)
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def ordered(self):
        if self.minimum_ramp_ms > self.maximum_ramp_ms:
            raise ValueError("Reversed ramp interval")
        return self


class RampObservation(StrictModel):
    rail: str = Field(min_length=1)
    up_start_ms: float = Field(ge=0)
    up_end_ms: float = Field(ge=0)
    down_start_ms: float = Field(ge=0)
    down_end_ms: float = Field(ge=0)
    off_voltage_v: float = Field(ge=0)
    driven_while_off: bool
    off_injection_a: float | None = Field(default=None, ge=0)
    threshold_definition: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.up_end_ms < self.up_start_ms or self.down_end_ms < self.down_start_ms:
            raise ValueError("Transition ends before it starts")
        return self


class SequencingPlan(StrictModel):
    rules: dict[str, RampRule] = Field(min_length=1)
    power_up_order: tuple[Sequence, ...] = ()
    power_down_order: tuple[Sequence, ...] = ()
    observations: tuple[RampObservation, ...] = ()

    @model_validator(mode="after")
    def topology(self):
        if len({o.rail for o in self.observations}) != len(self.observations):
            raise ValueError("Duplicate ramp observation")
        if {o.rail for o in self.observations} - self.rules.keys():
            raise ValueError("Unknown observed rail")
        for order in (self.power_up_order, self.power_down_order):
            graph = {rail: set() for rail in self.rules}
            for edge in order:
                if edge.before not in graph or edge.after not in graph:
                    raise ValueError("Sequence references unknown rail")
                graph[edge.before].add(edge.after)
            visiting, done = set(), set()

            def visit(rail):
                if rail in visiting:
                    raise ValueError("Contradictory cyclic sequence")
                if rail in done:
                    return
                visiting.add(rail)
                for following in graph[rail]:
                    visit(following)
                visiting.remove(rail)
                done.add(rail)

            for rail in graph:
                visit(rail)
        return self

    def audit(self) -> VerificationReport:
        observations = {o.rail: o for o in self.observations}
        checks = []
        for rail, rule in self.rules.items():
            observed = observations.get(rail)
            faults, unknown = [], []
            if observed is None:
                unknown.append("Missing waveform observation")
            elif observed.threshold_definition != rule.threshold_definition:
                unknown.append("Observed timing thresholds differ from device rule")
            else:
                ramp = observed.up_end_ms - observed.up_start_ms
                discharge = observed.down_end_ms - observed.down_start_ms
                if not rule.minimum_ramp_ms <= ramp <= rule.maximum_ramp_ms:
                    faults.append("Power-up ramp outside device limits")
                if (
                    discharge > rule.maximum_discharge_ms
                    or observed.off_voltage_v > rule.maximum_off_voltage_v
                ):
                    faults.append("Discharge/off-voltage limit exceeded")
                if observed.driven_while_off:
                    if not rule.partial_power_allowed:
                        faults.append("I/O driven while its rail is off")
                    elif rule.maximum_off_injection_a is None or observed.off_injection_a is None:
                        unknown.append("Partial-power injection limit/measurement missing")
                    elif observed.off_injection_a > rule.maximum_off_injection_a:
                        faults.append("Partial-power injection exceeds device limit")
            checks.append(
                CheckResult(
                    check_id="fpga.ramp." + rail,
                    name="Rail ramp/discharge/partial-power",
                    status="FAIL" if faults else "SKIP" if unknown else "PASS",
                    message="; ".join(faults + unknown)
                    or "Declared waveform satisfies cited rail limits",
                    evidence=(rule.evidence.model_dump_json(),)
                    + ((observed.model_dump_json(),) if observed else ()),
                    affected_objects=(rail,),
                )
            )
        for direction, order in (("up", self.power_up_order), ("down", self.power_down_order)):
            for i, edge in enumerate(order):
                a, b = observations.get(edge.before), observations.get(edge.after)
                delay = (
                    None
                    if a is None or b is None
                    else (
                        b.up_start_ms - a.up_end_ms
                        if direction == "up"
                        else b.down_start_ms - a.down_end_ms
                    )
                )
                passed = (
                    delay is not None
                    and edge.minimum_delay_ms <= delay
                    and (edge.maximum_delay_ms is None or delay <= edge.maximum_delay_ms)
                )
                checks.append(
                    CheckResult(
                        check_id=f"fpga.ramp-order.{direction}.{i}",
                        name="Nonoverlapping rail transition order",
                        status="SKIP" if delay is None else "PASS" if passed else "FAIL",
                        message=f"End-to-start delay {delay} ms; required {edge.minimum_delay_ms}..{edge.maximum_delay_ms}",
                        evidence=(edge.model_dump_json(),),
                        affected_objects=(edge.before, edge.after),
                    )
                )
        return VerificationReport(results=tuple(checks))
