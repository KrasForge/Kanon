"""Declarative scalar assertions and reproducible ngspice report construction."""

import re
from pathlib import Path

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.models.provenance import canonical_digest
from astra_pcb.simulation import assert_limit, measurements, simulate
from astra_pcb.simulation.models import ModelFile

UNITS = {
    "V": ("voltage", 1),
    "mV": ("voltage", 0.001),
    "A": ("current", 1),
    "mA": ("current", 0.001),
    "Hz": ("frequency", 1),
    "kHz": ("frequency", 1000),
    "s": ("time", 1),
    "ms": ("time", 0.001),
    "dB": ("gain", 1),
    "1": ("ratio", 1),
}


class Limits(StrictModel):
    unit: str
    min: float
    max: float

    @model_validator(mode="after")
    def ordered(self):
        if self.unit not in UNITS:
            raise ValueError("Unsupported assertion unit")
        if self.min > self.max:
            raise ValueError("Inverted assertion interval")
        return self


class SimulationJob(StrictModel):
    netlist: str = Field(min_length=1)
    description: str = Field(min_length=1)
    assumptions: tuple[str, ...] = Field(min_length=1)
    assertions: dict[str, Limits] = Field(min_length=1)
    measurement_units: dict[str, str]
    models: tuple[ModelFile, ...] = ()

    @model_validator(mode="after")
    def safe_names(self):
        if set(self.measurement_units) != set(self.assertions):
            raise ValueError("Every assertion needs declared measurement units")
        if any(unit not in UNITS for unit in self.measurement_units.values()):
            raise ValueError("Unsupported measurement unit")
        if any(
            UNITS[self.measurement_units[n]][0] != UNITS[lim.unit][0]
            for n, lim in self.assertions.items()
        ):
            raise ValueError("Measurement/assertion dimensions differ")
        if any(not re.fullmatch(r"[A-Za-z]\w*", name) for name in self.assertions):
            raise ValueError("Assertion names must be ngspice scalar identifiers")
        if Path(self.netlist).is_absolute() or ".." in Path(self.netlist).parts:
            raise ValueError("Job netlist must be relative to job directory")
        return self


def run_job(
    job: SimulationJob, root: Path, output: Path, *, executable: str = "ngspice"
) -> VerificationReport:
    netlist = (root / job.netlist).resolve()
    if not netlist.is_relative_to(root.resolve()):
        raise ValueError("Netlist escapes job directory")
    result = simulate(netlist, output, executable, models=job.models)
    log = output.read_text(errors="replace") if output.is_file() else ""
    status = CheckStatus.ERROR if result.error or result.exit_code != 0 else CheckStatus.PASS
    if status == CheckStatus.PASS and re.search(r"^\s*warning\b", log, re.I | re.M):
        status = CheckStatus.WARN
    checks = [
        CheckResult(
            check_id="simulation.execution",
            name="ngspice execution",
            status=status,
            message=result.error
            or (
                "Simulation completed with warnings"
                if status == CheckStatus.WARN
                else f"Process exit {result.exit_code}"
            ),
            evidence=(result.model_dump_json(), job.model_dump_json()),
            source="ngspice",
        )
    ]
    if status != CheckStatus.ERROR:
        values = measurements(log)
        values = {
            name: value
            * UNITS[job.measurement_units[name]][1]
            / UNITS[job.assertions[name].unit][1]
            for name, value in values.items()
            if name in job.assertions
        }
        checks.extend(
            assert_limit(name, values, limit.min, limit.max).model_copy(
                update={"evidence": (result.model_dump_json(), f"Unit: {limit.unit}")}
            )
            for name, limit in job.assertions.items()
        )
    else:
        checks.extend(
            CheckResult(
                check_id=f"simulation.{name}",
                name=name,
                status=CheckStatus.SKIP,
                message="Simulation failed; no trustworthy measurement",
            )
            for name in job.assertions
        )
    return VerificationReport(
        results=tuple(checks),
        input_digest=canonical_digest(
            {"process_inputs": result.input_digest, "job": job.model_dump(mode="json")}
        ),
        tool_versions={"ngspice": result.tool_version or "unknown"},
    )
