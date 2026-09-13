"""ngspice batch execution and scalar measurement limits."""

import math
import re
import tempfile
from pathlib import Path

from astra_pcb.models import CheckResult, CheckStatus
from astra_pcb.models.provenance import file_digest
from astra_pcb.simulation.models import ModelFile, flatten
from astra_pcb.verification.process import ProcessResult, run


def simulate(
    netlist: Path, output: Path, executable: str = "ngspice", *, models: tuple[ModelFile, ...] = ()
) -> ProcessResult:
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    command = [executable, "-n", "-b", "-o", str(output.resolve()), str(netlist.resolve())]
    if not netlist.is_file():
        return ProcessResult(command=tuple(command), exit_code=None, error="Missing netlist")
    try:
        content, digest, input_hashes = flatten(netlist, models)
    except (OSError, ValueError) as exc:
        return ProcessResult(command=tuple(command), exit_code=None, error=str(exc))
    # SPICE control blocks can execute shell commands; admit only analysis/math controls.
    # Includes are flattened only after their local provenance and digest are checked.
    control = False
    for line in content.splitlines()[1:]:
        stripped = line.strip().lower()
        if not stripped or stripped.startswith("*"):
            continue
        token = stripped.split()[0]
        if token == ".control":
            control = True
        elif token == ".endc":
            control = False
        elif (
            token in {".include", ".inc", ".lib", ".hdl"}
            or (control and token not in {"ac", "tran", "op", "let", "meas", "measure", "quit"})
            or ";" in stripped
            or "`" in stripped
        ):
            return ProcessResult(
                command=tuple(command),
                exit_code=None,
                error="External model or unsupported SPICE directive; flatten/audit first",
            )
    version = run([executable, "--version"], timeout=10)
    match = re.search(r"ngspice-(\d+)", version.stdout + version.stderr, re.I)
    if version.error or version.exit_code != 0 or not match or int(match[1]) < 42:
        return ProcessResult(
            command=tuple(command),
            exit_code=version.exit_code,
            error=version.error or "Unsupported/unrecognized ngspice version (requires >=42)",
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="astra-spice-") as directory:
        staged = Path(directory) / "input.cir"
        staged.write_text(content)
        command[-1] = str(staged)
        result = run(command, cwd=Path(directory), timeout=120, artifacts=(output.resolve(),))
    errors = []
    if not output.is_file() or output.stat().st_size == 0:
        errors.append("Missing or empty simulation log")
    else:
        log = output.read_text(errors="replace")
        if re.search(
            r"(^\s*(error|fatal)\b|simulation.*aborted|analysis not run)", log, re.I | re.M
        ):
            errors.append("ngspice log reports failed analysis/measurement")
    if any(not Path(p).is_file() or file_digest(Path(p)) != h for p, h in input_hashes.items()):
        errors.append("Netlist or model changed during simulation")
    return result.model_copy(
        update={
            "error": result.error or ("; ".join(errors) if errors else None),
            "input_digest": digest,
            "tool_version": match[1],
            "artifact_hashes": {str(output.resolve()): file_digest(output)}
            if output.is_file()
            else {},
        }
    )


def measurements(text: str) -> dict[str, float]:
    values = {}
    for name, value in re.findall(r"^\s*([\w]+)\s*=\s*([^\s]+)", text, re.MULTILINE):
        try:
            if name in values:
                raise ValueError(f"Duplicate measurement: {name}")
            parsed = float(value)
        except ValueError:
            if name in values:
                raise
            continue
        values[name] = parsed
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
