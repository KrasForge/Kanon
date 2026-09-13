"""Acceptance tests for versioning, semantic inputs and authenticated gate policy."""

import base64
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from astra_pcb.config import load_yaml
from astra_pcb.config.specification import migrate_spec, validate_spec
from astra_pcb.models import CheckResult, VerificationReport
from astra_pcb.models.engineering import Decision, Finding, Review
from astra_pcb.models.provenance import InputIdentity, file_digest
from astra_pcb.release import GateConfig, ReleaseGate, evaluate
from astra_pcb.release.attestations import Attestation, TrustedSigner


def test_spec_semantics_and_migration():
    spec = load_yaml(Path("examples/minimal-board/design-spec.yaml"))
    validate_spec(spec)
    old = {**spec, "schema_version": "0.1"}
    old["requirements"] = old.pop("functional_requirements")
    assert migrate_spec(old) == spec
    assert old["schema_version"] == "0.1"
    spec["power_inputs"][0]["voltage"]["nominal_v"] = 5
    with pytest.raises(ValueError, match="nominal outside"):
        validate_spec(spec)


@pytest.mark.parametrize("failure", ["cycle", "domain", "duplicate", "temperature"])
def test_spec_semantic_failures(failure):
    spec = load_yaml(Path("examples/minimal-board/design-spec.yaml"))
    if failure == "cycle":
        spec["rails"] = [dict(id="A", source="B"), dict(id="B", source="A")]
    elif failure == "domain":
        spec["interfaces"][0]["voltage_domain"] = "absent"
    elif failure == "duplicate":
        spec["interfaces"][0]["id"] = "VIN"
    else:
        spec["environmental_limits"]["temperature_min_c"] = -300
    with pytest.raises(ValueError):
        validate_spec(spec)


