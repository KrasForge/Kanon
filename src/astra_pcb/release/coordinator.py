"""Fail-closed local release transaction. Never uploads, orders, or trusts LLM check results."""

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.agents.critical_nets import Net, NetReview, check_critical_nets
from astra_pcb.bom import check_board_bom, check_bom
from astra_pcb.bom.importer import import_bom
from astra_pcb.config import load_yaml, validate_document
from astra_pcb.kicad import KiCadCLI
from astra_pcb.kicad.reports import interpret
from astra_pcb.kicad.snapshot import nodes, parse_sexpr
from astra_pcb.manufacturing import ManufacturingProfile
from astra_pcb.mechanical import check_step
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport
from astra_pcb.models.engineering import Review
from astra_pcb.models.provenance import InputIdentity, canonical_digest, file_digest
from astra_pcb.release import GateConfig, ReleaseGate, evaluate
from astra_pcb.release.artifacts import Manifest, artifact, check_export
from astra_pcb.release.attestations import Attestation, TrustedSigner
from astra_pcb.verification.process import run


class ReleaseProject(StrictModel):
    design_author: str = Field(min_length=1)
    spec: str
    schematic: str
    pcb: str
    bom: str
    manufacturing_profile: str
    critical_net_plan: str | None = None
    additional_inputs: tuple[str, ...] = ()
    gerber_layers: tuple[str, ...] = Field(min_length=3)
    parity: Literal[True] = True
    pick_and_place: bool = True

    @model_validator(mode="after")
    def paths(self):
        for path in self.paths_to_hash():
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError("Release input must be project-relative")
        if (
            len(self.gerber_layers) != len(set(self.gerber_layers))
            or "Edge.Cuts" not in self.gerber_layers
        ):
            raise ValueError("Distinct layers including Edge.Cuts required")
        return self

    def paths_to_hash(self) -> tuple[str, ...]:
        return (
            self.spec,
            self.schematic,
            self.pcb,
            self.bom,
            self.manufacturing_profile,
            *((self.critical_net_plan,) if self.critical_net_plan else ()),
            *self.additional_inputs,
        )


def identify(
    root: Path, project: ReleaseProject, config_file: Path, gate_file: Path
) -> InputIdentity:
    revision = run(["git", "rev-parse", "HEAD"], cwd=root)
    if revision.exit_code != 0 or not revision.stdout.strip():
        raise ValueError("Release requires a Git revision")
    # Source files may be dirty; their exact bytes are additionally bound by the manifest.
    paths = set(project.paths_to_hash()) | {
        str(config_file.resolve().relative_to(root.resolve())),
        str(gate_file.resolve().relative_to(root.resolve())),
    }
    pcb = Path(project.pcb)
    for suffix in (".kicad_pro", ".kicad_dru"):
        sibling = pcb.with_suffix(suffix)
        if (root / sibling).exists():
            paths.add(str(sibling))
    # Capture local hierarchy/libraries/models used by the KiCad adapters, not just root files.
    for folder in {Path(project.schematic).parent, Path(project.pcb).parent}:
        for path in (root / folder).rglob("*"):
            if any(part in {".git", ".venv", "artifacts"} for part in path.relative_to(root).parts):
                continue
            if path.is_file() and (
                path.suffix
                in {
                    ".kicad_sch",
                    ".kicad_pcb",
                    ".kicad_pro",
                    ".kicad_dru",
                    ".kicad_sym",
                    ".kicad_mod",
                    ".step",
                    ".stp",
                    ".wrl",
                }
                or path.name in {"fp-lib-table", "sym-lib-table"}
            ):
                paths.add(str(path.relative_to(root)))
    files = {}
    for name in sorted(paths):
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError("Missing or escaping release input: " + name)
        files[name] = file_digest(path)
    return InputIdentity(revision=revision.stdout.strip(), files=files)


