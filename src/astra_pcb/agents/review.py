"""Independent frozen-state review and finding-preserving remediation orchestration."""

from collections.abc import Callable
from pathlib import Path

from pydantic import Field

from astra_pcb.kicad.snapshot import Snapshot
from astra_pcb.kicad.workflow import MutationResult, mutate_verify
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.models.engineering import Finding, Review


class ReviewPacket(StrictModel):
    snapshot: Snapshot
    verification: VerificationReport
    design_author: str = Field(min_length=1)
    requested_scope: tuple[str, ...] = Field(min_length=1)
    # Immutable bytes/strings, not paths or executable tools. Include BOM, evidence, renders
    # and decisions in the snapshot identity or as hashed references inside its documents.
    instructions: str = (
        "Seek counterexamples and electrical/layout failures. Passing ERC/DRC "
        "does not establish correctness. Report missing evidence as limitations."
    )


def independent_review(
    packet: ReviewPacket, reviewer: str, invoke: Callable[[dict], dict]
) -> tuple[Review, CheckResult]:
    if reviewer == packet.design_author or not reviewer.strip():
        raise ValueError("Designer cannot be the independent reviewer")
    if packet.verification.input_digest != packet.snapshot.identity.digest:
        raise ValueError("Verification does not describe the frozen review state")
    # Serialization prevents in-place changes to the caller's snapshot/report dictionaries.
    review = Review.model_validate(invoke(packet.model_dump(mode="json")))
    if (
        review.reviewer != reviewer
        or review.snapshot_sha256 != packet.snapshot.identity.digest
        or review.design_revision != packet.snapshot.identity.revision
    ):
        raise ValueError("Reviewer identity or frozen revision mismatch")
    if not set(packet.requested_scope) <= set(review.scope):
        raise ValueError("Reviewer omitted requested scope")
    check = CheckResult(
        check_id="review.independent",
        name="Independent engineering review",
        status=CheckStatus.FAIL if review.has_blockers else CheckStatus.WARN,
        message="Unresolved findings/limitations"
        if review.has_blockers
        else "Findings recorded; separate signed independent approval is still required",
        evidence=(review.model_dump_json(),),
        source=reviewer,
    )
    return review, check


class RemediationResult(StrictModel):
    mutation: MutationResult
    findings: tuple[Finding, ...]
    review_required: bool = True


def remediate(
    review: Review,
    selected: tuple[str, ...],
    *,
    root: Path,
    sources: tuple[Path, ...],
    revision: str,
    designer: str,
    apply: Callable[[tuple[Finding, ...]], None],
    output: Path,
) -> RemediationResult:
    from astra_pcb.kicad.snapshot import capture

    if designer == review.reviewer:
        raise ValueError("Reviewer cannot perform remediation")
    current = capture(root, sources, revision)
    if current.identity.digest != review.snapshot_sha256:
        raise ValueError("Review is stale; reconcile findings against current snapshot first")
    by_id = {finding.id: finding for finding in review.findings}
    if not selected or len(set(selected)) != len(selected) or set(selected) - by_id.keys():
        raise ValueError("Select distinct existing finding IDs")
    if any(by_id[key].status not in {"open", "in_progress"} for key in selected):
        raise ValueError("Only open/in-progress findings may be remediated")
    result = mutate_verify(
        root, sources, revision, lambda: apply(tuple(by_id[k] for k in selected)), output
    )
    findings = tuple(
        f.transition("in_progress") if f.id in selected and f.status == "open" else f
        for f in review.findings
    )
    # A successful edit or verification does not resolve a reviewer finding automatically.
    return RemediationResult(mutation=result, findings=findings)


def reconcile(previous: Review, current: Review, design_author: str) -> Review:
    if current.reviewer == design_author:
        raise ValueError("Resolution review must be independent")
    old = {finding.id: finding for finding in previous.findings}
    new = {finding.id: finding for finding in current.findings}
    if old.keys() - new.keys():
        raise ValueError("Findings cannot disappear; resolve with evidence and preserve IDs")
    for key, before in old.items():
        after = new[key]
        if before.title != after.title or before.severity != after.severity:
            raise ValueError(
                "Finding identity/severity changed; retain original and add a new finding"
            )
        if before.status != after.status:
            before.transition(after.status, after.resolution_evidence)
    return current
