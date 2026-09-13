import base64
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from astra_pcb.agents.critical_nets import Net, NetReview, check_critical_nets
from astra_pcb.agents.lifecycle import Lifecycle, Stage
from astra_pcb.agents.review import ReviewPacket, independent_review, reconcile
from astra_pcb.agents.roles import Role, Roles, RoleTools
from astra_pcb.config import load_yaml
from astra_pcb.kicad.snapshot import capture
from astra_pcb.layout import DistanceRule, Floorplan, check_distances, placements_from_snapshot
from astra_pcb.models import VerificationReport
from astra_pcb.models.engineering import Finding
from astra_pcb.release.attestations import Attestation, TrustedSigner


def test_reviewer_policy_excludes_live_mutation_and_shell(tmp_path):
    roles = Roles.model_validate(load_yaml(Path("config/agents.yaml")))
    reviewer = next(r for r in roles.roles if r.name == "reviewer")
    with pytest.raises(ValueError):
        Role.model_validate({**reviewer.model_dump(), "tools": ["board.save"]})
    with pytest.raises(ValueError):
        Role.model_validate({**reviewer.model_dump(), "shell": True})
    path = tmp_path / "note.txt"
    path.write_text("Frozen")
    snapshot = capture(tmp_path, (Path("note.txt"),), "revision")
    tools = RoleTools(reviewer, snapshot)
    result = tools.call("snapshot.read", {})
    result["documents"]["note.txt"] = "Mutated copy"
    assert tools.call("snapshot.read", {})["documents"]["note.txt"] == "Frozen"
    with pytest.raises(PermissionError):
        tools.call("board.save", {})
    with pytest.raises(ValueError):
        RoleTools(reviewer, snapshot, designer=object())


def test_lifecycle_requires_signed_current_stage_evidence():
    state = Lifecycle(project="test", design_author="designer", input_digest="a" * 64)
    report = VerificationReport(results=(), input_digest="a" * 64, design_author="designer")
    with pytest.raises(ValueError, match="Illegal"):
        state.advance(Stage.SCHEMATIC, report, actor="architect")
    with pytest.raises(ValueError, match="blocked"):
        state.advance(Stage.ARCHITECTURE, report, actor="architect")
    private = Ed25519PrivateKey.generate()
    now = datetime.now(UTC)
    data = {
        "issuer": "reviewer",
        "purpose": "approval",
        "check_id": "requirements.complete",
        "input_digest": "a" * 64,
        "reason": "Independent synthetic test review",
        "evidence": ["test"],
        "issued_at": now,
        "expires_at": now + timedelta(hours=1),
        "signature_base64": "",
    }
    attestation = Attestation.model_validate(data)
    signature = base64.b64encode(private.sign(attestation.payload())).decode()
    attestation = attestation.model_copy(update={"signature_base64": signature})
    trusted = {
        "reviewer": TrustedSigner(
            public_key_base64=base64.b64encode(private.public_key().public_bytes_raw()).decode(),
            roles=("reviewer",),
        )
    }
    advanced = state.advance(
        Stage.ARCHITECTURE, report, actor="architect", attestations=(attestation,), trusted=trusted
    )
    assert advanced.stage == Stage.ARCHITECTURE
    invalidated = advanced.invalidate("b" * 64, actor="designer", reason="Changed requirements")
    assert invalidated.stage == Stage.SPEC
    with pytest.raises(ValueError):
        invalidated.advance(
            Stage.ARCHITECTURE,
            report,
            actor="architect",
            attestations=(attestation,),
            trusted=trusted,
        )


def test_independent_review_does_not_autoapprove_clean_drc(tmp_path):
    (tmp_path / "state.txt").write_text("test")
    snapshot = capture(tmp_path, (Path("state.txt"),), "rev")
    report = VerificationReport(results=(), input_digest=snapshot.identity.digest)
    packet = ReviewPacket(
        snapshot=snapshot, verification=report, design_author="designer", requested_scope=("power",)
    )

    def invoke(data):
        return {
            "reviewer": "independent",
            "design_revision": "rev",
            "snapshot_sha256": snapshot.identity.digest,
            "scope": ["power"],
            "findings": [],
            "limitations": [],
        }

    review, check = independent_review(packet, "independent", invoke)
    assert check.status == "WARN"
    with pytest.raises(ValueError):
        independent_review(packet, "designer", invoke)
    with pytest.raises(ValueError):
        independent_review(packet, "another", invoke)

    def limited(data):
        result = invoke(data)
        result["limitations"] = ["No regulator datasheet"]
        return result

    assert independent_review(packet, "independent", limited)[1].status == "FAIL"
    finding = Finding(
        id="F1",
        title="Supply mismatch",
        severity="blocker",
        evidence=("test",),
        explanation="Declared test mismatch",
        suggested_remediation="Correct supply",
    )
    old = review.model_copy(update={"findings": (finding,)})
    with pytest.raises(ValueError, match="disappear"):
        reconcile(old, review, "designer")
    working = finding.transition("in_progress")
    fixed = working.transition("resolved", ("Independent recheck",))
    previous = old.model_copy(update={"findings": (working,)})
    current = old.model_copy(update={"findings": (fixed,)})
    assert reconcile(previous, current, "designer").findings[0].id == "F1"