def test_input_identity_detects_mutation_and_escape(tmp_path):
    design = tmp_path / "board"
    design.write_text("revision 1")
    identity = InputIdentity(revision="dirty", files={"board": file_digest(design)})
    identity.verify(tmp_path)
    assert len(identity.digest) == 64
    design.write_text("revision 2")
    with pytest.raises(ValueError, match="changed"):
        identity.verify(tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        InputIdentity(revision="x", files={"../outside": "0" * 64}).verify(tmp_path)


def signed_attestation(purpose="approval", issuer="reviewer", roles=("reviewer",)):
    private = Ed25519PrivateKey.generate()
    trusted = {
        issuer: TrustedSigner(
            public_key_base64=base64.b64encode(private.public_key().public_bytes_raw()).decode(),
            roles=roles,
        )
    }
    now = datetime.now(UTC)
    draft = Attestation(
        issuer=issuer,
        purpose=purpose,
        check_id="gate",
        input_digest="a" * 64,
        reason="explicit test decision",
        evidence=("review.json",),
        issued_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(hours=1),
        signature_base64="",
    )
    signed = draft.model_copy(
        update={"signature_base64": base64.b64encode(private.sign(draft.payload())).decode()}
    )
    return signed, trusted, now


def test_signed_manual_approval_and_no_self_review():
    attestation, trusted, now = signed_attestation()
    report = VerificationReport(results=(), input_digest="a" * 64, design_author="designer")
    config = GateConfig(gates=(ReleaseGate(check_id="gate", mode="MANUAL"),))
    assert (
        evaluate(
            config,
            report,
            expected_digest="a" * 64,
            attestations=(attestation,),
            trusted=trusted,
            now=now,
        ).exit_code
        == 0
    )
    with pytest.raises(ValueError, match="independent"):
        evaluate(
            config,
            report.model_copy(update={"design_author": "reviewer"}),
            expected_digest="a" * 64,
            attestations=(attestation,),
            trusted=trusted,
        )


@pytest.mark.parametrize("attack", ["tamper", "expired", "stale", "unknown", "missing_identity"])
def test_attestation_attacks(attack):
    attestation, trusted, now = signed_attestation()
    expected = "a" * 64
    if attack == "tamper":
        attestation = attestation.model_copy(update={"reason": "tampered"})
    elif attack == "expired":
        now += timedelta(days=1)
    elif attack == "stale":
        expected = "b" * 64
    elif attack == "unknown":
        trusted = {}
    elif attack == "missing_identity":
        expected = None
    with pytest.raises(ValueError):
        evaluate(
            GateConfig(gates=(ReleaseGate(check_id="gate", mode="MANUAL"),)),
            VerificationReport(results=(), input_digest="a" * 64, design_author="designer"),
            expected_digest=expected,
            attestations=(attestation,),
            trusted=trusted,
            now=now,
        )


def test_human_waiver_requires_policy_and_human_key():
    attestation, trusted, now = signed_attestation("waiver", "owner", ("human",))
    failed = CheckResult(check_id="gate", name="gate", status="ERROR", message="failed tool")
    report = VerificationReport(results=(failed,), input_digest="a" * 64)
    config = GateConfig(
        gates=(ReleaseGate(check_id="gate", mode="AUTOMATED", allow_human_waiver=True),)
    )
    result = evaluate(
        config,
        report,
        expected_digest="a" * 64,
        attestations=(attestation,),
        trusted=trusted,
        now=now,
    )
    assert result.exit_code == 0 and "Human waiver" in result.results[0].message
    denied = GateConfig(gates=(ReleaseGate(check_id="gate", mode="AUTOMATED"),))
    with pytest.raises(ValueError, match="policy"):
        evaluate(
            denied,
            report,
            expected_digest="a" * 64,
            attestations=(attestation,),
            trusted=trusted,
            now=now,
        )
    trusted["owner"] = trusted["owner"].model_copy(update={"roles": ("reviewer",)})
    with pytest.raises(ValueError, match="human"):
        evaluate(
            config,
            report,
            expected_digest="a" * 64,
            attestations=(attestation,),
            trusted=trusted,
            now=now,
        )


def test_finding_identity_transitions_and_review():
    finding = Finding(
        id="F-1",
        title="Wrong pad",
        severity="blocker",
        evidence=("pad table p4",),
        explanation="Pinout mismatch",
        suggested_remediation="Correct footprint",
    )
    with pytest.raises(ValueError, match="Illegal"):
        finding.transition("resolved", ("recheck",))
    in_progress = finding.transition("in_progress")
    with pytest.raises(ValidationError):
        in_progress.transition("resolved")
    resolved = in_progress.transition("resolved", ("independent recheck",))
    assert resolved.id == finding.id
    review = Review(
        reviewer="reviewer",
        design_revision="A",
        snapshot_sha256="a" * 64,
        scope=("pinout",),
        findings=(resolved,),
        limitations=(),
    )
    assert not review.has_blockers
    with pytest.raises(ValidationError, match="Duplicate"):
        Review.model_validate({**review.model_dump(), "findings": [finding, finding]})


def test_decision_markdown_roundtrip_and_evidence():
    decision = Decision(
        id="D1",
        decision="Select package",
        context="Assembly limits",
        alternatives=("larger package",),
        evidence=(
            {
                "document": "Fixture datasheet",
                "manufacturer": "Test only",
                "revision": "A",
                "page": "4",
                "extracted_constraint": "Synthetic fixture constraint",
                "source_location": "fixture.pdf",
            },
        ),
        calculations=("calculation.py",),
        risks=("assembly yield",),
        chosen_solution="reviewed package",
        consequences=("qualification needed",),
        invalidated_by=("different assembly process",),
    )
    assert Decision.from_markdown(decision.to_markdown()) == decision
    with pytest.raises(ValueError):
        Decision.from_markdown("No canonical evidence")


def test_report_legacy_roundtrip_and_future_rejection():
    report = VerificationReport.model_validate({"schema_version": "1.0", "results": []})
    assert VerificationReport.model_validate_json(report.model_dump_json()) == report
    with pytest.raises(ValidationError):
        VerificationReport(schema_version="999", results=())
    with pytest.raises(ValidationError):
        VerificationReport(results=(), created_at=datetime(2026, 1, 1))
    assert json.loads(report.model_dump_json())["schema_version"] == "1.0"
