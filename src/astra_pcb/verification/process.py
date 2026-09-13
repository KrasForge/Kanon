"""Bounded, shell-free process execution with explicit failure capture."""

import shutil
import subprocess
from pathlib import Path

from astra_pcb.models import StrictModel


class ProcessResult(StrictModel):
    command: tuple[str, ...]
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    artifacts: tuple[str, ...] = ()


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 60,
    artifacts: tuple[Path, ...] = (),
) -> ProcessResult:
    if not command or timeout <= 0:
        raise ValueError("command and positive timeout required")
    if not shutil.which(command[0]):
        return ProcessResult(
            command=tuple(command), exit_code=None, error=f"Executable not found: {command[0]}"
        )
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
    except subprocess.TimeoutExpired as exc:

        def decode(value: bytes | str | None) -> str:
            return value.decode(errors="replace") if isinstance(value, bytes) else value or ""

        return ProcessResult(
            command=tuple(command),
            exit_code=None,
            error=str(exc),
            stdout=decode(exc.stdout),
            stderr=decode(exc.stderr),
        )
    except OSError as exc:
        return ProcessResult(command=tuple(command), exit_code=None, error=str(exc))
    artifact_paths = tuple(p if p.is_absolute() else (cwd or Path.cwd()) / p for p in artifacts)
    return ProcessResult(
        command=tuple(command),
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        artifacts=tuple(str(p.resolve()) for p in artifact_paths if p.is_file()),
    )
