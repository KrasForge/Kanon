"""Disposable local FreeCAD/MCP qualification. Requires audited pinned provider installation.

Never opens project files. RPC is loopback-only but unauthenticated; use a private host.
The execute_code probe is harness-owned qualification code, not an exposed reviewer tool.
"""

import argparse
import json
import os
import socket
import subprocess
import time
from pathlib import Path

from astra_pcb.kicad.mcp import StdioTransport
from astra_pcb.models.provenance import canonical_digest, file_digest

PIN = "5dbfe2c80b53c3102bff0723951676e16edf2d84"


def qualify(provider: Path, output: Path) -> dict:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=provider, capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=provider,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if revision != PIN or dirty:
        raise ValueError("Provider differs from audited commit")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    # Refuse to contact an existing session, even if it responds successfully.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 9875))
    read_fd, write_fd = os.pipe()
    with (output / "xvfb.log").open("w") as log:
        xvfb = subprocess.Popen(
            ["Xvfb", "-displayfd", str(write_fd), "-screen", "0", "1024x768x24"],
            pass_fds=(write_fd,),
            stdout=log,
            stderr=log,
        )
    os.close(write_fd)
    with os.fdopen(read_fd) as stream:
        display = ":" + stream.readline().strip()
    macro = output / "qualification.FCMacro"
    macro.write_text(
        "import sys,FreeCAD,FreeCADGui\nfrom PySide import QtCore,QtWidgets\n"
        + "sys.path.insert(0,"
        + repr(str(provider / "addon/FreeCADMCP"))
        + ")\n"
        + "from rpc_server import rpc_server\n"
        + 'rpc_server.load_settings=lambda: {"remote_enabled":False,"allowed_ips":"127.0.0.1"}\n'
        + "rpc_server.start_rpc_server()\n"
        # Only dismiss startup UI in this fresh, empty qualification session.
        + "def dismiss_startup():\n    dialog=QtWidgets.QApplication.activeModalWidget()\n"
        + "    if dialog: dialog.reject()\n"
        + "QtCore.QTimer.singleShot(1500,dismiss_startup)\n"
        + "QtCore.QTimer.singleShot(110000,FreeCADGui.getMainWindow().close)\n"
    )
    with (output / "freecad.log").open("w") as log:
        freecad = subprocess.Popen(
            [
                "FreeCAD",
                "--safe-mode",
                "-u",
                str(output / "user.cfg"),
                "-s",
                str(output / "system.cfg"),
                str(macro),
            ],
            env={
                **os.environ,
                "DISPLAY": display,
                "XDG_DATA_HOME": str(output / "data"),
                "XDG_CONFIG_HOME": str(output / "config"),
            },
            stdout=log,
            stderr=log,
        )
    receipts = []
    try:
        for _ in range(100):
            try:
                with socket.create_connection(("127.0.0.1", 9875), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("FreeCAD addon did not start")
        with StdioTransport(
            (str(provider / ".venv/bin/freecad-mcp"), "--host", "127.0.0.1"), timeout=35
        ) as transport:
            listing = transport.request("tools/list", {})
            (output / "inventory.json").write_text(json.dumps(listing, indent=2))
            code = (
                "import Part,json\nfrom pathlib import Path\n"
                "d=FreeCAD.getDocument('Qualification')\nd.recompute()\n"
                + f"d.saveAs({str(output / 'board.FCStd')!r})\n"
                + f"Part.export([d.Body],{str(output / 'board.step')!r})\n"
                + f"Path({str(output / 'native.json')!r}).write_text(json.dumps("
                + "{'volume_mm3':d.Body.Shape.Volume,'valid':d.Body.Shape.isValid()}))"
            )
            for name, arguments in (
                ("create_document", {"name": "Qualification"}),
                (
                    "create_object",
                    {
                        "doc_name": "Qualification",
                        "obj_type": "Part::Box",
                        "obj_name": "Body",
                        "obj_properties": {"Length": 10, "Width": 10, "Height": 1.6},
                        "include_screenshot": False,
                    },
                ),
                ("get_objects", {"doc_name": "Qualification"}),
                ("get_object", {"doc_name": "Qualification", "obj_name": "Body"}),
                ("execute_code", {"code": code, "include_screenshot": False}),
            ):
                result = transport.request("tools/call", {"name": name, "arguments": arguments})
                if result.get("isError"):
                    raise RuntimeError("FreeCAD MCP operation failed: " + name)
                receipts.append({"tool": name, "result": result})
            native = json.loads((output / "native.json").read_text())
            if not native["valid"] or abs(native["volume_mm3"] - 160) > 1e-8:
                raise ValueError("Native FreeCAD readback differs from requested geometry")
            # A nonexistent object must produce an error message, not a success-shaped object.
            missing = transport.request(
                "tools/call",
                {
                    "name": "get_object",
                    "arguments": {"doc_name": "Qualification", "obj_name": "DOES_NOT_EXIST"},
                },
            )
            text = " ".join(c.get("text", "") for c in missing.get("content", []))
            if (
                not missing.get("isError")
                and text.strip() != "null"
                and not any(
                    word in text.lower() for word in ("not found", "error", "does not exist")
                )
            ):
                raise ValueError("Missing object was not diagnosed")
            receipts.append({"tool": "get_object-negative", "result": missing})
        receipt = {
            "provider_commit": revision,
            "inventory_digest": canonical_digest(
                {"tools": sorted(listing["tools"], key=lambda t: t["name"])}
            ),
            "native": native,
            "artifacts": {
                name: file_digest(output / name) for name in ("board.FCStd", "board.step")
            },
            "calls": receipts,
        }
        (output / "qualification.json").write_text(json.dumps(receipt, indent=2))
        return receipt
    finally:
        freecad.terminate()
        freecad.wait(timeout=10)
        xvfb.terminate()
        xvfb.wait(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = qualify(args.provider.resolve(), args.output.resolve())
    print(json.dumps({k: v for k, v in result.items() if k != "calls"}, indent=2))
