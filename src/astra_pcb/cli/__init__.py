"""Repository-local CLI with deterministic checks and two-phase manufacturing release."""

import argparse
import json
from pathlib import Path

from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import ValidationError
from yaml import YAMLError

from astra_pcb.bom import check_bom
from astra_pcb.bom.importer import import_bom
from astra_pcb.bom.jlcsearch import JLCSearch
from astra_pcb.config import load_yaml, validate_document
from astra_pcb.engineering.power import PowerTree
from astra_pcb.kicad.verification import verify_design
from astra_pcb.models import CheckResult, CheckStatus, VerificationReport
from astra_pcb.models.engineering import Review
from astra_pcb.models.provenance import InputIdentity
from astra_pcb.release import GateConfig, evaluate
from astra_pcb.release.attestations import Attestation, TrustedSigner
from astra_pcb.release.coordinator import ReleaseProject, finalize_release, identify, release
from astra_pcb.simulation.workflow import SimulationJob, run_job
from astra_pcb.verification.environment import diagnose


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="astra-pcb")
    sub = parser.add_subparsers(dest="command", required=True)
    environment = sub.add_parser("environment")
    environment.add_argument("--probe-mcp", action="store_true")
    validate = sub.add_parser("validate")
    validate.add_argument("document", type=Path)
    validate.add_argument("--schema", type=Path, default=Path("schemas/design-spec.schema.json"))
    verify = sub.add_parser("verify")
    verify.add_argument("--report", type=Path)
    verify.add_argument("--gates", type=Path, default=Path("config/release-gates.yaml"))
    verify.add_argument("--identity", type=Path)
    verify.add_argument("--root", type=Path, default=Path.cwd())
    verify.add_argument("--attestations", type=Path)
    verify.add_argument("--trusted-signers", type=Path)
    kicad = sub.add_parser("check-kicad")
    kicad.add_argument("--schematic", type=Path)
    kicad.add_argument("--board", type=Path)
    kicad.add_argument("--output", type=Path, required=True)
    kicad.add_argument("--parity", action="store_true")
    simulate = sub.add_parser("simulate")
    simulate.add_argument("job", type=Path)
    simulate.add_argument("--output", type=Path, required=True)
    bom = sub.add_parser("check-bom")
    bom.add_argument("document", type=Path)
    power = sub.add_parser("check-power")
    power.add_argument("document", type=Path)
    sourcing = sub.add_parser("source-part")
    sourcing.add_argument("lcsc")
    sourcing.add_argument("--expected-mpn")
    releasing = sub.add_parser("release")
    releasing.add_argument("--project", type=Path)
    releasing.add_argument("--root", type=Path, default=Path.cwd())
    releasing.add_argument("--gates", type=Path, default=Path("config/release-gates.yaml"))
    releasing.add_argument("--output", type=Path)
    releasing.add_argument("--reviews", type=Path)
    releasing.add_argument("--attestations", type=Path)
    releasing.add_argument("--trusted-signers", type=Path)
    releasing.add_argument("--identity-only", action="store_true")
    releasing.add_argument("--finalize", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "simulate":
            report = run_job(
                SimulationJob.model_validate(load_yaml(args.job)), args.job.parent, args.output
            )
        elif args.command == "check-bom":
            report = VerificationReport(results=check_bom(import_bom(args.document)))
        elif args.command == "check-power":
            report = PowerTree.model_validate(load_yaml(args.document)).audit()
        elif args.command == "source-part":
            _, check = JLCSearch().lookup(args.lcsc, expected_mpn=args.expected_mpn)
            report = VerificationReport(results=(check,))
        elif args.command == "environment":
            report = diagnose(probe_mcp=args.probe_mcp)
        elif args.command == "validate":
            validate_document(args.document, args.schema)
            report = VerificationReport(
                results=(
                    CheckResult(
                        check_id="spec.schema",
                        name="Schema validation",
                        status=CheckStatus.PASS,
                        message=(
                            "Structure and declared semantics valid; "
                            "engineering completeness not established"
                        ),
                    ),
                )
            )
        elif args.command == "check-kicad":
            report = verify_design(
                schematic=args.schematic, board=args.board, output=args.output, parity=args.parity
            )
        elif args.command == "verify":
            inputs = (
                VerificationReport.model_validate_json(args.report.read_text())
                if (args.report)
                else VerificationReport(results=())
            )
            identity = (
                InputIdentity.model_validate_json(args.identity.read_text())
                if (args.identity)
                else None
            )
            if identity:
                identity.verify(args.root)
            attestations = tuple(
                Attestation.model_validate(x)
                for x in (json.loads(args.attestations.read_text()) if args.attestations else [])
            )
            trusted = {
                k: TrustedSigner.model_validate(v)
                for k, v in (
                    json.loads(args.trusted_signers.read_text()) if args.trusted_signers else {}
                ).items()
            }
            report = evaluate(
                GateConfig.model_validate(load_yaml(args.gates)),
                inputs,
                expected_digest=identity.digest if identity else None,
                attestations=attestations,
                trusted=trusted,
            )
        else:
            if args.finalize and not args.output:
                raise ValueError("Finalization requires an existing candidate output directory")
            trusted = {
                k: TrustedSigner.model_validate(v)
                for k, v in (
                    json.loads(args.trusted_signers.read_text()) if args.trusted_signers else {}
                ).items()
            }
            attestations = tuple(
                Attestation.model_validate(a)
                for a in (json.loads(args.attestations.read_text()) if args.attestations else [])
            )
            if args.finalize:
                report = finalize_release(args.root, args.output, attestations, trusted)
            else:
                if not args.project:
                    raise ValueError("Release requires --project; no design is implicitly released")
                project = ReleaseProject.model_validate(load_yaml(args.project))
                identity = identify(args.root, project, args.project, args.gates)
                if args.identity_only:
                    print(identity.model_dump_json(indent=2))
                    return 0
                if not args.output:
                    raise ValueError("Release preparation requires a fresh --output directory")
                reviews = tuple(
                    Review.model_validate(r)
                    for r in (json.loads(args.reviews.read_text()) if args.reviews else [])
                )
                report = release(
                    args.root,
                    project,
                    identity,
                    GateConfig.model_validate(load_yaml(args.gates)),
                    reviews,
                    attestations,
                    trusted,
                    args.output,
                )
        print(report.model_dump_json(indent=2))
        return report.exit_code
    except (OSError, ValueError, ValidationError, SchemaError, YAMLError) as exc:
        print(json.dumps({"status": "ERROR", "message": str(exc)}))
        return 1
