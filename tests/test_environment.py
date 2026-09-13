"""Real local HTTP handshake and version/error diagnostic fixtures."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from astra_pcb.verification.environment import PROTOCOL, diagnose, probe_endpoint
from astra_pcb.verification.process import ProcessResult


@pytest.fixture
def mcp_endpoint():
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append(data)
            if data["method"] == "initialize":
                payload = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "protocolVersion": PROTOCOL,
                            "capabilities": {},
                            "serverInfo": {"name": "fixture", "version": "1"},
                        },
                    }
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                assert self.headers["MCP-Protocol-Version"] == PROTOCOL
                self.send_response(202)
                self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/mcp", received
    server.shutdown()
    server.server_close()
    thread.join()


def test_real_local_handshake(mcp_endpoint):
    endpoint, received = mcp_endpoint
    assert "Initialized MCP" in probe_endpoint(endpoint)
    assert [x["method"] for x in received] == ["initialize", "notifications/initialized"]


def test_probe_errors_do_not_leak_credentials(monkeypatch):
    monkeypatch.setenv("KICAD_MCP_URL", "invalid://secret.example/secret")
    monkeypatch.setenv("KICAD_MCP_TOKEN", "do-not-print")
    report = diagnose(probe_mcp=True)
    result = next(x for x in report.results if x.check_id == "mcp.kicad")
    assert result.status == "ERROR"
    assert (
        "secret" not in report.model_dump_json() and "do-not-print" not in report.model_dump_json()
    )


def test_unsupported_kicad_version(monkeypatch):
    monkeypatch.setattr("astra_pcb.verification.environment.shutil.which", lambda _: "/bin/tool")
    monkeypatch.setattr(
        "astra_pcb.verification.environment.run",
        lambda *a, **k: ProcessResult(command=("fixture",), exit_code=0, stdout="9.0.0"),
    )
    report = diagnose()
    assert next(x for x in report.results if x.check_id == "kicad").status == "FAIL"


@pytest.mark.parametrize(
    "url", ["file:///tmp/test", "http://remote.example/mcp", "https://user:secret@example.com/mcp"]
)
def test_disallowed_endpoint(url):
    with pytest.raises(ValueError):
        probe_endpoint(url)
