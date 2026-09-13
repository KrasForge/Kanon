"""Canonical per-reference BOM rows and offline integrity checks."""

import re
from decimal import Decimal

from pydantic import Field

from astra_pcb.models import CheckResult, CheckStatus, StrictModel


class BOMItem(StrictModel):
    reference: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    value: str
    manufacturer: str | None = None
    mpn: str | None = None
    supplier: str | None = None
    supplier_part_number: str | None = None
    package: str
    lifecycle: str | None = None
    stock: int | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    assembly_classification: str | None = None
    alternates: tuple[str, ...] = ()
    notes: str = ""


def check_bom(items: list[BOMItem]) -> tuple[CheckResult, ...]:
    problems = []
    refs = set()
    parts = {}
    for item in items:
        if item.reference in refs:
            problems.append(f"Duplicate reference {item.reference}")
        refs.add(item.reference)
        if not item.mpn or item.mpn.strip().lower() in {"", "tbd", "unknown", "n/a"}:
            problems.append(f"Missing/ambiguous MPN: {item.reference}")
        elif re.search(r"\s+(?:or|/)\s+|[;,]", item.mpn, flags=re.IGNORECASE):
            problems.append(f"Ambiguous MPN alternatives: {item.reference}")
        else:
            key = ((item.manufacturer or "").strip().casefold(), item.mpn.strip())
            metadata = (item.value.strip(), item.package.strip())
            if key in parts and parts[key] != metadata:
                problems.append(f"Inconsistent value/package for {item.mpn}")
            parts[key] = metadata
    return (
        CheckResult(
            check_id="bom.integrity",
            name="BOM integrity",
            status=CheckStatus.FAIL
            if problems
            else CheckStatus.PASS
            if items
            else CheckStatus.SKIP,
            message="; ".join(problems) if problems else "BOM consistent" if items else "Empty BOM",
            source="canonical BOM",
        ),
    )
