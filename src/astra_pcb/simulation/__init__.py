"""ngspice batch execution and scalar measurement limits."""

import math
import re
from pathlib import Path

from astra_pcb.models import CheckResult, CheckStatus
from astra_pcb.verification.process import ProcessResult, run


def simulate(netlist: Path, output: Path, executable: str = "ngspice") -> ProcessResult:
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    return run(
        [executable, "-b", "-o", str(output.resolve()), str(netlist.resolve())],
        timeout=120,
        artifacts=(output,),
    )


def measurements(text: str) -> dict[str, float]:
    values = {}
    for name, value in re.findall(r"^\s*([\w]+)\s*=\s*([^\s]+)", text, re.MULTILINE):
        try:
            values[name] = float(value)
        except ValueError:
            continue
    return values


def assert_limit(
    name: str, values: dict[str, float], minimum: float, maximum: float
) -> CheckResult:
    if not all(math.isfinite(v) for v in (minimum, maximum)) or minimum > maximum:
        raise ValueError("invalid finite limit range")
    value = values.get(name)
    status = (
        CheckStatus.ERROR
        if value is None or not math.isfinite(value)
        else (CheckStatus.PASS if minimum <= value <= maximum else CheckStatus.FAIL)
    )
    return CheckResult(
        check_id=f"simulation.{name}",
        name=name,
        status=status,
        message=f"Measured {value}; required [{minimum}, {maximum}]",
        source="ngspice measurement",
    )
