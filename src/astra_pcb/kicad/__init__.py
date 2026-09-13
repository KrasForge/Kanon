"""Version-qualified KiCad CLI execution with source identity and fresh artifact capture."""

from pathlib import Path
from typing import Literal

from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import ProcessResult, run


class KiCadCLI:
    def __init__(self, executable: str = "kicad-cli", timeout: float = 120):
        self.executable = executable
        self.timeout = timeout

    def _execute(self, args: list[str], design: Path, output: Path) -> ProcessResult:
        command = [self.executable, *args, "--output", str(output.resolve()), str(design.resolve())]
        if output.exists() or output.is_symlink():
            raise FileExistsError(output)
        if not design.is_file():
            return ProcessResult(
                command=tuple(command), exit_code=None, error=f"Design file missing: {design}"
            )
        version = run([self.executable, "version"], timeout=10)
        if version.exit_code != 0 or not version.stdout.strip().startswith("10."):
            return ProcessResult(
                command=tuple(command),
                exit_code=None,
                error="KiCad 10 is required",
                stderr=version.stderr,
            )
        before = file_digest(design)
        output.parent.mkdir(parents=True, exist_ok=True)
        result = run(command, timeout=self.timeout)
        paths = (
            sorted(p for p in output.rglob("*") if p.is_file())
            if output.is_dir()
            else ([output] if output.is_file() else [])
        )
        if not design.is_file() or file_digest(design) != before:
            result = result.model_copy(
                update={"error": "Design changed during verification/export"}
            )
        if result.exit_code == 0 and (not paths or any(p.stat().st_size == 0 for p in paths)):
            result = result.model_copy(update={"error": "Missing or empty output artifacts"})
        return result.model_copy(
            update={
                "tool_version": version.stdout.strip(),
                "input_digest": before,
                "artifacts": tuple(str(p.resolve()) for p in paths),
                "artifact_hashes": {str(p.resolve()): file_digest(p) for p in paths},
            }
        )

    def check(
        self, kind: Literal["erc", "drc"], design: Path, output: Path, *, parity: bool = False
    ) -> ProcessResult:
        if kind not in {"erc", "drc"}:
            raise ValueError("expected erc or drc")
        args = [
            "sch" if kind == "erc" else "pcb",
            kind,
            "--format",
            "json",
            "--severity-all",
            "--exit-code-violations",
        ]
        if parity:
            if kind != "drc":
                raise ValueError("Parity is a PCB DRC option")
            args.append("--schematic-parity")
        # No refill/save flags: verifier must not mutate sources. Designer must persist zone fill.
        return self._execute(args, design, output)

    def export(
        self,
        kind: Literal["gerbers", "drill", "step", "bom", "netlist"],
        design: Path,
        output: Path,
        *,
        layers: tuple[str, ...] = (),
    ) -> ProcessResult:
        if kind not in {"gerbers", "drill", "step", "bom", "netlist"}:
            raise ValueError("unsupported export")
        args = ["sch" if kind in {"bom", "netlist"} else "pcb", "export", kind]
        if layers:
            if kind != "gerbers" or any("," in layer for layer in layers):
                raise ValueError("Explicit layers apply only to Gerbers")
            args += ["--layers", ",".join(layers)]
        if kind == "gerbers":
            args.append("--no-protel-ext")
        return self._execute(args, design, output)