def test_critical_nets_missing_stale_self_and_topic_coverage():
    nets = (Net(name="CLK", classes=("clock",), rationale="Sampling clock"),)
    review = NetReview(
        net="CLK",
        reviewer="other",
        input_digest="a" * 64,
        topics=("timing", "termination", "return-path", "jitter"),
        evidence=("test",),
    )
    args = {"input_digest": "a" * 64, "designer": "designer", "source_nets": frozenset({"CLK"})}
    assert check_critical_nets(nets, (review,), **args).exit_code == 0
    assert check_critical_nets(nets, (), **args).exit_code == 1
    for change in [
        {"reviewer": "designer"},
        {"input_digest": "b" * 64},
        {"topics": ("timing",)},
        {"unresolved": ("Plane split",)},
    ]:
        assert check_critical_nets(nets, (review.model_copy(update=change),), **args).exit_code == 1
    assert (
        check_critical_nets(
            nets, (review,), **{**args, "source_nets": frozenset({"CLK", "UNKNOWN"})}
        ).exit_code
        == 1
    )


def test_native_anchor_floorplan_and_distance_boundaries(tmp_path):
    # Parser fixture only, not a complete KiCad PCB.
    board = tmp_path / "test.kicad_pcb"
    board.write_text(
        '(kicad_pcb (footprint "test" (layer "F.Cu") (at 1 1) '
        '(property "Reference" "U1")) (footprint "test" (layer "F.Cu") '
        '(at 4 5) (property "Reference" "C1")))'
    )
    snapshot = capture(tmp_path, (Path("test.kicad_pcb"),), "rev")
    placements = placements_from_snapshot(snapshot, {"U1": "logic", "C1": "logic"})
    region = {
        "id": "logic",
        "function": "logic",
        "minimum": {"x_mm": 0, "y_mm": 0},
        "maximum": {"x_mm": 10, "y_mm": 10},
    }
    floorplan = Floorplan(
        input_digest=snapshot.identity.digest,
        regions=(region,),
        placements=placements,
        outline=region,
    )
    assert floorplan.audit().exit_code == 0
    rule = DistanceRule(
        id="decoupling-anchor",
        reference="U1",
        other="C1",
        maximum_mm=5,
        rationale="Synthetic anchor distance, not pad-loop inductance",
        evidence=("test",),
    )
    assert check_distances(floorplan, (rule,)).exit_code == 0  # 3-4-5 boundary
    assert check_distances(floorplan, (rule.model_copy(update={"maximum_mm": 4.9}),)).exit_code == 1
    assert (
        check_distances(floorplan, (rule.model_copy(update={"other": "absent"}),)).results[0].status
        == "SKIP"
    )


def test_remediation_preserves_findings_and_requires_reverification(tmp_path):
    from astra_pcb.agents.review import remediate
    from astra_pcb.models.engineering import Review

    source = tmp_path / "note.txt"
    source.write_text("before")
    snapshot = capture(tmp_path, (Path("note.txt"),), "rev")
    finding = Finding(
        id="F1",
        title="Declared fault",
        severity="major",
        evidence=("test",),
        explanation="Synthetic counterexample",
        suggested_remediation="Change text",
    )
    review = Review(
        reviewer="independent",
        design_revision="rev",
        snapshot_sha256=snapshot.identity.digest,
        scope=("test",),
        findings=(finding,),
        limitations=(),
    )

    def apply(findings):
        assert findings[0].id == "F1"
        source.write_text("after")

    result = remediate(
        review,
        ("F1",),
        root=tmp_path,
        sources=(Path("note.txt"),),
        revision="rev",
        designer="designer",
        apply=apply,
        output=tmp_path / "run",
    )
    assert result.review_required
    assert result.findings[0].id == "F1" and result.findings[0].status == "in_progress"
    assert result.mutation.prior_evidence_invalidated
    assert (
        result.mutation.verification.results[0].status == "SKIP"
    )  # no native source in this fixture
    with pytest.raises(ValueError, match="stale"):
        remediate(
            review,
            ("F1",),
            root=tmp_path,
            sources=(Path("note.txt"),),
            revision="rev",
            designer="designer",
            apply=apply,
            output=tmp_path / "second",
        )
