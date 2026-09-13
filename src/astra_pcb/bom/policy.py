"""Explicit fitted/mechanical exclusions, canonical manufacturers and ordering suffix rules."""

from pydantic import Field, model_validator

from astra_pcb.bom import BOMItem, check_bom
from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, StrictModel, VerificationReport


class OrderingRule(StrictModel):
    manufacturer: str
    base_mpn: str = Field(min_length=1)
    allowed_suffixes: tuple[str, ...] = Field(min_length=1)
    evidence: DatasheetEvidence


class BOMPolicy(StrictModel):
    manufacturer_aliases: dict[str, str] = {}
    unfitted_references: frozenset[str] = frozenset()
    mechanical_references: frozenset[str] = frozenset()
    exclusion_evidence: dict[str, str] = {}
    ordering_rules: tuple[OrderingRule, ...] = ()

    @model_validator(mode="after")
    def exclusions(self):
        if (self.unfitted_references | self.mechanical_references) - self.exclusion_evidence.keys():
            raise ValueError("Every excluded reference requires explicit policy evidence")
        aliases = {k.strip().casefold(): v.strip() for k, v in self.manufacturer_aliases.items()}
        if len(aliases) != len(self.manufacturer_aliases) or any(
            not k or not v for k, v in aliases.items()
        ):
            raise ValueError("Ambiguous or empty manufacturer aliases")
        if any(v.casefold() in aliases and aliases[v.casefold()] != v for v in aliases.values()):
            raise ValueError("Manufacturer alias chains/cycles are not allowed")
        return self


def audit_bom(items: list[BOMItem], policy: BOMPolicy) -> VerificationReport:
    aliases = {k.strip().casefold(): v.strip() for k, v in policy.manufacturer_aliases.items()}
    references = {i.reference for i in items}
    excluded = policy.unfitted_references | policy.mechanical_references
    failures = []
    if len(references) != len(items):
        failures.append("Duplicate references, including excluded items")
    if excluded - references:
        failures.append("Exclusion policy references absent BOM objects")
    normalized = []
    suppliers = {}
    for item in items:
        manufacturer = (item.manufacturer or "").strip()
        manufacturer = aliases.get(manufacturer.casefold(), manufacturer)
        row = BOMItem.model_validate(
            {
                **item.model_dump(),
                "manufacturer": manufacturer or None,
                "mpn": item.mpn.strip() if item.mpn else None,
                "value": item.value.strip(),
                "package": item.package.strip(),
            }
        )
        if row.reference in excluded:
            continue
        normalized.append(row)
        if row.supplier and row.supplier_part_number:
            key = (row.supplier.strip().casefold(), row.supplier_part_number.strip())
            identity = (manufacturer.casefold(), row.mpn)
            if key in suppliers and suppliers[key] != identity:
                failures.append(f"Supplier identity conflict at {row.reference}")
            suppliers[key] = identity
        for rule in policy.ordering_rules:
            if manufacturer.casefold() == rule.manufacturer.casefold() and (
                row.mpn or ""
            ).startswith(rule.base_mpn):
                if row.mpn not in {rule.base_mpn + suffix for suffix in rule.allowed_suffixes}:
                    failures.append(
                        f"Missing/ambiguous ordering suffix at {row.reference}: {row.mpn}"
                    )
    checks = list(check_bom(normalized))
    # An explicitly empty fitted electrical inventory does not validate a release BOM.
    checks.append(
        CheckResult(
            check_id="bom.policy",
            name="BOM normalization and exclusions",
            status="FAIL" if failures else "PASS",
            message="; ".join(failures) or "Declared policy satisfied",
            affected_objects=tuple(sorted(references)),
            evidence=(policy.model_dump_json(), *(i.model_dump_json() for i in normalized)),
        )
    )
    return VerificationReport(results=tuple(checks))
