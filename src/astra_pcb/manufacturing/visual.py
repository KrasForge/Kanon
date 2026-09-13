"""Render actual fabrication layers through gerbv; source PCB SVGs are not Gerber review."""

import re
from pathlib import Path

from astra_pcb.models import CheckResult, CheckStatus
from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import run


def render_gerbers(files: tuple[Path, ...], output: Path, executable: str = "gerbv") -> CheckResult:
    if not files or output.exists() or output.is_symlink():
        raise ValueError("Nonempty layer list and fresh SVG output required")
    hashes = {str(p.resolve()): file_digest(p) for p in files}
    version = run([executable, "--version"], timeout=10)
    if version.error or version.exit_code != 0:
        return CheckResult(
            check_id="visual.gerber",
            name="Gerber visual artifact",
            status=CheckStatus.SKIP,
            message="gerbv unavailable; no fabrication-layer render produced",
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    result = run(
        [
            executable,
            "--export=svg",
            "--output=" + str(output.resolve()),
            *(str(p.resolve()) for p in files),
        ],
        timeout=60,
        artifacts=(output,),
    )
    error = result.error or ("gerbv failed" if result.exit_code else None)
    if not output.is_file() or "<svg" not in output.read_text(errors="replace")[:2000]:
        error = "Missing/invalid Gerber SVG"
    if any(not Path(p).is_file() or file_digest(Path(p)) != h for p, h in hashes.items()):
        error = "Fabrication source changed while rendering"
    if re.search(r"critical|error", result.stderr, re.I):
        error = error or "Renderer reported parse errors; SVG may be incomplete"
    warning = re.search(r"warning", result.stderr, re.I)
    return CheckResult(
        check_id="visual.gerber",
        name="Gerber visual artifact",
        status=CheckStatus.ERROR if error else CheckStatus.WARN if warning else CheckStatus.PASS,
        message=error
        or (
            "Renderer diagnostics require review"
            if warning
            else "Actual fabrication layers rendered; human/independent inspection still required"
        ),
        evidence=(
            result.model_dump_json(),
            str(hashes),
            version.stdout,
            file_digest(output) if output.is_file() else "",
        ),
        source="gerbv",
    )


def render_layers(layers: dict[str, Path], output: Path, *, side_re: str = ".*") -> CheckResult:
    """Render explicit Gerbonara layer roles; never guess layers from ambiguous filenames."""
    import importlib.util
    import json
    import sys
    import tempfile

    if output.exists() or output.is_symlink() or not layers:
        raise ValueError("Explicit layers and fresh output required")
    allowed = {
        "top copper",
        "bottom copper",
        "top mask",
        "bottom mask",
        "top silk",
        "bottom silk",
        "top paste",
        "bottom paste",
        "mechanical outline",
    }
    if not set(layers) <= allowed or side_re not in {".*", "top|mechanical", "bottom|mechanical"}:
        raise ValueError("Unsupported render layer or view selection")
    if importlib.util.find_spec("gerbonara") is None:
        return CheckResult(
            check_id="visual.layers",
            name="Gerber layer render",
            status=CheckStatus.SKIP,
            message="Optional visual extra is not installed",
        )
    hashes = {str(p.resolve()): file_digest(p) for p in layers.values()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="astra-gerber-") as directory:
        config = Path(directory) / "render.json"
        config.write_text(
            json.dumps(
                {
                    "layers": {k: str(p.resolve()) for k, p in layers.items()},
                    "output": str(output.resolve()),
                    "side_re": side_re,
                }
            )
        )
        result = run(
            [sys.executable, "-m", "astra_pcb.manufacturing.render_worker", str(config)],
            timeout=60,
            artifacts=(output.resolve(),),
        )
    error = result.error or ("Render worker failed" if result.exit_code else None)
    diagnostics = {}
    if not error:
        try:
            diagnostics = json.loads(result.stdout)
        except ValueError:
            error = "Malformed renderer diagnostics"
    if not output.is_file() or "<svg" not in output.read_text(errors="replace")[:2000]:
        error = "Missing/invalid SVG render"
    if any(
        not Path(path).is_file() or file_digest(Path(path)) != digest
        for path, digest in hashes.items()
    ):
        error = "Gerber source changed during render"
    return CheckResult(
        check_id="visual.layers",
        name="Gerber layer render",
        status=CheckStatus.ERROR
        if error
        else CheckStatus.WARN
        if diagnostics.get("warnings")
        else CheckStatus.PASS,
        message=error
        or "Actual Gerber geometry rendered; independent visual review remains required",
        evidence=(result.model_dump_json(), str(hashes), json.dumps(diagnostics)),
        source="Gerbonara 1.6.3",
    )
