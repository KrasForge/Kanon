"""MCP 2025-06-18 stdio server exposing no source paths, shell or mutation capabilities."""

import json
import subprocess
import sys

from astra_pcb.models import CheckResult, VerificationReport
from astra_pcb.verifier.catalog import CHECKS

PROTOCOL = "2025-06-18"


def check(name, arguments):
    if name not in CHECKS:
        raise ValueError("Unimplemented tool; no success can be returned")
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "astra_pcb.verifier.worker"],
            input=json.dumps({"name": name, "arguments": arguments}),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode or len(result.stdout) > 8 * 1024 * 1024:
            raise ValueError("Worker failed or output limit exceeded")
        report = VerificationReport.model_validate_json(result.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        report = VerificationReport(
            results=(
                CheckResult(
                    check_id="verifier.error",
                    name="Verifier execution",
                    status="ERROR",
                    message=type(exc).__name__,
                ),
            )
        )
    return {
        "content": [{"type": "text", "text": report.model_dump_json()}],
        "structuredContent": report.model_dump(mode="json"),
        "isError": any(c.status == "ERROR" for c in report.results),
    }


def main():
    initialized = False
    for line in iter(lambda: sys.stdin.readline(1024 * 1024 + 1), ""):
        message = None
        try:
            if len(line) > 1024 * 1024:
                return 1
            message = json.loads(line)
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                raise ValueError("Invalid JSON-RPC")
            method = message.get("method")
            params = message.get("params", {})
            if "id" not in message:
                if method == "notifications/initialized":
                    continue
                continue  # Notifications receive no response, including unknown notifications.
            if method == "initialize":
                if params.get("protocolVersion") != PROTOCOL:
                    raise ValueError("Unsupported MCP version")
                initialized = True
                result = {
                    "protocolVersion": PROTOCOL,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "pcb-verifier", "version": "0.1.0"},
                }
            elif not initialized:
                raise ValueError("Initialize first")
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": name,
                            "description": description,
                            "inputSchema": model.model_json_schema(),
                            "annotations": {
                                "readOnlyHint": True,
                                "destructiveHint": False,
                                "openWorldHint": False,
                            },
                        }
                        for name, (model, _, description) in CHECKS.items()
                    ]
                }
            elif method == "tools/call":
                result = check(params["name"], params.get("arguments", {}))
            else:
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": message["id"],
                            "error": {"code": -32601, "message": "Method unavailable"},
                        }
                    ),
                    flush=True,
                )
                continue
            reply = {"jsonrpc": "2.0", "id": message["id"], "result": result}
        except Exception as exc:
            reply = {
                "jsonrpc": "2.0",
                "id": message.get("id") if isinstance(message, dict) else None,
                "error": {"code": -32602, "message": type(exc).__name__ + ": " + str(exc)[:300]},
            }
        print(json.dumps(reply), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
