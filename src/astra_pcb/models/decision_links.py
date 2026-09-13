"""Resolve decision citations and calculation links against a frozen local corpus."""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from astra_pcb.datasheets.registry import Registry
from astra_pcb.models import CheckResult, VerificationReport
from astra_pcb.models.engineering import Decision
from astra_pcb.models.provenance import file_digest


def validate_links(decision: Decision, root: Path, registry: Registry) -> VerificationReport:
    results = []
    for index, citation in enumerate(decision.evidence):
        try:
            matches = [
                d
                for d in registry.documents.values()
                if (
                    citation.source_location in {d.local_path, d.canonical_url}
                    and citation.document == d.title
                    and citation.revision == d.revision
                    and citation.manufacturer == d.manufacturer
                )
            ]
            if len(matches) != 1 or not citation.sha256:
                raise ValueError("Missing/ambiguous registered citation or content digest")
            document = matches[0]
            registry.validate(document)
            if citation.sha256 != document.sha256:
                raise ValueError("Decision cites a changed document")
            result = CheckResult(
                check_id=f"decision.{decision.id}.citation.{index}",
                name="Decision citation",
                status="PASS",
                message="Registered document and locator match",
                evidence=(citation.model_dump_json(),),
            )
        except (OSError, ValueError) as exc:
            result = CheckResult(
                check_id=f"decision.{decision.id}.citation.{index}",
                name="Decision citation",
                status="ERROR",
                message=str(exc),
            )
        results.append(result)
    for index, text in enumerate(decision.calculations):
        links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
        for offset, link in enumerate(links):
            try:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or parsed.query:
                    raise ValueError("Calculation links must reference local frozen artifacts")
                relative = Path(unquote(parsed.path))
                path = (root / relative).resolve()
                if relative.is_absolute() or not path.is_relative_to(root.resolve()):
                    raise ValueError("Calculation link escapes project")
                if not path.is_file():
                    raise ValueError("Calculation artifact missing")
                result = CheckResult(
                    check_id=f"decision.{decision.id}.calculation.{index}.{offset}",
                    name="Decision calculation link",
                    status="PASS",
                    message=str(relative),
                    evidence=(file_digest(path),),
                )
            except (OSError, ValueError) as exc:
                result = CheckResult(
                    check_id=f"decision.{decision.id}.calculation.{index}.{offset}",
                    name="Decision calculation link",
                    status="ERROR",
                    message=str(exc),
                )
            results.append(result)
    return VerificationReport(results=tuple(results))
