"""Native 3D model inventory, separate from STEP file envelope integrity."""

from pathlib import Path

from astra_pcb.kicad.snapshot import nodes, parse_sexpr
from astra_pcb.models import CheckResult, VerificationReport
from astra_pcb.models.provenance import file_digest


def model_inventory(board: Path, *, exemptions: dict[str, str] | None = None) -> VerificationReport:
    exemptions = exemptions or {}
    checks = []
    references = set()
    for footprint in nodes(parse_sexpr(board.read_text()), "footprint"):
        reference = next(
            (p[2] for p in nodes(footprint, "property") if len(p) >= 3 and p[1] == "Reference"),
            None,
        )
        if not reference or reference in references:
            raise ValueError("Missing/duplicate native footprint reference")
        references.add(reference)
        models = list(nodes(footprint, "model"))
        evidence = []
        missing = []
        for model in models:
            name = model[1] if len(model) > 1 else ""
            path = Path(name.replace("${KIPRJMOD}", str(board.parent.resolve())))
            if not path.is_absolute():
                path = board.parent / path
            if (
                not name
                or "$" in str(path)
                or not path.is_file()
                or path.suffix.lower() not in {".step", ".stp", ".igs", ".iges"}
                or any(h == ["hide", "yes"] for h in nodes(model, "hide"))
            ):
                missing.append(name or "malformed model reference")
            else:
                evidence.append(str(path) + " sha256:" + file_digest(path))
        exemption = exemptions.get(reference)
        if exemption is not None and not exemption.strip():
            raise ValueError("Model exemption needs explicit review evidence")
        status = "FAIL" if missing or (not models and not exemption) else "PASS"
        checks.append(
            CheckResult(
                check_id="mechanical.models." + reference,
                name="Native component model coverage",
                status=status,
                message="Missing model geometry: " + repr(missing)
                if missing
                else "No model assigned"
                if not models and not exemption
                else "Explicit non-modelled component exemption"
                if exemption
                else "Assigned model files exist; dimensional accuracy still requires review",
                evidence=tuple(evidence) + ((exemption,) if exemption else ()),
                affected_objects=(reference,),
            )
        )
    if set(exemptions) - references:
        raise ValueError("Model exemption references absent source object")
    if not references:
        checks.append(
            CheckResult(
                check_id="mechanical.models.empty",
                name="Native model inventory",
                status="SKIP",
                message="No populated native footprints",
            )
        )
    return VerificationReport(results=tuple(checks), input_digest=file_digest(board))
