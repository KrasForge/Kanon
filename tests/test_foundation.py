import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from astra_pcb.bom import BOMItem, check_bom
from astra_pcb.cli import main
from astra_pcb.config import validate_document
from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.kicad import KiCadCLI
from astra_pcb.models import CheckResult, CheckStatus, VerificationReport
from astra_pcb.release import GateConfig, ReleaseGate, evaluate
from astra_pcb.simulation import assert_limit, measurements
from astra_pcb.verification.process import run


@pytest.mark.parametrize("status", list(CheckStatus))
def test_report_roundtrip_and_gate(status):
    report = VerificationReport(
        results=(CheckResult(check_id="drc", name="DRC", status=status, message="fixture"),)
    )
    assert VerificationReport.model_validate_json(report.model_dump_json()) == report
    gates = GateConfig(gates=(ReleaseGate(check_id="drc", mode="AUTOMATED"),))
    assert evaluate(gates, report).exit_code == (0 if status == CheckStatus.PASS else 1)


def test_missing_manual_duplicate_and_empty_gates():
    config = GateConfig(gates=(ReleaseGate(check_id="review", mode="MANUAL"),))
    passed = CheckResult(check_id="review", name="review", status="PASS", message="untrusted")
    assert evaluate(config, VerificationReport(results=(passed,))).exit_code == 1
    assert evaluate(config, VerificationReport(results=())).exit_code == 1
    with pytest.raises(ValueError, match="duplicate result"):
        evaluate(config, VerificationReport(results=(passed, passed)))
    with pytest.raises(ValidationError):
        GateConfig(gates=())
    with pytest.raises(ValidationError):
        GateConfig(gates=(ReleaseGate(check_id="x", mode="AUTOMATED", mandatory=False),))


def test_optional_gate_does_not_hide_missing():
    config = GateConfig(
        gates=(
            ReleaseGate(check_id="ok", mode="AUTOMATED"),
            ReleaseGate(check_id="extra", mode="AUTOMATED", mandatory=False),
        )
    )
    report = VerificationReport(
        results=(CheckResult(check_id="ok", name="ok", status="PASS", message="ok"),)
    )
    result = evaluate(config, report)
    assert result.results[1].status == CheckStatus.WARN
    assert result.exit_code == 2


@pytest.mark.parametrize(
    ("status", "code"), [("PASS", 0), ("FAIL", 1), ("ERROR", 1), ("WARN", 2), ("SKIP", 2)]
)
def test_exit_codes(status, code):
    assert (
        VerificationReport(
            results=(CheckResult(check_id="x", name="x", status=status, message="x"),)
        ).exit_code
        == code
    )


def test_process_success_failure_timeout_and_missing(tmp_path):
    ok = run([sys.executable, "-c", 'print("ok")'])
    assert ok.exit_code == 0 and ok.stdout.strip() == "ok"
    bad = run([sys.executable, "-c", 'import sys; sys.stderr.write("bad"); sys.exit(3)'])
    assert bad.exit_code == 3 and bad.stderr == "bad"
    missing = run(["astra-pcb-nonexistent-executable"])
    assert missing.exit_code is None and missing.error
    timeout = run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.01)
    assert timeout.exit_code is None and timeout.error


def test_kicad_command_is_independent_and_no_overwrite(monkeypatch, tmp_path):
    from astra_pcb.verification.process import ProcessResult

    commands = []

    def fake(command, **kwargs):
        commands.append(command)
        return ProcessResult(command=tuple(command), exit_code=0, stdout="10.0.0")

    monkeypatch.setattr("astra_pcb.kicad.run", fake)
    (tmp_path / "board.kicad_pcb").write_text("fixture")
    output = tmp_path / "drc.json"
    KiCadCLI().check("drc", tmp_path / "board.kicad_pcb", output)
    assert commands[1][1:3] == ["pcb", "drc"]
    assert "--exit-code-violations" in commands[1]
    assert "--save-board" not in commands[1]
    output.write_text("{}")
    with pytest.raises(FileExistsError):
        KiCadCLI().check("drc", tmp_path / "board.kicad_pcb", output)


