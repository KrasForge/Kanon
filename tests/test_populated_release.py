"""Real KiCad pipeline; only human approvals and fab capability evidence are synthetic.

The project-owned passive geometry is a software qualification coupon, not a purchasable BOM.
"""

import base64
import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from astra_pcb.agents.critical_nets import TOPICS, NetClass, NetReview
from astra_pcb.config import load_yaml, validate_document
from astra_pcb.models.engineering import Review
from astra_pcb.models.provenance import canonical_digest
from astra_pcb.release import GateConfig
from astra_pcb.release.artifacts import Manifest
from astra_pcb.release.attestations import Attestation, TrustedSigner
from astra_pcb.release.coordinator import ReleaseProject, finalize_release, identify, release

ROOT = Path(__file__).resolve().parents[1]


def synthetic_sign(private, check_id, digest, evidence=("TEST ONLY; not manufacturing approval",)):
    now = datetime.now(UTC)
    value = Attestation(
        issuer="test-independent",
        purpose="approval",
        check_id=check_id,
        input_digest=digest,
        reason="Synthetic CI authorization only",
        evidence=evidence,
        issued_at=now,
        expires_at=now + timedelta(hours=1),
        signature_base64="",
    )
    return value.model_copy(
        update={"signature_base64": base64.b64encode(private.sign(value.payload())).decode()}
    )


@pytest.mark.integration
@pytest.mark.skipif(not shutil.which("kicad-cli"), reason="Actual KiCad runtime unavailable")
def test_real_populated_two_phase_release_and_negative_control(tmp_path):
    root = tmp_path / "source"
    shutil.copytree(ROOT / "examples/populated-fixture", root)
    profile = load_yaml(ROOT / "config/manufacturing/jlcpcb-4layer.yaml")
    profile.update(
        name="SYNTHETIC CI profile",
        status="QUALIFIED",
        capabilities_checked_at=datetime.now(UTC).isoformat(),
        qualification_evidence=["TEST ONLY: no actual fab capability claim"],
        layer_count=2,
    )
    (root / "profile.yaml").write_text(yaml.safe_dump(profile))
    gates = GateConfig.model_validate(load_yaml(ROOT / "config/release-gates.yaml"))
    (root / "gates.yaml").write_text(yaml.safe_dump(gates.model_dump(mode="json")))
    project = ReleaseProject.model_validate(load_yaml(root / "release.yaml"))
    for args in [
        ("init", "-q"),
        ("add", "."),
        (
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "Synthetic software qualification coupon",
        ),
    ]:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    validate_document(root / project.spec, ROOT / "schemas/design-spec.schema.json")
    identity = identify(root, project, root / "release.yaml", root / "gates.yaml")
    private = Ed25519PrivateKey.generate()
    trusted = {
        "test-independent": TrustedSigner(
            public_key_base64=base64.b64encode(private.public_key().public_bytes_raw()).decode(),
            roles=("reviewer",),
        )
    }
    review = Review(
        reviewer="test-independent",
        design_revision=identity.revision,
        snapshot_sha256=identity.digest,
        scope=("Synthetic CI coupon only",),
        findings=(),
        limitations=(),
    )
    nets = tuple(
        NetReview(
            net=n,
            reviewer="test-independent",
            input_digest=identity.digest,
            topics=tuple(sorted(TOPICS[NetClass.POWER])),
            evidence=("Synthetic class coverage fixture",),
        )
        for n in ("/A", "/B")
    )
    binding = "critical-net-reviews-sha256:" + canonical_digest(
        {"reviews": [n.model_dump(mode="json") for n in nets]}
    )
    signatures = tuple(
        synthetic_sign(
            private,
            g.check_id,
            identity.digest,
            (binding,) if g.check_id == "critical-nets.review" else ("Synthetic test evidence",),
        )
        for g in gates.gates
        if g.mode == "MANUAL"
    )
    output = tmp_path / "candidate"
    report = release(
        root,
        project,
        identity,
        gates,
        (review,),
        signatures,
        trusted,
        output,
        spec_schema=ROOT / "schemas/design-spec.schema.json",
        net_reviews=nets,
    )
    assert report.exit_code == 2, report.model_dump_json(indent=2)
    assert not (output / "manifest.json").exists()
    assert finalize_release(root, output, (), trusted).exit_code == 1
    candidate = Manifest.model_validate_json((output / "candidate-manifest.json").read_text())
    artifact_digest = canonical_digest(candidate.model_dump(mode="json"))
    artifact_approvals = tuple(
        synthetic_sign(private, name, artifact_digest)
        for name in ("gerber.review", "review.final-artifacts")
    )
    assert finalize_release(root, output, artifact_approvals, trusted).exit_code == 0
    Manifest.model_validate_json((output / "manifest.json").read_text()).verify(output)
    identity.verify(root)
    verification = json.loads((output / "verification.json").read_text())
    assert {c["check_id"]: c["status"] for c in verification["results"]}["pcb.drc"] == "PASS"
    # A source mutation invalidates even prior valid signatures.
    board = root / project.pcb
    board.write_text(board.read_text().replace('(net "/A")', '(net "/B")', 1))
    blocked = release(
        root,
        project,
        identity,
        gates,
        (review,),
        signatures,
        trusted,
        tmp_path / "changed",
        spec_schema=ROOT / "schemas/design-spec.schema.json",
        net_reviews=nets,
    )
    assert blocked.exit_code == 1 and not (tmp_path / "changed/candidate-manifest.json").exists()
