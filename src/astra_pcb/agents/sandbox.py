"""Fail-closed Linux reviewer executor: empty root, immutable inputs, no credentials/network."""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import ProcessResult


def isolated_call(
    worker: Path, packet: dict, *, evidence: Path | None = None, timeout: float = 30
) -> ProcessResult:
    if sys.platform != "linux" or not shutil.which("bwrap"):
        return ProcessResult(
            command=("bwrap",),
            exit_code=None,
            error="Required Linux bubblewrap isolation unavailable; no fallback",
        )
    if timeout <= 0 or timeout > 60:
        raise ValueError("Reviewer deadline must be in (0,60] seconds")
    payload = json.dumps(packet, allow_nan=False)
    if len(payload.encode()) > 4 * 1024 * 1024:
        raise ValueError("Review packet exceeds 4 MiB")
    interpreter = Path(sys.executable).resolve()
    runtime = Path(sys.base_prefix)
    command = [
        "bwrap",
        "--unshare-all",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        "--setenv",
        "LD_LIBRARY_PATH",
        "/runtime/lib",
        "--cap-drop",
        "ALL",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--ro-bind",
        str(runtime / "lib"),
        "/runtime/lib",
        "--ro-bind",
        str(interpreter),
        "/runtime/bin/python",
    ]
    # Only libraries, not host /usr/bin, home, SSH agents, sockets or credentials are exposed.
    for path in ("/lib", "/lib64"):
        if Path(path).exists():
            command += ["--ro-bind", str(Path(path).resolve()), path]
    with tempfile.TemporaryDirectory(prefix="kanon-review-") as directory:
        staging = Path(directory)
        script = staging / "worker.py"
        script.write_bytes(worker.read_bytes())
        bootstrap = Path(__file__).with_name("sandbox_bootstrap.py")
        command += [
            "--ro-bind",
            str(script),
            "/worker.py",
            "--ro-bind",
            str(bootstrap),
            "/bootstrap.py",
        ]
        if evidence is not None:
            if not evidence.is_dir():
                raise ValueError("Frozen evidence directory required")
            command += ["--ro-bind", str(evidence.resolve()), "/evidence"]
        command += ["--chdir", "/tmp", "/runtime/bin/python", "-I", "-S", "-B", "/bootstrap.py"]
        # Files bound the captured output; no unbounded PIPE buffering.
        with (staging / "stdout").open("w+") as stdout, (staging / "stderr").open("w+") as stderr:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
                text=True,
                start_new_session=True,
            )
            error = None
            try:
                process.communicate(payload, timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                error = "Reviewer deadline exceeded"
            stdout.seek(0)
            stderr.seek(0)
            out, err = stdout.read(8 * 1024 * 1024 + 1), stderr.read(1024 * 1024 + 1)
            if len(out) > 8 * 1024 * 1024 or len(err) > 1024 * 1024:
                error = "Reviewer output limit exceeded"
            return ProcessResult(
                command=tuple(command),
                exit_code=process.returncode,
                stdout=out,
                stderr=err,
                error=error or ("Isolated reviewer failed" if process.returncode else None),
                artifact_hashes={
                    "worker": file_digest(script),
                    "bootstrap": file_digest(bootstrap),
                },
            )
