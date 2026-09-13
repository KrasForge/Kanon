"""Strict interpretation of KiCad 10 ERC/DRC JSON, including omitted/excluded checks."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from astra_pcb.models import CheckResult, CheckSeverity, CheckStatus, VerificationReport
from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import ProcessResult


class Item(BaseModel):
    model_config = ConfigDict(extra="allow")
    uuid: str
    description: str
    pos: dict[str, float]


class Violation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
    description: str
    severity: Literal["error", "warning"]
    items: list[Item]
    excluded: bool = False
    comment: str | None = None


class Sheet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    uuid_path: str
    violations: list[Violation]


class ReportData(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_url: str = Field(alias="$schema")
    source: str
    date: str
    kicad_version: str = Field(pattern=r"^10\.")
    coordinate_units: Literal["mm", "mils", "in"]
    included_severities: list[Literal["error", "warning", "exclusion"]]
    ignored_checks: list[dict[str, str]]
    sheets: list[Sheet] | None = None
    violations: list[Violation] | None = None
    unconnected_items: list[Violation] | None = None
    schematic_parity: list[Violation] | None = None


def interpret(
    kind: Literal["erc", "drc"],
    process: ProcessResult,
    output: Path,
    source: Path,
    *,
    allowed_ignored: frozenset[str] = frozenset(),
) -> VerificationReport:
    check_id = "schematic.erc" if kind == "erc" else "pcb.drc"
    try:
        if process.error or process.exit_code not in {0, 5}:
            raise ValueError(process.error or f"KiCad exited {process.exit_code}: {process.stderr}")
        if str(output.resolve()) not in {str(Path(p).resolve()) for p in process.artifacts}:
            raise ValueError("Current invocation did not generate the report")
        if process.artifact_hashes.get(str(output.resolve())) != file_digest(output):
            raise ValueError("Report changed after execution or lacks artifact identity")
        data = ReportData.model_validate_json(output.read_text())
        if data.schema_url != f"https://schemas.kicad.org/{kind}.v1.json":
            raise ValueError("Unexpected report schema")
        if Path(data.source).name != source.name:
            raise ValueError("Report source does not match requested design")
        if set(data.included_severities) != {"error", "warning", "exclusion"}:
            raise ValueError("Report omits severity classes")
        if kind == "erc":
            if data.sheets is None or not data.sheets:
                raise ValueError("ERC report lacks sheets")
            violations = [v for sheet in data.sheets for v in sheet.violations]
        else:
            if any(
                x is None for x in (data.violations, data.unconnected_items, data.schematic_parity)
            ):
                raise ValueError("DRC report lacks required violation categories")
            violations = [*data.violations, *data.unconnected_items, *data.schematic_parity]
        ignored = {x["key"] for x in data.ignored_checks}
        details = []
        for i, violation in enumerate(violations):
            status = (
                CheckStatus.WARN
                if violation.excluded or violation.severity == "warning"
                else (CheckStatus.FAIL)
            )
            details.append(
                CheckResult(
                    check_id=f"{check_id}.{i}",
                    name=violation.type,
                    status=status,
                    severity=CheckSeverity.WARNING
                    if status == CheckStatus.WARN
                    else (CheckSeverity.ERROR),
                    message=violation.description
                    + (f" [excluded: {violation.comment}]" if violation.excluded else ""),
                    evidence=(str(output), json.dumps(violation.model_dump())),
                    affected_objects=tuple(item.uuid for item in violation.items),
                    source="kicad-cli",
                )
            )
        unknown_ignored = ignored - allowed_ignored
        if unknown_ignored:
            details.append(
                CheckResult(
                    check_id=f"{check_id}.ignored",
                    name="Ignored checks",
                    status=CheckStatus.WARN,
                    message=", ".join(sorted(unknown_ignored)),
                    evidence=(str(output),),
                    source="kicad-cli",
                )
            )
        if process.exit_code == 5 and not violations:
            raise ValueError("Violation exit code contradicts an empty report")
        status = (
            CheckStatus.FAIL
            if any(r.status == CheckStatus.FAIL for r in details)
            else (CheckStatus.WARN if details else CheckStatus.PASS)
        )
        summary = CheckResult(
            check_id=check_id,
            name=f"KiCad {kind.upper()}",
            status=status,
            message=(
                f"{len(violations)} violations; {len(unknown_ignored)} unaccepted ignored checks"
            ),
            evidence=(str(output),),
            source="kicad-cli",
        )
        return VerificationReport(
            results=(summary, *details),
            input_digest=process.input_digest,
            tool_versions={"kicad-cli": data.kicad_version},
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return VerificationReport(
            results=(
                CheckResult(
                    check_id=check_id,
                    name=check_id,
                    status=CheckStatus.ERROR,
                    message=str(exc),
                    evidence=(str(output),),
                    source="kicad-cli",
                ),
            )
        )
