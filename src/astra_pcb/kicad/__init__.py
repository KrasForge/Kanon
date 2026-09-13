"""KiCad 10 command hooks. JSON violation interpretation remains pending."""

from pathlib import Path
from typing import Literal

from astra_pcb.verification.process import ProcessResult, run


class KiCadCLI:
    def __init__(self, executable: str = "kicad-cli", timeout: float = 120):
        self.executable = executable
        self.timeout = timeout

    def check(self, kind: Literal["erc", "drc"], design: Path, output: Path) -> ProcessResult:
        if kind not in {"erc", "drc"}:
            raise ValueError("expected erc or drc")
        if output.exists():
            raise FileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        return run(
            [
                self.executable,
                "sch" if kind == "erc" else "pcb",
                kind,
                "--format",
                "json",
                "--severity-all",
                "--exit-code-violations",
                "--output",
                str(output.resolve()),
                str(design.resolve()),
            ],
            timeout=self.timeout,
            artifacts=(output,),
        )

    def export(
        self, kind: Literal["gerbers", "drill", "step", "bom"], design: Path, output: Path
    ) -> ProcessResult:
        if kind not in {"gerbers", "drill", "step", "bom"}:
            raise ValueError("unsupported export")
        if output.exists():
            raise FileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        result = run(
            [
                self.executable,
                "sch" if kind == "bom" else "pcb",
                "export",
                kind,
                "--output",
                str(output.resolve()),
                str(design.resolve()),
            ],
            timeout=self.timeout,
        )
        paths = (
            tuple(str(p) for p in output.rglob("*") if p.is_file())
            if output.is_dir()
            else ((str(output),) if output.is_file() else ())
        )
        return result.model_copy(update={"artifacts": paths})
