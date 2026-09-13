"""Read-only JLCSearch mirror lookup; no orders, substitutions or freshness claims."""

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from astra_pcb.bom.sourcing import SourcingRecord
from astra_pcb.models import CheckResult, CheckStatus


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "astra-pcb/0.1"})
    with build_opener(NoRedirect).open(request, timeout=20) as response:
        data = response.read(1024 * 1024 + 1)
        if len(data) > 1024 * 1024:
            raise ValueError("Supplier response exceeds 1 MiB")
        if response.headers.get_content_type() != "application/json":
            raise ValueError("Supplier response is not JSON")
    result = json.loads(data)
    if not isinstance(result, dict):
        raise ValueError("Supplier response must be an object")
    return result


class JLCSearch:
    """Replaceable public mirror. Upstream does not supply manufacturer or stock timestamp.

    Prices are retained verbatim as unqualified quote evidence: the endpoint omits currency.
    Electrical attributes are deliberately excluded; manufacturer evidence must supply those.
    """

    def __init__(
        self,
        base_url: str = "https://jlcsearch.tscircuit.com",
        *,
        fetch: Callable[[str], dict] = fetch_json,
    ):
        parsed = urlsplit(base_url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError("Supplier origin must be HTTPS without credentials/path/query")
        self.base_url, self.fetch = base_url.rstrip("/"), fetch

    def lookup(
        self, lcsc: str, *, expected_mpn: str | None = None
    ) -> tuple[SourcingRecord | None, CheckResult]:
        if not re.fullmatch(r"C[1-9]\d*", lcsc):
            raise ValueError("Canonical C-prefixed LCSC number required")
        url = self.base_url + "/components/list.json?" + urlencode({"search": lcsc, "limit": 100})
        try:
            data = self.fetch(url)
            rows = data.get("components")
            if not isinstance(rows, list):
                raise ValueError("Missing components array")
            matches = [
                row
                for row in rows
                if isinstance(row, dict)
                and type(row.get("lcsc")) is int
                and row["lcsc"] == int(lcsc[1:])
            ]
            if len(matches) != 1:
                raise ValueError("Supplier part absent or ambiguous")
            row = matches[0]
            if expected_mpn is not None and row.get("mfr") != expected_mpn:
                raise ValueError("MPN mismatch; substitution refused")
            if type(row.get("is_basic")) is not bool:
                raise ValueError("Missing/invalid Basic classification")
            if row.get("stock") is not None and type(row["stock"]) is not int:
                raise ValueError("Invalid inventory type")
            record = SourcingRecord(
                mpn=row["mfr"],
                manufacturer=None,
                supplier="JLCPCB",
                supplier_part_number=lcsc,
                package=row["package"],
                stock=row.get("stock"),
                assembly_classification="Basic" if row["is_basic"] else "Extended",
                observed_at=datetime.now(UTC),
                source_url=url,
                source_kind="third-party-mirror",
                raw_price_tiers=str(row.get("price", "")),
            )
            return record, CheckResult(
                check_id="sourcing.lookup",
                name="JLCSearch lookup",
                status=CheckStatus.WARN,
                message=(
                    "Mirror record retrieved; manufacturer, stock age and price currency unknown"
                ),
                evidence=(record.model_dump_json(),),
                source="JLCSearch / jlcparts mirror",
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return None, CheckResult(
                check_id="sourcing.lookup",
                name="JLCSearch lookup",
                status=CheckStatus.ERROR,
                message=f"Lookup failed: {type(exc).__name__}",
                remediation="Check connectivity and the current supplier API response contract",
            )