def test_simulation_limits():
    values = measurements("gain_db = 6.01\ncutoff_hz = 2e4\nbad = failed\n")
    assert assert_limit("gain_db", values, 5.8, 6.2).status == CheckStatus.PASS
    assert assert_limit("cutoff_hz", values, 1, 10).status == CheckStatus.FAIL
    assert assert_limit("missing", values, 1, 10).status == CheckStatus.ERROR
    assert assert_limit("x", {"x": float("nan")}, 1, 10).status == CheckStatus.ERROR
    with pytest.raises(ValueError):
        assert_limit("x", {}, 10, 1)


def test_bom_inconsistency_missing_and_empty():
    first = BOMItem(reference="R1", value="10k", package="0603", mpn="RES", manufacturer="M")
    second = first.model_copy(update={"reference": "R2", "package": "0805"})
    assert check_bom([first])[0].status == CheckStatus.PASS
    assert check_bom([first, second])[0].status == CheckStatus.FAIL
    assert check_bom([first, first])[0].status == CheckStatus.FAIL
    assert check_bom([first.model_copy(update={"mpn": None})])[0].status == CheckStatus.FAIL
    assert check_bom([])[0].status == CheckStatus.SKIP


def test_evidence_requires_locator():
    data = dict(
        document="Datasheet",
        manufacturer="M",
        revision="A",
        extracted_constraint="Documented limit",
        source_location="local.pdf",
    )
    with pytest.raises(ValidationError):
        DatasheetEvidence(**data)
    assert DatasheetEvidence(**data, page="4").page == "4"


def test_schemas_examples_and_rejection(tmp_path):
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import ValidationError as SchemaError

    for path in Path("schemas").glob("*.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    validate_document(
        Path("examples/minimal-board/design-spec.yaml"), Path("schemas/design-spec.schema.json")
    )
    validate_document(Path("templates/pin-plan.yaml"), Path("schemas/pin-plan.schema.json"))
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema_version: '1.0'\n")
    with pytest.raises(SchemaError):
        validate_document(bad, Path("schemas/design-spec.schema.json"))


def test_cli_safe_defaults_and_invalid_input(tmp_path, capsys):
    assert main(["validate", "examples/minimal-board/design-spec.yaml"]) == 0
    assert main(["verify"]) == 1
    assert main(["release"]) == 1
    missing = tmp_path / "missing.json"
    assert main(["verify", "--report", str(missing)]) == 1
    assert "ERROR" in capsys.readouterr().out


def test_backlog_is_complete_acyclic_and_unique():
    catalog = json.loads(Path(".github/backlog.json").read_text())["issues"]
    assert len(catalog) == 76
    assert len({i["title"] for i in catalog}) == len(catalog)
    by_id = {i["id"]: i for i in catalog}

    def visit(issue_id, chain):
        assert issue_id not in chain, f"dependency cycle {chain} -> {issue_id}"
        for dep in by_id[issue_id]["dependencies"]:
            visit(dep, [*chain, issue_id])

    for issue in catalog:
        visit(issue["id"], [])


def test_process_preserves_timeout_output_and_cwd_artifacts(tmp_path):
    timeout = run(
        [sys.executable, "-u", "-c", 'import time; print("started", flush=True); time.sleep(5)'],
        timeout=0.3,
    )
    assert timeout.error and "started" in timeout.stdout
    result = run(
        [sys.executable, "-c", 'from pathlib import Path; Path("result.txt").write_text("data")'],
        cwd=tmp_path,
        artifacts=(Path("result.txt"),),
    )
    assert result.artifacts == (str(tmp_path / "result.txt"),)


def test_malformed_yaml_is_structured_error(tmp_path, capsys):
    config = tmp_path / "gates.yaml"
    config.write_text("gates: [invalid")
    assert main(["verify", "--gates", str(config)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "ERROR"
