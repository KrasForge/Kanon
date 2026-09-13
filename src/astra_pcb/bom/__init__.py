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


def check_board_bom(items: list[BOMItem], board_text: str) -> CheckResult:
    """Compare populated native footprints with per-reference BOM value and footprint ID."""
    from astra_pcb.kicad.snapshot import nodes, parse_sexpr

    expected = {}
    for footprint in nodes(parse_sexpr(board_text), "footprint"):
        fields = [x for x in footprint if isinstance(x, list)]
        attributes = next((f[1:] for f in fields if f and f[0] == "attr"), [])
        dnp = any(f == ["dnp", "yes"] for f in fields)
        if "exclude_from_bom" in attributes or dnp:
            continue
        properties = {f[1]: f[2] for f in fields if len(f) > 2 and f[0] == "property"}
        reference = properties.get("Reference")
        if not reference or reference in expected:
            return CheckResult(
                check_id="bom.parity",
                name="Native BOM parity",
                status=CheckStatus.FAIL,
                message="Missing/duplicate native footprint reference",
            )
        expected[reference] = (properties.get("Value"), footprint[1])
    actual = {i.reference: (i.value, i.package) for i in items}
    passed = bool(expected) and expected == actual and all(i.quantity == 1 for i in items)
    return CheckResult(
        check_id="bom.parity",
        name="Native BOM parity",
        status=CheckStatus.PASS if passed else CheckStatus.FAIL,
        message="Native populated footprint/value inventory matches BOM"
        if passed
        else "Empty design or populated reference/value/footprint/quantity mismatch",
        evidence=(str(expected), str(actual)),
        source="native KiCad footprint inventory",
    )
