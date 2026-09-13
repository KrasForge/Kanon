"""Fresh export receipts, fabrication-file envelopes and content-addressed manifests."""

import re
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.models import CheckResult, CheckStatus, StrictModel
from astra_pcb.models.provenance import Digest, InputIdentity, file_digest
from astra_pcb.verification.process import ProcessResult


class Artifact(StrictModel):
    role: str = Field(min_length=1)
    path: str = Field(min_length=1)
    sha256: Digest
    size_bytes: int = Field(gt=0)

    @model_validator(mode="after")
    def relative(self):
        if Path(self.path).is_absolute() or ".." in Path(self.path).parts:
            raise ValueError("Manifest artifact path must stay inside release directory")
        return self


class Manifest(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    release_id: str = Field(min_length=1)
    inputs: InputIdentity
    artifacts: tuple[Artifact, ...] = Field(min_length=1)
    design_author: str = Field(min_length=1)
    notice: str = "Gate evidence and fabrication package; no manufacturing order has been placed."

    @model_validator(mode="after")
    def complete(self):
        paths = [a.path for a in self.artifacts]
        if len(paths) != len(set(paths)):
            raise ValueError("Duplicate release artifact paths")
        required = {
            "schematic",
            "pcb",
            "gerber",
            "drill",
            "bom",
            "step",
            "review",
            "verification",
            "manufacturing-profile",
            "release-report",
        }
        if required - {a.role for a in self.artifacts}:
            raise ValueError("Incomplete release artifact roles")
        return self

    def verify(self, root: Path) -> None:
        for artifact in self.artifacts:
            path = (root / artifact.path).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                raise ValueError("Missing/escaping release artifact")
            if path.stat().st_size != artifact.size_bytes or file_digest(path) != artifact.sha256:
                raise ValueError("Release artifact changed")


def artifact(root: Path, path: Path, role: str) -> Artifact:
    path = path.resolve()
    return Artifact(
        role=role,
        path=str(path.relative_to(root.resolve())),
        sha256=file_digest(path),
        size_bytes=path.stat().st_size,
    )


def check_export(
    kind: str,
    result: ProcessResult,
    *,
    expected_layers: tuple[str, ...] = (),
    expected_drills: tuple[str, ...] | None = None,
) -> CheckResult:
    error = result.error
    if result.exit_code != 0 or not result.input_digest or not result.artifacts:
        error = error or "Export failed or lacks source/artifact identity"
    observed = set()
    drill_categories = []
    if len(result.artifacts) != len(set(result.artifacts)):
        error = "Duplicate artifact receipt"
    for name in result.artifacts:
        path = Path(name)
        if not path.is_file() or result.artifact_hashes.get(str(path.resolve())) != file_digest(
            path
        ):
            error = "Missing or changed export artifact"
            continue
        if path.stat().st_size == 0:
            error = "Empty export"
            continue
        data = path.read_text(errors="replace")
        if kind == "gerbers":
            if not path.name.endswith(".gbr"):
                continue  # KiCad job file is recorded separately in the receipt.
            if "M02*" not in data[-100:] or "%FS" not in data or "%MO" not in data:
                error = "Invalid Gerber envelope"
            matching_layers = [
                layer
                for layer in expected_layers
                if path.name.endswith("-" + layer.replace(".", "_") + ".gbr")
            ]
            if len(matching_layers) != 1 or matching_layers[0] in observed:
                error = "Unexpected or duplicate Gerber layer"
            for layer in expected_layers:
                if path.name.endswith("-" + layer.replace(".", "_") + ".gbr"):
                    functions = {
                        "F.Cu": r"Copper,L1,Top",
                        "B.Cu": r"Copper,L\d+,Bot",
                        "Edge.Cuts": r"Profile,NP",
                        "F.Mask": r"Soldermask,Top",
                        "B.Mask": r"Soldermask,Bot",
                        "F.Silkscreen": r"Legend,Top",
                        "B.Silkscreen": r"Legend,Bot",
                        "F.Paste": r"Paste,Top",
                        "B.Paste": r"Paste,Bot",
                    }
                    expected = functions.get(layer)
                    if re.fullmatch(r"In\d+\.Cu", layer):
                        expected = rf"Copper,L{int(layer[2:-3]) + 1},Inr"
                    if expected is None or not re.search(
                        r"%TF.FileFunction," + expected + r"(?:,|\*)", data
                    ):
                        error = "Gerber X2 layer identity does not match requested layer: " + layer
                    observed.add(layer)
        elif kind == "drill" and path.suffix.lower() == ".drl":
            if not re.search(r"^M48\s*$", data, re.M) or not re.search(r"^M30\s*$", data, re.M):
                error = "Invalid Excellon envelope"
            observed.add("drill")
            category = (
                "NPTH"
                if path.stem.endswith("-NPTH")
                else "PTH"
                if path.stem.endswith("-PTH")
                else "combined"
            )
            drill_categories.append(category)
            function = re.search(r"; #@! TF.FileFunction,([^\n]+)", data)
            if function and (
                (category == "NPTH" and not function[1].startswith("NonPlated,"))
                or (category == "PTH" and not function[1].startswith("Plated,"))
            ):
                error = "Drill filename and plating identity disagree"
    if kind == "gerbers" and set(expected_layers) - observed:
        error = "Missing requested Gerber layers: " + ", ".join(
            sorted(set(expected_layers) - observed)
        )
    if kind == "drill" and "drill" not in observed:
        error = "No Excellon drill file generated"
    if (
        kind == "drill"
        and expected_drills is not None
        and sorted(drill_categories) != sorted(expected_drills)
    ):
        error = "Drill categories differ from expected inventory: " + str(drill_categories)
    return CheckResult(
        check_id=f"export.{kind}",
        name=f"{kind} export consistency",
        status=CheckStatus.ERROR if error else CheckStatus.PASS,
        message=error or "Fresh source-bound artifact receipts and file envelopes match",
        evidence=(result.model_dump_json(),),
        source="kicad-cli export",
    )
