"""Declarative scalar assertions and reproducible ngspice report construction."""

import re
from pathlib import Path

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.simulation import assert_limit, measurements, simulate


class Limits(StrictModel):
    min: float
    max: float

    @model_validator(mode="after")
    def ordered(self):
        if self.min > self.max:
            raise ValueError("Inverted assertion interval")
        return self


class SimulationJob(StrictModel):
    netlist: str = Field(min_length=1)
    description: str = Field(min_length=1)
    assumptions: tuple[str, ...] = Field(min_length=1)
    assertions: dict[str, Limits] = Field(min_length=1)

    @model_validator(mode="after")
    def safe_names(self):
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
    result = simulate(netlist, output, executable)
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
        checks.extend(
            assert_limit(name, values, limit.min, limit.max).model_copy(
                update={"evidence": (result.model_dump_json(),)}
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
        input_digest=result.input_digest,
        tool_versions={"ngspice": result.tool_version or "unknown"},
    )
