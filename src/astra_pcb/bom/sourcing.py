"""Optional supplier-MCP lookup and transparent, timestamped sourcing risk."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.kicad.mcp import Transport
from astra_pcb.models import CheckResult, CheckStatus, StrictModel


class SourcingRecord(StrictModel):
    mpn: str = Field(min_length=1)
    manufacturer: str | None = Field(default=None, min_length=1)
    supplier: Literal["LCSC", "JLCPCB"]
    supplier_part_number: str = Field(pattern=r"^C\d+$")
    package: str
    stock: int | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    price_quantity: int = Field(default=1, ge=1)
    assembly_classification: Literal["Basic", "Extended", "unknown"] = "unknown"
    lifecycle: Literal["active", "nrnd", "obsolete", "unknown"] = "unknown"
    independent_sources: int | None = Field(default=None, ge=0)
    observed_at: datetime
    source_url: str = Field(min_length=1)
    source_kind: Literal["supplier", "third-party-mirror"] = "supplier"
    stock_updated_at: datetime | None = None
    raw_price_tiers: str | None = None

    @model_validator(mode="after")
    def metadata(self):
        if self.observed_at.tzinfo is None or (
            self.stock_updated_at is not None and self.stock_updated_at.tzinfo is None
        ):
            raise ValueError("Stock timestamp must have timezone")
        if self.unit_cost is not None and not self.currency:
            raise ValueError("Price requires currency")
        return self


class SupplierAdapter:
    """Consumes normalized JSON from an explicitly configured, audited supplier MCP tool."""

    def __init__(self, transport: Transport | None = None, tool: str | None = None):
        self.transport, self.tool = transport, tool

    def lookup(self, manufacturer: str, mpn: str) -> tuple[SourcingRecord | None, CheckResult]:
        if self.transport is None or not self.tool:
            return None, CheckResult(
                check_id="sourcing.lookup",
                name="Supplier lookup",
                status=CheckStatus.SKIP,
                message="Supplier MCP is unconfigured; no live data available",
            )
        try:
            reply = self.transport.request(
                "tools/call",
                {"name": self.tool, "arguments": {"manufacturer": manufacturer, "mpn": mpn}},
            )
            if reply.get("isError") or "structuredContent" not in reply:
                raise ValueError("Supplier lookup failed or lacks normalized structured content")
            record = SourcingRecord.model_validate(reply["structuredContent"])
            if (
                record.mpn != mpn
                or (record.manufacturer or "").casefold() != manufacturer.casefold()
            ):
                raise ValueError("Supplier returned a different part; no substitution permitted")
            return record, CheckResult(
                check_id="sourcing.lookup",
                name="Supplier lookup",
                status=CheckStatus.PASS,
                message="Retrieved supplier record; freshness checked separately",
                evidence=(record.source_url, record.model_dump_json()),
            )
        except (OSError, ValueError, TimeoutError, RuntimeError) as exc:
            return None, CheckResult(
                check_id="sourcing.lookup",
                name="Supplier lookup",
                status=CheckStatus.ERROR,
                message=type(exc).__name__,
            )


def sourcing_risk(
    record: SourcingRecord,
    needed: int,
    *,
    now: datetime | None = None,
    max_age: timedelta = timedelta(hours=24),
) -> CheckResult:
    if needed <= 0 or max_age.total_seconds() <= 0:
        raise ValueError("Positive quantity and freshness window required")
    now = now or datetime.now(UTC)
    risks = []
    if now.tzinfo is None:
        raise ValueError("Current time must have timezone")
    if record.manufacturer is None:
        risks.append("manufacturer unknown")
    if record.source_kind == "third-party-mirror":
        risks.append("third-party mirror; supplier confirmation required")
        if record.stock_updated_at is None:
            risks.append("stock source age unknown")
        elif not timedelta(0) <= now - record.stock_updated_at <= max_age:
            risks.append("stale/future source stock timestamp")
    if record.lifecycle != "active":
        risks.append(f"lifecycle {record.lifecycle}")
    if record.stock is None:
        risks.append("stock unknown")
    elif record.stock < needed:
        risks.append("insufficient stock")
    if not timedelta(0) <= now - record.observed_at <= max_age:
        risks.append("stale/future observation")
    if record.independent_sources is None or record.independent_sources < 2:
        risks.append("sole-source or unassessed source diversity")
    return CheckResult(
        check_id="bom.sourcing-risk",
        name="Sourcing risk",
        status=CheckStatus.WARN if risks else CheckStatus.PASS,
        message="; ".join(risks)
        or "Declared lifecycle, availability and source diversity acceptable",
        evidence=(record.model_dump_json(),),
        affected_objects=(record.mpn,),
    )
