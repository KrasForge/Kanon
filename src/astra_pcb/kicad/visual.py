"""Consistent top/bottom/isometric PNG artifacts; vision remains supplementary."""

from pathlib import Path

from astra_pcb.kicad import KiCadCLI
from astra_pcb.models import CheckResult, CheckStatus, VerificationReport
from astra_pcb.models.provenance import file_digest


def render_board(board: Path, output: Path, adapter: KiCadCLI | None = None) -> VerificationReport:
    output.mkdir(parents=True, exist_ok=False)
    adapter = adapter or KiCadCLI(timeout=120)
    checks = []
    source_hash = file_digest(board)
    for view in ("top", "bottom", "isometric"):
        target = output / f"{view}.png"
        result = adapter.render(board, target, view=view)
        valid = (
            not result.error
            and result.exit_code == 0
            and target.is_file()
            and target.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            and result.artifact_hashes.get(str(target.resolve())) == file_digest(target)
            and file_digest(board) == source_hash
        )
        checks.append(
            CheckResult(
                check_id=f"visual.pcb.{view}",
                name=f"PCB {view} rendering",
                status=CheckStatus.PASS if valid else CheckStatus.ERROR,
                message="Native PCB render generated; not engineering approval"
                if valid
                else result.error or "Missing/invalid/changed render artifact",
                evidence=(result.model_dump_json(),),
                source="kicad-cli 3D renderer",
            )
        )
    report = VerificationReport(results=tuple(checks))
    (output / "renders.json").write_text(report.model_dump_json(indent=2))
    return report
