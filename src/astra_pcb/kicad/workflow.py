"""Persisted mutation/readback/verification workflow with immutable before/after identities."""

from collections.abc import Callable
from pathlib import Path

from astra_pcb.kicad import KiCadCLI
from astra_pcb.kicad.reports import interpret
from astra_pcb.kicad.snapshot import Snapshot, capture
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class MutationResult(StrictModel):
    before: Snapshot
    after: Snapshot | None
    verification: VerificationReport
    prior_evidence_invalidated: bool


def mutate_verify(
    root: Path,
    sources: tuple[Path, ...],
    revision: str,
    mutation: Callable[[], None],
    output: Path,
    adapter: KiCadCLI | None = None,
) -> MutationResult:
    output.mkdir(parents=True, exist_ok=False)
    before = capture(root, sources, revision)
    failure = None
    try:
        mutation()  # Contract: remote edit AND explicit persistence/readback must finish here.
    except Exception as exc:
        failure = CheckResult(
            check_id="mutation.persistence",
            name="Mutation persistence",
            status=CheckStatus.ERROR,
            message=str(exc),
        )
    try:
        after = capture(root, sources, revision)
    except (OSError, ValueError) as exc:
        checks = ([failure] if failure else []) + [
            CheckResult(
                check_id="mutation.readback",
                name="Mutation readback",
                status=CheckStatus.ERROR,
                message=f"Persisted state cannot be read: {type(exc).__name__}: {exc}",
                remediation=(
                    "Restore or repair source before continuing; prior approvals invalidated"
                ),
            )
        ]
        report = VerificationReport(results=tuple(checks))
        (output / "verification.json").write_text(report.model_dump_json(indent=2))
        (output / "before-snapshot.json").write_text(before.model_dump_json(indent=2))
        return MutationResult(
            before=before, after=None, verification=report, prior_evidence_invalidated=True
        )
    checks = [failure] if failure else []
    adapter = adapter or KiCadCLI()
    # An exception can occur after a partial edit: still run independent checks.
    for index, path in enumerate(sources):
        kind = {".kicad_pcb": "drc", ".kicad_sch": "erc"}.get(path.suffix)
        if not kind:
            continue
        report_path = output / f"{index}-{kind}.json"
        process = adapter.check(kind, root / path, report_path)
        parsed = interpret(kind, process, report_path, root / path)
        # Multiple sheets/boards retain unique IDs; project aggregation is explicit.
        checks.extend(
            r.model_copy(update={"check_id": f"{index}.{r.check_id}"}) for r in parsed.results
        )
    try:
        after.identity.verify(root)
    except ValueError as exc:
        checks.append(
            CheckResult(
                check_id="mutation.identity",
                name="Readback identity",
                status=CheckStatus.ERROR,
                message=str(exc),
            )
        )
    if not checks:
        checks.append(
            CheckResult(
                check_id="mutation.checks",
                name="Applicable checks",
                status=CheckStatus.SKIP,
                message="No schematic or PCB supplied",
            )
        )
    report = VerificationReport(results=tuple(checks), input_digest=after.identity.digest)
    (output / "verification.json").write_text(report.model_dump_json(indent=2))
    (output / "snapshot.json").write_text(after.model_dump_json(indent=2))
    return MutationResult(
        before=before,
        after=after,
        verification=report,
        prior_evidence_invalidated=before.identity.digest != after.identity.digest,
    )