def release(
    root: Path,
    project: ReleaseProject,
    identity: InputIdentity,
    gates: GateConfig,
    reviews: tuple[Review, ...],
    attestations: tuple[Attestation, ...],
    trusted: dict[str, TrustedSigner],
    output: Path,
    *,
    adapter: KiCadCLI | None = None,
    spec_schema: Path = Path("schemas/design-spec.schema.json"),
    net_reviews: tuple[NetReview, ...] = (),
) -> VerificationReport:
    """Trusted coordinator owns adapter/trust configuration; agent tools cannot replace them.

    Caller obtains identity via identify immediately before invocation. Public CLI never
    accepts automation-result JSON or an arbitrary process command as a release check.
    """
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    checks = []
    adapter = adapter or KiCadCLI()

    def finish() -> VerificationReport:
        report = VerificationReport(
            results=tuple(checks), input_digest=identity.digest, design_author=project.design_author
        )
        (output / "release-report.json").write_text(report.model_dump_json(indent=2))
        return report

    try:
        identity.verify(root)
        if not set(project.paths_to_hash()) <= identity.files.keys():
            raise ValueError("Release identity omits required input files")
        profile = ManufacturingProfile.model_validate(
            load_yaml(root / project.manufacturing_profile)
        )
        checks.append(profile.check())
        board_tree = parse_sexpr((root / project.pcb).read_text())
        layer_node = next(
            (n for n in board_tree if isinstance(n, list) and n and n[0] == "layers"), None
        )
        thickness_node = next(nodes(board_tree, "thickness"), None)
        if layer_node is None or thickness_node is None:
            raise ValueError("Native layer/thickness data missing")
        copper_layers = {
            n[1]
            for n in layer_node[1:]
            if isinstance(n, list) and len(n) > 1 and n[1].endswith(".Cu")
        }
        if (
            len(copper_layers) != profile.layer_count
            or abs(float(thickness_node[1]) - profile.board_thickness_mm) > 1e-6
            or not copper_layers <= set(project.gerber_layers)
        ):
            raise ValueError(
                "Native stackup or exported copper layers differ from manufacturing profile"
            )
        for model in nodes(board_tree, "model"):
            if len(model) < 2:
                raise ValueError("Malformed 3D model reference")
            model_path = model[1].replace("${KIPRJMOD}", str((root / project.pcb).parent.resolve()))
            if "$" in model_path:
                raise ValueError(
                    "External/environment 3D model reference must be frozen locally first"
                )
            resolved = ((root / project.pcb).parent / model_path).resolve()
            if (
                not resolved.is_relative_to(root.resolve())
                or str(resolved.relative_to(root.resolve())) not in identity.files
            ):
                raise ValueError("3D model absent from release input identity")
        validate_document(root / project.spec, spec_schema)
        checks.append(
            CheckResult(
                check_id="spec.schema",
                name="Design specification",
                status=CheckStatus.PASS,
                message="Specification schema/semantics valid",
            )
        )
        bom_items = import_bom(root / project.bom)
        checks.extend(check_bom(bom_items))
        checks.append(check_board_bom(bom_items, (root / project.pcb).read_text()))
        source_nets = frozenset(n[-1] for n in nodes(board_tree, "net") if len(n) >= 3 and n[-1])
        if not project.critical_net_plan:
            raise ValueError("Critical-net classification plan is required for release")
        plan = load_yaml(root / project.critical_net_plan)
        classifications = tuple(Net.model_validate(n) for n in plan["nets"])
        if net_reviews:
            binding = "critical-net-reviews-sha256:" + canonical_digest(
                {"reviews": [r.model_dump(mode="json") for r in net_reviews]}
            )
            authorized = set()
            for attestation in attestations:
                if (
                    attestation.check_id == "critical-nets.review"
                    and attestation.purpose == "approval"
                    and binding in attestation.evidence
                ):
                    attestation.verify(
                        trusted,
                        now=datetime.now(UTC),
                        digest=identity.digest,
                        design_author=project.design_author,
                    )
                    authorized.add(attestation.issuer)
            if not {r.reviewer for r in net_reviews} <= authorized:
                raise ValueError("Critical-net review payload lacks its reviewer's signed binding")
        coverage = check_critical_nets(
            classifications,
            net_reviews,
            input_digest=identity.digest,
            designer=project.design_author,
            source_nets=source_nets,
        )
        checks.append(
            CheckResult(
                check_id="critical-nets.coverage",
                name="Current native critical-net coverage",
                status=CheckStatus.PASS if coverage.exit_code == 0 else CheckStatus.FAIL,
                message="Current native net inventory and class-specific reviews match"
                if coverage.exit_code == 0
                else "Missing/stale/incomplete native critical-net review",
                evidence=(coverage.model_dump_json(),),
            )
        )
        matching = [
            r
            for r in reviews
            if r.snapshot_sha256 == identity.digest
            and r.design_revision == identity.revision
            and r.reviewer != project.design_author
        ]
        if len(matching) != len(reviews) or not matching or any(r.has_blockers for r in matching):
            raise ValueError("Missing, stale, self-authored or blocking independent review")
        for kind, path in [("erc", project.schematic), ("drc", project.pcb)]:
            dest = output / f"{kind}.json"
            result = adapter.check(
                kind, root / path, dest, parity=project.parity if kind == "drc" else False
            )
            checks.extend(interpret(kind, result, dest, root / path).results)
        # Required baseline cannot be removed by a supplied gate file.
        mandatory = {
            "requirements.complete": "MANUAL",
            "architecture.review": "MANUAL",
            "components.review": "MANUAL",
            "schematic.review": "MANUAL",
            "power.review": "MANUAL",
            "critical-nets.review": "MANUAL",
            "critical-nets.coverage": "AUTOMATED",
            "mechanical.review": "MANUAL",
            "dfm.review": "MANUAL",
            "review.independent": "MANUAL",
            "schematic.erc": "AUTOMATED",
            "pcb.drc": "AUTOMATED",
            "bom.integrity": "AUTOMATED",
            "bom.parity": "AUTOMATED",
            "manufacturing.profile": "AUTOMATED",
            "spec.schema": "AUTOMATED",
        }
        configured = {g.check_id: g for g in gates.gates}
        for name, mode in mandatory.items():
            if name in configured and (
                configured[name].mode != mode or not configured[name].mandatory
            ):
                raise ValueError("Project cannot weaken mandatory release gate: " + name)
            configured.setdefault(name, ReleaseGate(check_id=name, mode=mode))
        exports = {"export.gerbers", "export.drill", "export.step", "export.pos"}
        before = GateConfig(
            gates=tuple(g for g in configured.values() if g.check_id not in exports)
        )
        report = VerificationReport(
            results=tuple(checks), input_digest=identity.digest, design_author=project.design_author
        )
        valid_attestations = tuple(
            a for a in attestations if a.check_id in {g.check_id for g in before.gates}
        )
        if len(valid_attestations) != len(attestations):
            raise ValueError(
                "Unexpected export/unknown attestation; cannot pre-approve future output"
            )
        decisions = evaluate(
            before,
            report,
            expected_digest=identity.digest,
            attestations=attestations,
            trusted=trusted,
        )
        (output / "verification.json").write_text(report.model_dump_json(indent=2))
        (output / "gates.json").write_text(decisions.model_dump_json(indent=2))
        if decisions.exit_code:
            checks.append(
                CheckResult(
                    check_id="release.transaction",
                    name="Release transaction",
                    status=CheckStatus.FAIL,
                    message="Mandatory pre-export checks/approvals blocked release",
                )
            )
            return finish()
        checks = list(decisions.results)
        for kind in ["gerbers", "drill", "step", *(["pos"] if project.pick_and_place else [])]:
            dest = output / ({"step": "board.step", "pos": "positions.csv"}.get(kind, kind))
            result = adapter.export(
                kind,
                root / project.pcb,
                dest,
                layers=project.gerber_layers if kind == "gerbers" else (),
            )
            check = (
                check_step(result, dest)
                if kind == "step"
                else check_export(
                    kind, result, expected_layers=project.gerber_layers if kind == "gerbers" else ()
                )
            )
            checks.append(check)
            (output / f"{kind}-receipt.json").write_text(result.model_dump_json(indent=2))
            if check.status != CheckStatus.PASS:
                checks.append(
                    CheckResult(
                        check_id="release.transaction",
                        name="Release transaction",
                        status=CheckStatus.FAIL,
                        message="Export failed; package not released",
                    )
                )
                return finish()
        identity.verify(root)
        source_dir = output / "sources"
        source_dir.mkdir()
        for name in identity.files:
            target = source_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
            if file_digest(target) != identity.files[name]:
                raise ValueError("Source changed while packaging")
        (output / "reviews.json").write_text(
            json.dumps([r.model_dump(mode="json") for r in reviews], indent=2)
        )
        (output / "attestations.json").write_text(
            json.dumps([a.model_dump(mode="json") for a in attestations], indent=2)
        )
        checks.append(
            CheckResult(
                check_id="release.transaction",
                name="Release transaction",
                status=CheckStatus.WARN,
                message="Package prepared; fresh artifact review/approval required before release",
            )
        )
        final = finish()
        (output / "release-report.json").rename(output / "release-preview.json")
        roles = {
            str(source_dir / project.schematic): "schematic",
            str(source_dir / project.pcb): "pcb",
            str(source_dir / project.bom): "bom",
            str(source_dir / project.manufacturing_profile): "manufacturing-profile",
            str(output / "reviews.json"): "review",
            str(output / "verification.json"): "verification",
            str(output / "release-preview.json"): "release-report",
            str(output / "board.step"): "step",
        }
        entries = []
        for path in sorted(p for p in output.rglob("*") if p.is_file()):
            role = roles.get(str(path), "supporting-evidence")
            if path.parent == output / "gerbers" and path.suffix == ".gbr":
                role = "gerber"
            if path.parent == output / "drill" and path.suffix == ".drl":
                role = "drill"
            if path.name == "positions.csv":
                role = "pick-and-place"
            entries.append(artifact(output, path, role))
        manifest = Manifest(
            release_id=str(uuid.uuid4()),
            inputs=identity,
            artifacts=tuple(entries),
            design_author=project.design_author,
        )
        manifest.verify(output)
        (output / "candidate-manifest.json").write_text(manifest.model_dump_json(indent=2))
        return final
    except (OSError, ValueError, KeyError) as exc:
        checks = [c for c in checks if c.check_id != "release.transaction"]
        checks.append(
            CheckResult(
                check_id="release.transaction",
                name="Release transaction",
                status=CheckStatus.ERROR,
                message=str(exc),
            )
        )
        return finish()


