"""Check a JSON array of canonical BOM rows; no live supplier lookups."""

import argparse
import json
from pathlib import Path

from astra_pcb.bom import BOMItem, check_bom
from astra_pcb.models import CheckResult, CheckStatus, VerificationReport


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bom", type=Path, help="JSON array of per-reference BOM rows")
    args = parser.parse_args()
    try:
        rows = json.loads(args.bom.read_text())
        if not isinstance(rows, list):
            raise ValueError("BOM must be a JSON array")
        report = VerificationReport(
            results=check_bom([BOMItem.model_validate(row) for row in rows])
        )
    except (OSError, ValueError) as exc:
        report = VerificationReport(
            results=(
                CheckResult(
                    check_id="bom.input",
                    name="BOM input",
                    status=CheckStatus.ERROR,
                    message=str(exc),
                    source=str(args.bom),
                ),
            )
        )
    print(report.model_dump_json(indent=2))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
