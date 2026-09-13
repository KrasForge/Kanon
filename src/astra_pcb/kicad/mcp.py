"""Audited designer tool mapping and a separate snapshot-only reviewer surface."""

import json
import queue
import subprocess
import threading
from typing import Literal, Protocol

from pydantic import Field, model_validator

from astra_pcb.kicad.snapshot import Snapshot
from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import Digest, canonical_digest
from astra_pcb.verification.environment import PROTOCOL


class ToolMapping(StrictModel):
    operation: str = Field(min_length=1)
    remote_tool: str = Field(min_length=1)
    access: Literal["READ", "WRITE"]


class MCPProfile(StrictModel):
    command: tuple[str, ...] = Field(min_length=1)
    tools: tuple[ToolMapping, ...]
    inventory_digest: Digest | None = None

    @model_validator(mode="after")
    def unique_mapping(self):
        for names in ([t.operation for t in self.tools], [t.remote_tool for t in self.tools]):
            if len(names) != len(set(names)):
                raise ValueError("Ambiguous MCP tool mapping")
        return self


class Transport(Protocol):
    def request(self, method: str, params: dict) -> dict: ...


class StdioTransport:
    """Small bounded MCP stdio transport; caller must audit the server command."""

    def __init__(self, command: tuple[str, ...], timeout: float = 30):
        self.timeout = timeout
        self._messages = queue.Queue(maxsize=256)
        self._counter = 0
        self._process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()
        try:
            reply = self.request(
                "initialize",
                {
                    "protocolVersion": PROTOCOL,
                    "capabilities": {},
                    "clientInfo": {"name": "astra-pcb-designer", "version": "0.1.0"},
                },
            )
            if reply.get("protocolVersion") != PROTOCOL:
                raise ValueError("Unsupported MCP protocol")
            self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            self.close()
            raise

    def _read(self):
        while True:
            line = self._process.stdout.readline(1024 * 1024 + 1)
            if not line:
                break
            if len(line) > 1024 * 1024:
                break
            try:
                self._messages.put_nowait(json.loads(line))
            except (ValueError, queue.Full):
                break
        try:
            self._messages.put_nowait(None)
        except queue.Full:
            pass

    def _send(self, message: dict) -> None:
        self._process.stdin.write(json.dumps(message) + "\n")
        self._process.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        self._counter += 1
        request_id = self._counter
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        # Notifications are rejected rather than risking an unbounded notification stream.
        try:
            message = self._messages.get(timeout=self.timeout)
        except queue.Empty as exc:
            self.close()
            raise TimeoutError("MCP response timed out") from exc
        if (
            not isinstance(message, dict)
            or message.get("id") != request_id
            or (message.get("jsonrpc") != "2.0" or "error" in message)
        ):
            raise ValueError("Invalid, unsolicited or failed MCP response")
        if not isinstance(message.get("result"), dict):
            raise ValueError("MCP result must be an object")
        return message["result"]

    def close(self):
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)
        self._process.stdin.close()
        self._process.stdout.close()
        self._reader.join(timeout=2)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DesignerTools:
    def __init__(self, profile: MCPProfile, transport: Transport):
        self._mapping = {t.operation: t for t in profile.tools}
        self._transport = transport
        listing = transport.request("tools/list", {})
        available = {t["name"] for t in listing.get("tools", [])}
        selected = {t.remote_tool for t in profile.tools}
        if profile.inventory_digest is not None:
            inventory = sorted(listing.get("tools", []), key=lambda tool: tool["name"])
            if canonical_digest({"tools": inventory}) != profile.inventory_digest:
                raise ValueError("Server tool inventory changed; qualification required")
            if not selected <= available:
                raise ValueError("Selected tools unavailable")
        elif available != selected:
            raise ValueError("Server tools differ from explicitly audited profile")

    def call(self, operation: str, arguments: dict, *, allow_write: bool = False) -> dict:
        mapping = self._mapping.get(operation)
        if mapping is None or (mapping.access == "WRITE" and not allow_write):
            raise PermissionError("Tool operation not authorized")
        result = self._transport.request(
            "tools/call", {"name": mapping.remote_tool, "arguments": arguments}
        )
        if result.get("isError"):
            raise RuntimeError("MCP tool execution failed")
        return result


class ReviewerTools:
    """Contains no transport, source path, shell or mutation entry point."""

    names = ("snapshot.read", "snapshot.objects")

    def __init__(self, snapshot: Snapshot):
        self._frozen_json = snapshot.model_dump_json()

    def call(self, operation: str, arguments: dict) -> dict:
        frozen = Snapshot.model_validate_json(self._frozen_json)
        if operation == "snapshot.read" and not arguments:
            return frozen.model_dump(mode="json")
        if (
            operation == "snapshot.objects"
            and set(arguments) == {"kind"}
            and isinstance(arguments["kind"], str)
        ):
            return {"objects": frozen.objects(arguments["kind"])}
        raise PermissionError("Reviewer tool unavailable; source mutation is not exposed")
