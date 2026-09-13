"""Release transaction tests use explicit fake exporters; real tools tested separately."""

import base64
import json
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from astra_pcb.bom import BOMItem, check_board_bom
from astra_pcb.config import load_yaml
from astra_pcb.kicad import KiCadCLI
from astra_pcb.manufacturing import Feature, ManufacturingProfile, check_dfm
from astra_pcb.mechanical import check_step
from astra_pcb.models import CheckResult, VerificationReport
from astra_pcb.models.engineering import Review
from astra_pcb.models.provenance import canonical_digest, file_digest
from astra_pcb.release import GateConfig
from astra_pcb.release.artifacts import Manifest, check_export
from astra_pcb.release.attestations import Attestation, TrustedSigner
from astra_pcb.release.coordinator import ReleaseProject, finalize_release, identify, release
from astra_pcb.verification.process import ProcessResult

ROOT = Path(__file__).resolve().parents[1]


def sign(private, gate, digest):
    now = datetime.now(UTC)
    value = Attestation(
        issuer="independent",
        purpose="approval",
        check_id=gate,
        input_digest=digest,
        reason="Synthetic contract-test approval; never manufacturing authorization",
        evidence=("fixture",),
        issued_at=now,
        expires_at=now + timedelta(hours=1),
        signature_base64="",
    )
    return value.model_copy(
        update={"signature_base64": base64.b64encode(private.sign(value.payload())).decode()}
    )


class FakeExporter:
    def __init__(self):
        self.exports = []

    def check(self, kind, source, output, **kwargs):
        return ProcessResult(command=("fake",), exit_code=0, input_digest="a" * 64)

    def export(self, kind, source, output, **kwargs):
        self.exports.append(kind)
        if kind in {"gerbers", "drill"}:
            output.mkdir()
            if kind == "gerbers":
                for layer in kwargs["layers"]:
                    (output / ("board-" + layer.replace(".", "_") + ".gbr")).write_text(
                        "%FSLAX46Y46*%\n%MOMM*%\n%TF.FileFunction,"
                        + {
                            "F.Cu": "Copper,L1,Top",
                            "B.Cu": "Copper,L2,Bot",
                            "Edge.Cuts": "Profile,NP",
                        }[layer]
                        + "*%\nM02*\n"
                    )
            else:
                (output / "board.drl").write_text("M48\nMETRIC\n%\nM30\n")
            files = tuple(output.iterdir())
        else:
            output.write_text(
                "ISO-10303-21;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"
                if kind == "step"
                else "Ref,PosX,PosY,Rot,Side\nR1,1,1,0,top\n"
            )
            files = (output,)
        return ProcessResult(
            command=("fake",),
            exit_code=0,
            input_digest="a" * 64,
            artifacts=tuple(str(f.resolve()) for f in files),
            artifact_hashes={str(f.resolve()): file_digest(f) for f in files},
        )


