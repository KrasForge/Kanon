"""Golden status semantics prevent missing/skipped evidence becoming approval."""

import json
from pathlib import Path

from astra_pcb.models import VerificationReport
from astra_pcb.release import GateConfig, ReleaseGate, evaluate


def test_golden_all_statuses():
    fixture = json.loads((Path(__file__).parent / "fixtures/report-statuses.json").read_text())
    report = VerificationReport.model_validate(fixture["report"])
    gates = GateConfig(
        gates=tuple(ReleaseGate(check_id=r.check_id, mode="AUTOMATED") for r in report.results)
    )
    evaluated = evaluate(gates, report)
    assert [r.status.value for r in evaluated.results] == fixture["expected_gate_statuses"]
    assert evaluated.exit_code == fixture["expected_exit_code"]
