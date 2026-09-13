"""Version-qualified KiCad CLI execution with source identity and fresh artifact capture."""

import shutil
import tempfile
from pathlib import Path
from typing import Literal

from astra_pcb.models.provenance import canonical_digest, file_digest
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
        original_root = design.resolve().parent
        suffixes = {
            ".kicad_pcb",
            ".kicad_sch",
            ".kicad_pro",
            ".kicad_dru",
            ".kicad_sym",
            ".kicad_mod",
            ".step",
            ".stp",
            ".wrl",
            ".igs",
            ".iges",
        }
        sources = [
            p
            for p in original_root.rglob("*")
            if p.is_file()
            and (p.suffix in suffixes or p.name in {"fp-lib-table", "sym-lib-table"})
            and not any(
                part in {".git", ".venv", "artifacts"}
                for part in p.relative_to(original_root).parts
            )
        ]
        if len(sources) > 10000 or sum(p.stat().st_size for p in sources) > 512 * 1024 * 1024:
            return ProcessResult(
                command=tuple(command),
                exit_code=None,
                error="Project copy exceeds qualification size limits",
            )
        before = {str(p.relative_to(original_root)): file_digest(p) for p in sources}
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="astra-kicad-") as temporary:
            copied_root = Path(temporary)
            for source in sources:
                copied = copied_root / source.relative_to(original_root)
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, copied)
                if file_digest(copied) != before[str(source.relative_to(original_root))]:
                    return ProcessResult(
                        command=tuple(command),
                        exit_code=None,
                        error="Source changed while copying project",
                    )
            command[-1] = str(copied_root / design.name)
            result = run(command, timeout=self.timeout)
        paths = (
            sorted(p for p in output.rglob("*") if p.is_file())
            if output.is_dir()
            else ([output] if output.is_file() else [])
        )
        if any(
            not (original_root / name).is_file() or file_digest(original_root / name) != digest
            for name, digest in before.items()
        ):
            result = result.model_copy(
                update={"error": "Design changed during verification/export"}
            )
        if result.exit_code == 0 and (not paths or any(p.stat().st_size == 0 for p in paths)):
            result = result.model_copy(update={"error": "Missing or empty output artifacts"})
        return result.model_copy(
            update={
                "tool_version": version.stdout.strip(),
                "input_digest": canonical_digest(before),
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
        kind: Literal["gerbers", "drill", "step", "bom", "netlist", "pos"],
        design: Path,
        output: Path,
        *,
        layers: tuple[str, ...] = (),
    ) -> ProcessResult:
        if kind not in {"gerbers", "drill", "step", "bom", "netlist", "pos"}:
            raise ValueError("unsupported export")
        args = ["sch" if kind in {"bom", "netlist"} else "pcb", "export", kind]
        if layers:
            if kind != "gerbers" or any("," in layer for layer in layers):
                raise ValueError("Explicit layers apply only to Gerbers")
            args += ["--layers", ",".join(layers)]
        if kind == "step":
            args += ["--user-origin", "0x0mm"]
        if kind == "pos":
            args += ["--format", "csv", "--units", "mm", "--exclude-dnp"]
        if kind == "gerbers":
            args.append("--no-protel-ext")
        return self._execute(args, design, output)

    def render(self, design: Path, output: Path, *, view: str = "top") -> ProcessResult:
        if view not in {"top", "bottom", "isometric"}:
            raise ValueError("Unknown PCB render view")
        args = [
            "pcb",
            "render",
            "--width",
            "800",
            "--height",
            "600",
            "--quality",
            "basic",
            "--side",
            "bottom" if view == "bottom" else "top",
        ]
        if view == "isometric":
            args.extend(["--rotate", "315,0,45", "--perspective"])
        return self._execute(args, design, output)
