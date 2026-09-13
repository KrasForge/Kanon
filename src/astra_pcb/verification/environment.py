"""Version-qualified discovery and opt-in MCP initialization diagnostics."""

import json
import os
import re
import shutil
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from astra_pcb.models import CheckResult, CheckStatus, VerificationReport
from astra_pcb.verification.process import run

PROTOCOL = "2025-06-18"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("MCP diagnostic redirects are not permitted")


urlopen = build_opener(NoRedirect()).open


def probe_endpoint(url: str, token: str | None = None) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        raise ValueError("Expected HTTP(S) endpoint without embedded credentials")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Remote MCP endpoints require HTTPS")
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL,
            "capabilities": {},
            "clientInfo": {"name": "astra-pcb-diagnostics", "version": "0.1.0"},
        },
    }
    with urlopen(
        Request(url, data=json.dumps(request).encode(), headers=headers), timeout=5
    ) as reply:
        content_type = reply.headers.get("Content-Type", "")
        session = reply.headers.get("Mcp-Session-Id")
        if "text/event-stream" in content_type:
            message = None
            size = 0
            for line in reply:
                size += len(line)
                if size > 1024 * 1024:
                    raise ValueError("MCP initialization response too large")
                if line.startswith(b"data:"):
                    candidate = json.loads(line[5:])
                    if candidate.get("id") == 1:
                        message = candidate
                        break
        else:
            payload = reply.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                raise ValueError("MCP initialization response too large")
            message = json.loads(payload)
    if not isinstance(message, dict) or message.get("id") != 1 or message.get("jsonrpc") != "2.0":
        raise ValueError("Invalid initialization response identity")
    result = message.get("result", {})
    if (
        not isinstance(result, dict)
        or result.get("protocolVersion") != PROTOCOL
        or not isinstance(result.get("capabilities"), dict)
        or not isinstance(result.get("serverInfo"), dict)
    ):
        raise ValueError("Unsupported protocol or malformed server capabilities")
    headers["MCP-Protocol-Version"] = PROTOCOL
    if session:
        headers["Mcp-Session-Id"] = session
    notification = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode()
    with urlopen(Request(url, data=notification, headers=headers), timeout=5) as reply:
        if reply.status not in {200, 202, 204}:
            raise ValueError("Server rejected initialization notification")
    if session:
        try:
            with urlopen(Request(url, method="DELETE", headers=headers), timeout=5):
                pass
        except HTTPError as exc:
            if exc.code != 405:
                raise
    return f"Initialized MCP {PROTOCOL}; editing capabilities not qualified"


def diagnose(*, probe_mcp: bool = False) -> VerificationReport:
    results = [
        CheckResult(
            check_id="python",
            name="Python",
            status=(CheckStatus.PASS if sys.version_info >= (3, 12) else CheckStatus.FAIL),
            message=sys.version.split()[0],
        )
    ]
    tools = [
        ("git", ["git"], "--version", True, 2, None),
        ("kicad", ["kicad-cli"], "version", False, 10, 10),
        ("ngspice", ["ngspice"], "--version", False, 42, None),
        ("freecad", ["FreeCADCmd", "freecadcmd"], "--version", False, 1, None),
    ]
    for name, candidates, flag, required, minimum, maximum in tools:
        executable = next((p for p in candidates if shutil.which(p)), None)
        if not executable:
            results.append(
                CheckResult(
                    check_id=name,
                    name=name,
                    status=CheckStatus.ERROR if required else CheckStatus.SKIP,
                    message="Executable not installed",
                    source=candidates[0],
                )
            )
            continue
        result = run([executable, flag], timeout=10)
        version_text = result.stdout + result.stderr
        match = re.search(r"(?:ngspice[-\s]+)?(\d+)(?:\.\d+)*", version_text)
        major = int(match[1]) if match else None
        status = (
            CheckStatus.ERROR
            if result.exit_code != 0 or result.error
            else (
                CheckStatus.PASS
                if major is not None and major >= minimum and (maximum is None or major <= maximum)
                else CheckStatus.FAIL
            )
        )
        results.append(
            CheckResult(
                check_id=name,
                name=name,
                status=status,
                message=result.error or version_text or "No version output",
                source=executable,
            )
        )
    for name in ["KICAD", "PARTS", "FREECAD", "DATASHEETS"]:
        url = os.getenv(f"{name}_MCP_URL")
        status = CheckStatus.SKIP
        message = "Configured; connectivity untested" if url else "Unconfigured"
        if url and probe_mcp:
            try:
                message = probe_endpoint(url, os.getenv(f"{name}_MCP_TOKEN"))
                status = CheckStatus.PASS
            except (OSError, ValueError, URLError) as exc:
                # Do not echo URLs, response bodies or tokens into diagnostics.
                status = CheckStatus.ERROR
                message = f"MCP initialization failed ({type(exc).__name__})"
        results.append(
            CheckResult(
                check_id=f"mcp.{name.lower()}", name=f"{name} MCP", status=status, message=message
            )
        )
    return VerificationReport(results=tuple(results))
