"""KiCad execution, snapshot and capability-boundary acceptance tests."""

import json
import shutil
import sys
from pathlib import Path

import pytest

from astra_pcb.kicad import KiCadCLI
from astra_pcb.kicad.mcp import (
    DesignerTools,
    MCPProfile,
    ReviewerTools,
    StdioTransport,
    ToolMapping,
)
from astra_pcb.kicad.reports import interpret
from astra_pcb.kicad.snapshot import capture, parse_sexpr
from astra_pcb.kicad.workflow import mutate_verify
from astra_pcb.models.provenance import file_digest
from astra_pcb.verification.process import ProcessResult

FIXTURES = Path("tests/fixtures/kicad")


def report_data():
    return {
        "$schema": "https://schemas.kicad.org/drc.v1.json",
        "source": "board.kicad_pcb",
        "date": "2026-09-13T00:00:00",
        "kicad_version": "10.0.0",
        "coordinate_units": "mm",
        "included_severities": ["error", "warning", "exclusion"],
        "ignored_checks": [],
        "violations": [],
        "unconnected_items": [],
        "schematic_parity": [],
    }


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("clean", "PASS"),
        ("error", "FAIL"),
        ("warning", "WARN"),
        ("excluded", "WARN"),
        ("ignored", "WARN"),
        ("malformed", "ERROR"),
        ("missing_category", "ERROR"),
        ("wrong_source", "ERROR"),
        ("tool_failure", "ERROR"),
    ],
)
def test_kicad_report_cases(tmp_path, case, expected):
    data = report_data()
    if case in {"error", "warning", "excluded"}:
        data["violations"] = [
            {
                "type": "fixture",
                "description": "test violation",
                "severity": "warning" if case == "warning" else "error",
                "items": [],
                "excluded": case == "excluded",
            }
        ]
    if case == "ignored":
        data["ignored_checks"] = [{"key": "test", "description": "ignored rule"}]
    if case == "missing_category":
        del data["unconnected_items"]
    if case == "wrong_source":
        data["source"] = "another-board.kicad_pcb"
    output = tmp_path / "report.json"
    output.write_text("invalid" if case == "malformed" else json.dumps(data))
    process = ProcessResult(
        command=("kicad-cli",),
        exit_code=3 if case == "tool_failure" else 0,
        artifacts=(str(output),),
        artifact_hashes={str(output.resolve()): file_digest(output)},
    )
    report = interpret("drc", process, output, Path("board.kicad_pcb"))
    assert report.results[0].status == expected


def test_snapshot_diff_and_reviewer_denies_mutation(tmp_path):
    path = tmp_path / "board.kicad_pcb"
    path.write_text('(kicad_pcb (footprint "fixture" (uuid "id")))')
    before = capture(tmp_path, (Path(path.name),), "test")
    reviewer = ReviewerTools(before)
    assert len(reviewer.call("snapshot.objects", {"kind": "footprint"})["objects"]) == 1
    returned = reviewer.call("snapshot.read", {})
    returned["documents"].clear()
    assert reviewer.call("snapshot.read", {})["documents"]
    for operation in ["design.write", "tools/call", "shell", "file.write"]:
        with pytest.raises(PermissionError):
            reviewer.call(operation, {})
    path.write_text('(kicad_pcb (footprint "changed" (uuid "id")))')
    after = capture(tmp_path, (Path(path.name),), "test")
    assert before.diff(after)["changed"] == ("board.kicad_pcb",)
    assert "fixture" in reviewer.call("snapshot.read", {})["documents"][path.name]
    with pytest.raises(ValueError):
        parse_sexpr("(broken")


def test_designer_unknown_tool_and_write_denied():
    class Transport:
        def request(self, method, params):
            return {"tools": [{"name": "edit"}]} if method == "tools/list" else {"content": []}

    profile = MCPProfile(
        command=("fixture",),
        tools=(ToolMapping(operation="place", remote_tool="edit", access="WRITE"),),
    )
    designer = DesignerTools(profile, Transport())
    with pytest.raises(PermissionError):
        designer.call("place", {})
    assert designer.call("place", {}, allow_write=True) == {"content": []}
    with pytest.raises(PermissionError):
        designer.call("unclassified", {}, allow_write=True)
    with pytest.raises(ValueError, match="audited"):
        DesignerTools(MCPProfile(command=("fixture",), tools=()), Transport())


def test_real_stdio_protocol_and_tool_error(tmp_path):
    server = tmp_path / "server.py"
    server.write_text("""import json,sys
for line in sys.stdin:
    request=json.loads(line)
    if 'id' not in request: continue
    result={'protocolVersion':'2025-06-18'} if request['method']=='initialize' else {'isError':True}
    print(json.dumps({'jsonrpc':'2.0','id':request['id'],'result':result}),flush=True)
""")
    with StdioTransport((sys.executable, str(server))) as transport:
        assert transport.request("tools/call", {})["isError"]


@pytest.mark.integration
@pytest.mark.skipif(not shutil.which("kicad-cli"), reason="KiCad CLI not installed")
def test_real_kicad_checks_exports_and_mutation(tmp_path):
    schematic = tmp_path / "empty.kicad_sch"
    board = tmp_path / "outline.kicad_pcb"
    shutil.copyfile(FIXTURES / schematic.name, schematic)
    shutil.copyfile(FIXTURES / board.name, board)
    adapter = KiCadCLI()
    for kind, design in [("erc", schematic), ("drc", board)]:
        output = tmp_path / f"{kind}.json"
        result = adapter.check(kind, design, output)
        assert result.exit_code == 0 and result.error is None
        raw = json.loads(output.read_text())
        approved_ignored = frozenset(x["key"] for x in raw["ignored_checks"])
        parsed = interpret(kind, result, output, design, allowed_ignored=approved_ignored)
        assert parsed.results[0].status == "PASS"
        assert result.artifact_hashes and result.tool_version.startswith("10.")
    for kind, destination in [("gerbers", "gerbers"), ("drill", "drill"), ("step", "board.step")]:
        result = adapter.export(
            kind,
            board,
            tmp_path / destination,
            layers=("F.Cu", "B.Cu", "Edge.Cuts") if kind == "gerbers" else (),
        )
        assert result.exit_code == 0 and result.error is None, result
        assert result.artifacts and result.artifact_hashes
    result = mutate_verify(
        tmp_path,
        (Path(board.name),),
        "fixture",
        lambda: board.write_text(board.read_text().replace("(end 20 0)", "(end 19 0)")),
        tmp_path / "mutation",
    )
    assert result.prior_evidence_invalidated
    assert result.verification.exit_code == 1
    assert any(r.status == "FAIL" for r in result.verification.results)


def test_report_tampering_is_rejected(tmp_path):
    output = tmp_path / "report.json"
    output.write_text(json.dumps(report_data()))
    process = ProcessResult(
        command=("kicad-cli",),
        exit_code=0,
        artifacts=(str(output),),
        artifact_hashes={str(output): file_digest(output)},
    )
    output.write_text(output.read_text() + " ")
    assert interpret("drc", process, output, Path("board.kicad_pcb")).results[0].status == "ERROR"


def test_snapshot_tampering_is_rejected(tmp_path):
    from astra_pcb.kicad.snapshot import Snapshot

    path = tmp_path / "board.kicad_pcb"
    path.write_text("(kicad_pcb)")
    snapshot = capture(tmp_path, (Path(path.name),), "test").model_dump()
    snapshot["documents"][path.name] = "(kicad_pcb (tampered))"
    with pytest.raises(ValueError, match="content identity"):
        Snapshot.model_validate(snapshot)
