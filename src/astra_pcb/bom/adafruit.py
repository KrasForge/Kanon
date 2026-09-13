"""Credential-free exact product lookup from Adafruit's public catalog API."""

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime

from astra_pcb.bom.jlcsearch import fetch_json
from astra_pcb.bom.sourcing import SourcingRecord
from astra_pcb.models import CheckResult, CheckStatus


class Adafruit:
    """Supplier product IDs are distinct from MPNs; missing MPNs are never invented.

    API prices omit currency and inventory can be a count or availability text. Retain
    unqualified values, never turn 'in stock' into an invented purchasable quantity.
    """

    def __init__(self, *, fetch: Callable[[str], dict] = fetch_json):
        self.fetch = fetch

    def lookup(
        self, product_id: str, *, expected_mpn: str | None = None
    ) -> tuple[SourcingRecord | None, CheckResult]:
        if not re.fullmatch(r"[1-9]\d*", product_id):
            raise ValueError("Canonical positive Adafruit product ID required")
        url = f"https://www.adafruit.com/api/products/{product_id}"
        try:
            row = self.fetch(url)
            if str(row.get("product_id")) != product_id:
                raise ValueError("Supplier returned a different product")
            mpn = row.get("product_mpn")
            if not isinstance(mpn, str) or not mpn.strip():
                raise ValueError("Manufacturer part number is unavailable")
            if expected_mpn is not None and mpn != expected_mpn:
                raise ValueError("MPN mismatch; substitution refused")
            stock = row.get("product_stock")
            if type(stock) is int and stock >= 0:
                quantity = stock
            elif isinstance(stock, str) and re.fullmatch(r"\d+", stock):
                quantity = int(stock)
            elif stock is None or stock in {"in stock", "out of stock"}:
                quantity = None
            else:
                raise ValueError("Unrecognized supplier inventory format")
            manufacturer = row.get("product_manufacturer") or None
            record = SourcingRecord(
                mpn=mpn,
                manufacturer=manufacturer,
                supplier="Adafruit",
                supplier_part_number=product_id,
                package=None,
                stock=quantity,
                availability=str(stock) if stock is not None else None,
                observed_at=datetime.now(UTC),
                source_url=url,
                source_kind="supplier",
                raw_price_tiers=json.dumps(
                    {
                        "product_price": row.get("product_price"),
                        "discount_pricing": row.get("discount_pricing"),
                    },
                    sort_keys=True,
                ),
                raw_lifecycle=str(row.get("discontinue_status", "unknown")),
            )
            return record, CheckResult(
                check_id="sourcing.lookup",
                name="Adafruit public catalog lookup",
                status=CheckStatus.WARN,
                message="Supplier record retrieved without credentials; package, lifecycle, "
                "price currency and inventory update age are unqualified",
                evidence=(record.model_dump_json(),),
                source="Adafruit public product API",
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return None, CheckResult(
                check_id="sourcing.lookup",
                name="Adafruit public catalog lookup",
                status=CheckStatus.ERROR,
                message=f"Lookup failed: {type(exc).__name__}",
                remediation="Check connectivity, exact product/MPN and supplier response contract",
            )
