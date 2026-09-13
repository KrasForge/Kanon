"""Optional bounded solid-geometry collision review over immutable STEP inputs."""

import json
import math
import sys
import tempfile
from pathlib import Path

from astra_pcb.models import CheckResult, CheckStatus
from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import run


def check_collision(
    left: Path,
    right: Path,
    *,
    minimum_clearance_mm: float,
    shared_frame_evidence: str,
    python: str = sys.executable,
) -> CheckResult:
    if (
        not math.isfinite(minimum_clearance_mm)
        or minimum_clearance_mm <= 0
        or not shared_frame_evidence
    ):
        raise ValueError(
            "Positive clearance and explicit shared coordinate-frame evidence required"
        )
    hashes = {str(p.resolve()): file_digest(p) for p in (left, right)}
    available = run([python, "-c", "import OCP"], timeout=15)
    if available.error or available.exit_code:
        return CheckResult(
            check_id="mechanical.collision",
            name="STEP collision review",
            status=CheckStatus.SKIP,
            message="Optional OpenCascade Python runtime unavailable",
        )
    with tempfile.TemporaryDirectory(prefix="astra-collision-") as directory:
        config = Path(directory) / "job.json"
        output = Path(directory) / "result.json"
        config.write_text(
            json.dumps(
                {"files": [str(left.resolve()), str(right.resolve())], "output": str(output)}
            )
        )
        # The checked-in worker path supports a separate optional geometry Python environment.
        worker = Path(__file__).with_name("collision_worker.py")
        result = run([python, str(worker), str(config)], timeout=120)
        if result.error or result.exit_code or not output.is_file():
            return CheckResult(
                check_id="mechanical.collision",
                name="STEP collision review",
                status=CheckStatus.ERROR,
                message="STEP geometry analysis failed",
                evidence=(result.model_dump_json(),),
            )
        data = json.loads(output.read_text())
    if not all(math.isfinite(v) and v >= -1e-9 for v in data.values()):
        raise ValueError("Invalid geometry measurement")
    if any(
        not Path(path).is_file() or file_digest(Path(path)) != digest
        for path, digest in hashes.items()
    ):
        raise ValueError("STEP source changed during analysis")
    failed = data["overlap_mm3"] > 1e-9 or data["clearance_mm"] < minimum_clearance_mm
    return CheckResult(
        check_id="mechanical.collision",
        name="STEP collision review",
        status=CheckStatus.FAIL if failed else CheckStatus.PASS,
        message=f"Overlap {data['overlap_mm3']:.6g} mm3; clearance {data['clearance_mm']:.6g} mm",
        evidence=(json.dumps(hashes), shared_frame_evidence, result.model_dump_json()),
        source="OpenCascade solid intersection/distance; depends on geometry/frame",
    )
