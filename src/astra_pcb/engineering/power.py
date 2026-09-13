"""Rail dependency/current budgets and evidence-backed regulator corner calculations."""

from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class Rail(StrictModel):
    id: str = Field(min_length=1)
    source: str | None = None
    minimum_v: float = Field(gt=0)
    nominal_v: float = Field(gt=0)
    maximum_v: float = Field(gt=0)
    current_limit_a: float = Field(gt=0)
    conversion: Literal["source", "direct", "linear", "switching"]
    efficiency_min: float | None = Field(default=None, gt=0, le=1)
    quiescent_a: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_rail(self):
        if not self.minimum_v <= self.nominal_v <= self.maximum_v:
            raise ValueError("Rail nominal voltage must lie inside min/max range")
        if (self.source is None) != (self.conversion == "source"):
            raise ValueError("Source rails and converted rails need consistent dependencies")
        if self.conversion == "switching" and self.efficiency_min is None:
            raise ValueError("Switching current propagation requires minimum efficiency")
        return self


class Load(StrictModel):
    id: str = Field(min_length=1)
    rail: str
    expected_a: float = Field(ge=0)
    peak_a: float = Field(ge=0)

    @model_validator(mode="after")
    def ordered(self):
        if self.expected_a > self.peak_a:
            raise ValueError("Expected current exceeds peak")
        return self


class Sequence(StrictModel):
    before: str
    after: str
    minimum_delay_ms: float = Field(default=0, ge=0)
    maximum_delay_ms: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def ordered(self):
        if self.maximum_delay_ms is not None and self.maximum_delay_ms < self.minimum_delay_ms:
            raise ValueError("Inverted sequencing delay")
        return self


class PowerTree(StrictModel):
    rails: tuple[Rail, ...] = Field(min_length=1)
    loads: tuple[Load, ...]
    sequencing: tuple[Sequence, ...] = ()

    @model_validator(mode="after")
    def graph(self):
        rails = {r.id: r for r in self.rails}
        if len(rails) != len(self.rails) or len({x.id for x in self.loads}) != len(self.loads):
            raise ValueError("Duplicate rail/load IDs")
        if any(load.rail not in rails for load in self.loads):
            raise ValueError("Load references unknown rail")
        edges = {r.id: ([r.source] if r.source else []) for r in self.rails}
        for sequence in self.sequencing:
            if sequence.after not in rails or sequence.before not in rails:
                raise ValueError("Sequence references unknown rail")
            edges[sequence.after].append(sequence.before)

        def visit(name, stack):
            if name not in rails:
                raise ValueError("Unknown upstream rail")
            if name in stack:
                raise ValueError("Cyclic supply/sequencing dependency")
            for previous in edges[name]:
                visit(previous, {*stack, name})

        for name in rails:
            visit(name, set())
        return self

    def demand(self, rail_id: str, *, peak: bool = True) -> float:
        rails = {r.id: r for r in self.rails}
        parent = rails[rail_id]
        current = sum(x.peak_a if peak else x.expected_a for x in self.loads if x.rail == rail_id)
        for child in self.rails:
            if child.source == rail_id:
                demand = self.demand(child.id, peak=peak)
                if child.conversion == "switching":
                    demand *= child.maximum_v / (parent.minimum_v * child.efficiency_min)
                current += demand + child.quiescent_a
        return current

    def audit(self) -> VerificationReport:
        return VerificationReport(
            results=tuple(
                CheckResult(
                    check_id=f"power.current.{rail.id}",
                    name=f"{rail.id} current budget",
                    status=CheckStatus.PASS
                    if self.demand(rail.id) <= rail.current_limit_a
                    else CheckStatus.FAIL,
                    message=(
                        f"Worst-case demand {self.demand(rail.id):.6g} A; "
                        f"limit {rail.current_limit_a} A"
                    ),
                    affected_objects=(rail.id,),
                    evidence=(self.model_dump_json(),),
                    source="power-tree",
                )
                for rail in self.rails
            )
        )


class Regulator(StrictModel):
    reference: str
    output_rail: str
    input_minimum_v: float = Field(gt=0)
    input_maximum_v: float = Field(gt=0)
    dropout_v: float = Field(default=0, ge=0)
    ambient_maximum_c: float
    junction_maximum_c: float
    theta_ja_c_per_w: float | None = Field(default=None, gt=0)
    thermal_conditions: str | None = None
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def ordered(self):
        if self.input_minimum_v > self.input_maximum_v:
            raise ValueError("Inverted regulator input limits")
        if self.ambient_maximum_c < -273.15 or self.junction_maximum_c <= self.ambient_maximum_c:
            raise ValueError("Invalid ambient/junction temperature limits")
        return self


def check_regulator(tree: PowerTree, regulator: Regulator) -> VerificationReport:
    rails = {r.id: r for r in tree.rails}
    output = rails[regulator.output_rail]
    if output.source is None or output.conversion not in {"linear", "switching"}:
        raise ValueError("Regulator output must be a declared converted rail")
    source = rails[output.source]
    current = tree.demand(output.id)
    limits_ok = regulator.input_minimum_v <= source.minimum_v and (
        source.maximum_v <= regulator.input_maximum_v
    )
    if output.conversion == "linear":
        limits_ok &= source.minimum_v >= output.maximum_v + regulator.dropout_v
        loss = max(0, source.maximum_v - output.minimum_v) * current
    else:
        loss = output.maximum_v * current * (1 / output.efficiency_min - 1)
    loss += source.maximum_v * output.quiescent_a
    evidence = (regulator.evidence.model_dump_json(), tree.model_dump_json())
    results = [
        CheckResult(
            check_id=f"power.regulator.{regulator.reference}.range",
            name="Regulator input/headroom",
            status=CheckStatus.PASS if limits_ok else CheckStatus.FAIL,
            message=(
                f"Input [{source.minimum_v}, {source.maximum_v}] V; worst-case loss {loss:.6g} W"
            ),
            evidence=evidence,
            affected_objects=(regulator.reference,),
        )
    ]
    thermal_status = CheckStatus.SKIP
    message = "Invalid electrical range or missing applicable documented thermal parameter"
    if limits_ok and regulator.theta_ja_c_per_w is not None and regulator.thermal_conditions:
        junction = regulator.ambient_maximum_c + loss * regulator.theta_ja_c_per_w
        thermal_status = (
            CheckStatus.PASS if junction < regulator.junction_maximum_c else CheckStatus.FAIL
        )
        message = f"Estimated junction {junction:.6g} C; limit {regulator.junction_maximum_c} C"
    results.append(
        CheckResult(
            check_id=f"power.regulator.{regulator.reference}.thermal",
            name="Regulator thermal estimate",
            status=thermal_status,
            message=message,
            evidence=evidence,
            affected_objects=(regulator.reference,),
            source="first-order thermal model",
        )
    )
    return VerificationReport(results=tuple(results))
