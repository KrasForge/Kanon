"""Run fresh, independent project ERC/DRC and persist an aggregate report."""

from pathlib import Path

from astra_pcb.kicad import KiCadCLI
from astra_pcb.kicad.reports import interpret
from astra_pcb.models import VerificationReport


def verify_design(
    *, schematic: Path | None = None, board: Path | None = None, output: Path, parity: bool = False
) -> VerificationReport:
    if schematic is None and board is None:
        raise ValueError("A schematic or PCB is required")
    output.mkdir(parents=True, exist_ok=False)
    adapter = KiCadCLI()
    results = []
    versions = {}
    for kind, design in [("erc", schematic), ("drc", board)]:
        if design is None:
            continue
        report_path = output / f"{kind}.json"
        execution = adapter.check(kind, design, report_path, parity=parity and kind == "drc")
        (output / f"{kind}-execution.json").write_text(execution.model_dump_json(indent=2))
        report = interpret(kind, execution, report_path, design)
        results.extend(report.results)
        versions.update(report.tool_versions)
    result = VerificationReport(results=tuple(results), tool_versions=versions)
    (output / "verification.json").write_text(result.model_dump_json(indent=2))
    return result