@pytest.fixture
def package(tmp_path, monkeypatch):
    (tmp_path / "spec.yaml").write_text(
        (ROOT / "examples/minimal-board/design-spec.yaml").read_text()
    )
    # Native-parser-only fixture with one test reference. The FakeExporter never invokes KiCad.
    (tmp_path / "board.kicad_pcb").write_text(
        "(kicad_pcb (general (thickness 1.6)) "
        '(layers (0 "F.Cu" signal) (2 "B.Cu" signal)) (footprint "TEST:0603" '
        '(property "Reference" "R1") (property "Value" "1k")))'
    )
    (tmp_path / "board.kicad_sch").write_text("(kicad_sch)")
    (tmp_path / "bom.json").write_text(
        '[{"reference":"R1","quantity":1,"value":"1k","package":"TEST:0603","mpn":"TEST-PART"}]'
    )
    profile = load_yaml(ROOT / "config/manufacturing/jlcpcb-4layer.yaml")
    profile.update(
        status="QUALIFIED",
        capabilities_checked_at=datetime.now(UTC).isoformat(),
        qualification_evidence=["Synthetic profile; no real manufacturer qualification"],
        layer_count=2,
    )
    (tmp_path / "profile.yaml").write_text(yaml.safe_dump(profile))
    project = ReleaseProject(
        design_author="designer",
        spec="spec.yaml",
        schematic="board.kicad_sch",
        pcb="board.kicad_pcb",
        bom="bom.json",
        manufacturing_profile="profile.yaml",
        gerber_layers=("F.Cu", "B.Cu", "Edge.Cuts"),
    )
    (tmp_path / "release.yaml").write_text(yaml.safe_dump(project.model_dump(mode="json")))
    gates = GateConfig.model_validate(load_yaml(ROOT / "config/release-gates.yaml"))
    (tmp_path / "gates.yaml").write_text(yaml.safe_dump(gates.model_dump(mode="json")))
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
            "Synthetic release fixture",
        ),
    ]:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)
    identity = identify(tmp_path, project, tmp_path / "release.yaml", tmp_path / "gates.yaml")
    review = Review(
        reviewer="independent",
        design_revision=identity.revision,
        snapshot_sha256=identity.digest,
        scope=("all declared fixture scope",),
        findings=(),
        limitations=(),
    )
    private = Ed25519PrivateKey.generate()
    trusted = {
        "independent": TrustedSigner(
            public_key_base64=base64.b64encode(private.public_key().public_bytes_raw()).decode(),
            roles=("reviewer",),
        )
    }
    approvals = tuple(
        sign(private, g.check_id, identity.digest) for g in gates.gates if g.mode == "MANUAL"
    )
    monkeypatch.setattr(
        "astra_pcb.release.coordinator.interpret",
        lambda kind, *args: VerificationReport(
            results=(
                CheckResult(
                    check_id="schematic.erc" if kind == "erc" else "pcb.drc",
                    name=kind,
                    status="PASS",
                    message="Fake tool contract",
                ),
            )
        ),
    )
    return tmp_path, project, identity, gates, (review,), approvals, trusted, private


def prepare(package, exporter=None):
    root, project, identity, gates, reviews, approvals, trusted, _ = package
    return release(
        root,
        project,
        identity,
        gates,
        reviews,
        approvals,
        trusted,
        root / "output",
        adapter=exporter or FakeExporter(),
        spec_schema=ROOT / "schemas/design-spec.schema.json",
    )


def test_prepare_then_exact_artifact_approval(package):
    root, *_ = package
    assert prepare(package).exit_code == 2
    assert not (root / "output/manifest.json").exists()
    candidate = Manifest.model_validate_json((root / "output/candidate-manifest.json").read_text())
    assert finalize_release(root, root / "output", (), package[-2]).exit_code == 1
    digest = canonical_digest(candidate.model_dump(mode="json"))
    approvals = tuple(
        sign(package[-1], name, digest) for name in ("gerber.review", "review.final-artifacts")
    )
    assert finalize_release(root, root / "output", approvals, package[-2]).exit_code == 0
    manifest = Manifest.model_validate_json((root / "output/manifest.json").read_text())
    manifest.verify(root / "output")
    assert {"gerber", "drill", "bom", "step", "review", "verification"} <= {
        a.role for a in manifest.artifacts
    }


def test_changed_artifact_rejects_signed_approval(package):
    assert prepare(package).exit_code == 2
    root = package[0]
    out = root / "output"
    candidate = Manifest.model_validate_json((out / "candidate-manifest.json").read_text())
    digest = canonical_digest(candidate.model_dump(mode="json"))
    approvals = tuple(
        sign(package[-1], name, digest) for name in ("gerber.review", "review.final-artifacts")
    )
    (out / "gerbers/board-F_Cu.gbr").write_text("altered")
    with pytest.raises(ValueError, match="changed"):
        finalize_release(root, out, approvals, package[-2])
    assert not (out / "manifest.json").exists()


def test_failed_gate_stops_exports(package, monkeypatch):
    monkeypatch.setattr(
        "astra_pcb.release.coordinator.interpret",
        lambda kind, *args: VerificationReport(
            results=(
                CheckResult(
                    check_id="schematic.erc" if kind == "erc" else "pcb.drc",
                    name=kind,
                    status="FAIL",
                    message="Injected fault",
                ),
            )
        ),
    )
    exporter = FakeExporter()
    assert prepare(package, exporter).exit_code == 1
    assert exporter.exports == []
    assert not (package[0] / "output/candidate-manifest.json").exists()


