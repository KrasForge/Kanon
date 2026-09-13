import os
import shutil
from pathlib import Path

import pytest

from astra_pcb.agents.history import ReviewHistory
from astra_pcb.agents.review import ReviewPacket, isolated_review, remediate
from astra_pcb.kicad.snapshot import capture
from astra_pcb.layout import Floorplan, MechanicalAnchor, Placement, Point, Region
from astra_pcb.models import VerificationReport
from astra_pcb.models.engineering import Finding, Review


def review_fixture(tmp_path):
    (tmp_path / "source.txt").write_text("Known synthetic fault")
    snapshot = capture(tmp_path, (Path("source.txt"),), "rev")
    finding = Finding(
        id="F1",
        title="Synthetic fault",
        severity="blocker",
        evidence=("source",),
        explanation="Declared fault",
        suggested_remediation="Correct source",
    )
    review = Review(
        reviewer="independent",
        design_revision="rev",
        snapshot_sha256=snapshot.identity.digest,
        scope=("test",),
        findings=(finding,),
        limitations=(),
    )
    return snapshot, review


def test_persistent_iteration_stop_and_tamper(tmp_path):
    _, review = review_fixture(tmp_path)
    path = tmp_path / "private/history.jsonl"
    history = ReviewHistory(path, "designer")
    assert history.append(review).status == "WARN"
    assert history.append(review).status == "WARN"
    assert ReviewHistory(path, "designer").append(review).status == "FAIL"
    assert len(path.read_text().splitlines()) == 3
    path.write_text(path.read_text().replace("Synthetic fault", "Modified fault", 1))
    with pytest.raises(ValueError, match="tampered"):
        history.append(review)


def test_remediation_stops_before_third_mutation(tmp_path):
    _, review = review_fixture(tmp_path)
    attempts = []
    for i in range(2):
        remediate(
            review,
            ("F1",),
            root=tmp_path,
            sources=(Path("source.txt"),),
            revision="rev",
            designer="designer",
            apply=lambda _: attempts.append(True),
            output=tmp_path / f"attempt-{i}",
        )
    with pytest.raises(RuntimeError, match="Stop automatic"):
        remediate(
            review,
            ("F1",),
            root=tmp_path,
            sources=(Path("source.txt"),),
            revision="rev",
            designer="designer",
            apply=lambda _: attempts.append(True),
            output=tmp_path / "attempt-3",
        )
    assert len(attempts) == 2


def test_soft_floorplan_and_hard_mechanical_anchor():
    region = Region(
        id="analog",
        function="analog-input",
        strength="soft",
        minimum=Point(x_mm=0, y_mm=0),
        maximum=Point(x_mm=10, y_mm=10),
    )
    placement = Placement(
        reference="J1", point=Point(x_mm=12, y_mm=5), region="analog", rotation_degrees=180
    )
    anchor = MechanicalAnchor(
        reference="J1",
        point=Point(x_mm=12, y_mm=5),
        tolerance_mm=0.1,
        rotation_degrees=180,
        rotation_tolerance_degrees=1,
        evidence=("Mechanical drawing",),
    )
    plan = Floorplan(
        input_digest="a" * 64, regions=(region,), placements=(placement,), anchors=(anchor,)
    )
    assert plan.audit().exit_code == 2
    assert (
        plan.model_copy(update={"anchors": (anchor.model_copy(update={"rotation_degrees": 0}),)})
        .audit()
        .exit_code
        == 1
    )


@pytest.mark.integration
def test_isolated_review_returns_findings_not_approval(tmp_path):
    if not shutil.which("bwrap"):
        if os.getenv("KANON_REQUIRE_REVIEWER_ISOLATION") == "1":
            pytest.fail("Mandatory OS isolation unavailable")
        pytest.skip("Required isolation runtime unavailable")
    snapshot, expected = review_fixture(tmp_path)
    packet = ReviewPacket(
        snapshot=snapshot,
        verification=VerificationReport(results=(), input_digest=snapshot.identity.digest),
        design_author="designer",
        requested_scope=("test",),
    )
    worker = tmp_path / "review.py"
    # Deployment-owned deterministic test adapter; never represents a live model qualification.
    worker.write_text(
        "import json,sys\np=json.load(sys.stdin)\nprint(json.dumps("
        + repr(expected.model_dump(mode="json"))
        + "))\n"
    )
    try:
        review, check = isolated_review(packet, "independent", worker)
    except RuntimeError:
        if os.getenv("KANON_REQUIRE_REVIEWER_ISOLATION") == "1":
            raise
        # Platform absence is checked by the dedicated mandatory OS integration job.
        from astra_pcb.agents.sandbox import isolated_call

        probe = isolated_call(worker, {})
        if "No permissions to create a new namespace" in probe.stderr:
            pytest.skip("Nested container namespaces unavailable; dedicated OS job covers review")
        raise
    assert check.status == "FAIL" and review.findings[0].id == "F1"