def finalize_release(
    root: Path,
    output: Path,
    attestations: tuple[Attestation, ...],
    trusted: dict[str, TrustedSigner],
) -> VerificationReport:
    """Approve exactly the prepared artifact set, never pre-approve future Gerber output."""
    if (output / "manifest.json").exists() or (output / "release-report.json").exists():
        raise FileExistsError("Release already finalized or final report path occupied")
    candidate = Manifest.model_validate_json((output / "candidate-manifest.json").read_text())
    candidate.verify(output)
    candidate.inputs.verify(root)
    revision = run(["git", "rev-parse", "HEAD"], cwd=root)
    if revision.exit_code != 0 or revision.stdout.strip() != candidate.inputs.revision:
        raise ValueError("Git revision changed since release preparation")
    artifact_digest = canonical_digest(candidate.model_dump(mode="json"))
    gates = GateConfig(
        gates=(
            ReleaseGate(check_id="gerber.review", mode="MANUAL"),
            ReleaseGate(check_id="review.final-artifacts", mode="MANUAL"),
        )
    )
    decisions = evaluate(
        gates,
        VerificationReport(
            results=(), input_digest=artifact_digest, design_author=candidate.design_author
        ),
        expected_digest=artifact_digest,
        attestations=attestations,
        trusted=trusted,
    )
    if decisions.exit_code:
        return decisions  # Keep immutable candidate; no final release artifacts created.
    preview = VerificationReport.model_validate_json((output / "release-preview.json").read_text())
    if any(
        c.status != CheckStatus.PASS for c in preview.results if c.check_id != "release.transaction"
    ):
        raise ValueError("Prepared gates/exports were not satisfied")
    final = VerificationReport(
        input_digest=candidate.inputs.digest,
        design_author=candidate.design_author,
        results=tuple(c for c in preview.results if c.check_id != "release.transaction")
        + decisions.results
        + (
            CheckResult(
                check_id="release.transaction",
                name="Release transaction",
                status=CheckStatus.PASS,
                message="Source and artifact gates satisfied; no order placed",
            ),
        ),
    )
    # Final files are new; every byte approved in the candidate remains available unchanged.
    (output / "release-report.json").write_text(final.model_dump_json(indent=2))
    (output / "artifact-approvals.json").write_text(
        json.dumps([a.model_dump(mode="json") for a in attestations], indent=2)
    )
    entries = [
        a.model_copy(update={"role": "supporting-evidence"}) if a.role == "release-report" else a
        for a in candidate.artifacts
    ]
    entries.extend(
        artifact(output, output / name, role)
        for name, role in [
            ("release-report.json", "release-report"),
            ("artifact-approvals.json", "supporting-evidence"),
            ("candidate-manifest.json", "supporting-evidence"),
        ]
    )
    manifest = Manifest(
        release_id=candidate.release_id,
        inputs=candidate.inputs,
        artifacts=tuple(entries),
        design_author=candidate.design_author,
    )
    manifest.verify(output)
    (output / "manifest.json").write_text(manifest.model_dump_json(indent=2))
    return final