def test_unqualified_example_profile_and_dfm_limits():
    profile = ManufacturingProfile.model_validate(
        load_yaml(ROOT / "config/manufacturing/jlcpcb-4layer.yaml")
    )
    assert profile.check().status == "FAIL"
    result = check_dfm(
        profile,
        (
            Feature(
                id="track",
                kind="trace",
                minimum_mm=0.1,
                source_object="TEST",
                evidence=("Measured fixture",),
            ),
        ),
        layer_count=4,
        thickness_mm=1.6,
    )
    assert result.results[-1].status == "FAIL"
    with pytest.raises(ValueError):
        ManufacturingProfile.model_validate({**profile.model_dump(), "status": "QUALIFIED"})


def test_bom_cannot_release_wrong_native_footprint():
    items = [BOMItem(reference="R1", value="1k", package="TEST:0603", mpn="TEST")]
    board = (
        '(kicad_pcb (footprint "TEST:0805" (property "Reference" "R1") (property "Value" "1k")))'
    )
    assert check_board_bom(items, board).status == "FAIL"
    assert check_board_bom(items, board.replace("0805", "0603")).status == "PASS"


@pytest.mark.integration
def test_real_export_envelopes_and_step_identity(tmp_path):
    if not shutil.which("kicad-cli"):
        pytest.skip("KiCad CLI unavailable")
    adapter = KiCadCLI()
    board = ROOT / "tests/fixtures/kicad/outline.kicad_pcb"
    layers = ("F.Cu", "B.Cu", "Edge.Cuts")
    gerbers = adapter.export("gerbers", board, tmp_path / "gerbers", layers=layers)
    assert check_export("gerbers", gerbers, expected_layers=layers).status == "PASS"
    assert check_export("gerbers", gerbers, expected_layers=(*layers, "In1.Cu")).status == "ERROR"
    drills = adapter.export("drill", board, tmp_path / "drill")
    assert check_export("drill", drills).status == "PASS"
    step = adapter.export("step", board, tmp_path / "board.step")
    assert check_step(step, tmp_path / "board.step").status == "PASS"
    (tmp_path / "board.step").write_text("changed")
    assert check_step(step, tmp_path / "board.step").status == "ERROR"


@pytest.mark.integration
def test_actual_gerber_layer_render(tmp_path):
    pytest.importorskip("gerbonara", reason="Optional visual extra unavailable")
    if not shutil.which("kicad-cli"):
        pytest.skip("KiCad CLI unavailable")
    from astra_pcb.manufacturing.visual import render_layers

    board = ROOT / "tests/fixtures/kicad/outline.kicad_pcb"
    KiCadCLI().export("gerbers", board, tmp_path / "gerbers", layers=("F.Cu", "B.Cu", "Edge.Cuts"))
    files = {
        "top copper": tmp_path / "gerbers/outline-F_Cu.gbr",
        "bottom copper": tmp_path / "gerbers/outline-B_Cu.gbr",
        "mechanical outline": tmp_path / "gerbers/outline-Edge_Cuts.gbr",
    }
    assert render_layers(files, tmp_path / "review.svg").status == "PASS"
    assert "<svg" in (tmp_path / "review.svg").read_text()


def test_minimal_spec_to_blocked_release_cli(tmp_path, capsys):
    from astra_pcb.cli import main

    assert main(["validate", str(ROOT / "examples/minimal-board/design-spec.yaml")]) == 0
    validation = json.loads(capsys.readouterr().out)
    assert validation["results"][0]["status"] == "PASS"
    # Deliberately lacks native design files; no fictional board is released by the walkthrough.
    assert (
        main(
            [
                "release",
                "--project",
                str(ROOT / "examples/minimal-board/release.yaml"),
                "--root",
                str(ROOT),
                "--output",
                str(tmp_path / "never-created"),
            ]
        )
        == 1
    )
    assert json.loads(capsys.readouterr().out)["status"] == "ERROR"
    assert not (tmp_path / "never-created/manifest.json").exists()
