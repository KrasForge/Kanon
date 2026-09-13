"""Advanced models use explicit synthetic evidence and include counterexamples."""

import math
import shutil
import sys
from pathlib import Path

import pytest

from astra_pcb.agents.change_plan import ChangePlan
from astra_pcb.bom.alternates import Alternate, Compatibility
from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.engineering.audio import (
    AudioChain,
    AudioStage,
    NoiseBudget,
    NoiseSource,
    OpAmpEnvelope,
)
from astra_pcb.engineering.clocks import ClockNode, ClockTree
from astra_pcb.engineering.fpga import FamilyRules, IOStandard
from astra_pcb.engineering.fpga_device import (
    BootPlan,
    DeviceRules,
    Pin,
    RailTiming,
    check_device_decoupling,
    check_pin_plan,
    check_sequence,
)
from astra_pcb.engineering.power import Sequence
from astra_pcb.kicad.mcp import StdioTransport
from astra_pcb.kicad.visual import render_board
from astra_pcb.mechanical.collision import check_collision


@pytest.fixture
def evidence():
    return DatasheetEvidence(
        document="Synthetic engineering test limits",
        manufacturer="Test only",
        revision="1",
        page="1",
        extracted_constraint="Test fixture, no real device specification",
        source_location="test",
    )


def test_audio_headroom_and_interface_mismatch(evidence):
    stage = AudioStage(
        id="gain",
        gain_db=6.020599913,
        input_maximum_vrms=2,
        output_maximum_vrms=2,
        input_impedance_ohm=10000,
        output_impedance_ohm=10,
        input_mode="unbalanced",
        output_mode="unbalanced",
        coupling="ac",
        filtering="Declared ideal passband",
        evidence=evidence,
    )
    chain = AudioChain(
        nominal_input_vrms=0.25,
        maximum_input_vrms=0.5,
        required_headroom_db=5,
        stages=(stage,),
        level_convention="Sine-equivalent RMS, loaded gain",
    )
    assert chain.audit().exit_code == 0
    assert chain.model_copy(update={"maximum_input_vrms": 1.5}).audit().exit_code == 1
    next_stage = stage.model_copy(update={"id": "next", "gain_db": 0, "input_mode": "balanced"})
    assert chain.model_copy(update={"stages": (stage, next_stage)}).audit().exit_code == 1


def test_noise_matches_johnson_formula_and_rejects_unknown(evidence):
    source = NoiseSource(
        id="R",
        kind="resistor",
        resistance_ohm=1000,
        temperature_k=300,
        output_gain=2,
        evidence=evidence,
    )
    expected = math.sqrt(4 * 1.380649e-23 * 300 * 1000 * 20000) * 2
    budget = NoiseBudget(
        equivalent_noise_bandwidth_hz=20000,
        signal_vrms=1,
        maximum_noise_vrms=expected * 1.001,
        independent_sources=True,
        sources=(source,),
        assumptions=("Independent white source only",),
    )
    assert budget.audit().status == "PASS"
    assert (
        budget.model_copy(update={"maximum_noise_vrms": expected * 0.999}).audit().status == "FAIL"
    )
    with pytest.raises(ValueError):
        NoiseSource(id="unknown", kind="amplifier-white", output_gain=1, evidence=evidence)


def test_opamp_unknown_stability_and_range_failure(evidence):
    model = OpAmpEnvelope(
        reference="U1",
        supply_minimum_v=4,
        supply_maximum_v=6,
        supply_v=5,
        common_mode_minimum_v=0.5,
        common_mode_maximum_v=4.5,
        input_minimum_v=1,
        input_maximum_v=4,
        output_limit_minimum_v=0.2,
        output_limit_maximum_v=4.8,
        output_minimum_v=0.5,
        output_maximum_v=4.5,
        noise_gain=2,
        gbw_hz=1e6,
        signal_bandwidth_hz=20000,
        bandwidth_margin=10,
        capacitive_load_f=10e-12,
        topology="Declared noninverting stage",
        applicability="Synthetic test envelope",
        evidence=evidence,
    )
    assert [c.status.value for c in model.audit().results] == [
        "PASS",
        "PASS",
        "PASS",
        "PASS",
        "SKIP",
        "SKIP",
    ]
    bad = model.model_copy(update={"supply_v": 12, "input_maximum_v": 5})
    assert bad.audit().results[0].status == "FAIL" and bad.audit().results[1].status == "FAIL"


def test_clock_fanout_cycle_frequency_and_domain(evidence):
    root = ClockNode(
        id="osc",
        frequency_hz=10e6,
        domain="A",
        expected_termination="none",
        termination="none",
        evidence=evidence,
    )
    sink = root.model_copy(update={"id": "sink", "source": "osc"})
    assert ClockTree(nodes=(root, sink)).audit().exit_code == 0
    assert (
        ClockTree(nodes=(root, sink.model_copy(update={"frequency_hz": 11e6}))).audit().exit_code
        == 1
    )
    assert ClockTree(nodes=(root, sink.model_copy(update={"domain": "B"}))).audit().exit_code == 1
    with pytest.raises(ValueError):
        ClockTree(nodes=(root.model_copy(update={"source": "sink"}), sink))


@pytest.fixture
def device(evidence):
    banks = FamilyRules(
        part="TEST",
        package="TEST_PACKAGE",
        pin_banks={"A1": "0", "A2": "0"},
        standards={
            "TEST_DIFF": IOStandard(name="TEST_DIFF", allowed_vcco_v=(1.8,), evidence=evidence)
        },
    )
    return DeviceRules(
        banks=banks,
        pins={
            "A1": Pin(role="io", clock_capable=True, differential_partner="A2", evidence=evidence),
            "A2": Pin(role="io", differential_partner="A1", evidence=evidence),
            "B1": Pin(role="configuration", function="CONFIG", evidence=evidence),
        },
        vref_by_standard={"TEST_DIFF": 0.9},
        differential_standards=("TEST_DIFF",),
        boot_interfaces=("SPI",),
        required_configuration_pins={"B1": "CONFIG"},
        required_boot_straps={"SPI": {"MODE": "high"}},
        qualified_boot_mpns=("TEST_FLASH",),
        evidence=evidence,
    )


@pytest.fixture
def plan():
    return {
        "fpga": {
            "part": "TEST",
            "package": "TEST_PACKAGE",
            "banks": {
                "0": {
                    "voltage": 1.8,
                    "vref_v": 0.9,
                    "signals": [
                        {
                            "pin": "A1",
                            "name": "P",
                            "io_standard": "TEST_DIFF",
                            "required_voltage_v": 1.8,
                            "differential_partner": "N",
                            "requires_clock_pin": True,
                        },
                        {
                            "pin": "A2",
                            "name": "N",
                            "io_standard": "TEST_DIFF",
                            "required_voltage_v": 1.8,
                            "differential_partner": "P",
                        },
                    ],
                }
            },
            "dedicated_pins": {"B1": "CONFIG"},
        }
    }


def test_device_pin_rules_and_vref(plan, device):
    assert check_pin_plan(plan, device).exit_code == 0
    plan["fpga"]["banks"]["0"]["vref_v"] = 1.2
    assert check_pin_plan(plan, device).exit_code == 1
    plan["fpga"]["banks"]["0"]["vref_v"] = float("nan")
    with pytest.raises(ValueError):
        check_pin_plan(plan, device)


def test_device_dedicated_pair_clock_and_reserved(plan, device):
    plan["fpga"]["dedicated_pins"] = {}
    assert check_pin_plan(plan, device).exit_code == 1
    plan["fpga"]["dedicated_pins"] = {"B1": "CONFIG"}
    plan["fpga"]["banks"]["0"]["signals"][1]["requires_clock_pin"] = True
    assert check_pin_plan(plan, device).exit_code == 1
    plan["fpga"]["banks"]["0"]["signals"][1]["requires_clock_pin"] = False
    assert check_pin_plan(plan, device.model_copy(update={"reserved_pins": ("A1",)})).exit_code == 1
    plan["fpga"]["banks"]["0"]["signals"][0]["differential_partner"] = "WRONG"
    assert check_pin_plan(plan, device).exit_code == 1


def test_boot_sequencing_and_device_decoupling(device, evidence):
    boot = BootPlan(
        part="TEST",
        package="TEST_PACKAGE",
        interface="SPI",
        boot_mpn="TEST_FLASH",
        compatible_boot_mpns=("TEST_FLASH",),
        flash_supply_v=1.8,
        bank_supply_v=1.8,
        programming_header="JTAG",
        required_straps={"MODE": "high"},
        actual_straps={"MODE": "high"},
        pull_resistors={"MODE": 10000},
        evidence=evidence,
    )
    assert boot.audit(device).status == "PASS"
    assert boot.model_copy(update={"flash_supply_v": 3.3}).audit(device).status == "FAIL"
    assert boot.model_copy(update={"required_straps": {}}).audit(device).status == "FAIL"
    rule = Sequence(before="core", after="io", minimum_delay_ms=1, maximum_delay_ms=5)
    timings = (
        RailTiming(rail="core", power_up_ms=1, power_down_ms=4),
        RailTiming(rail="io", power_up_ms=3, power_down_ms=1),
    )
    assert check_sequence(timings, (rule,), evidence=evidence).exit_code == 0
    assert check_sequence(timings, (rule,)).exit_code == 2
    assert check_sequence(timings, (rule,), direction="down", evidence=evidence).exit_code == 1
    assert (
        check_device_decoupling("OTHER", "TEST_PACKAGE", (), frozenset(), device).results[0].status
        == "ERROR"
    )
    assert (
        check_device_decoupling("TEST", "TEST_PACKAGE", (), frozenset(), device).results[0].status
        == "SKIP"
    )


def test_alternate_requires_all_compatibility_evidence(evidence):
    alternate = Alternate(
        original_mpn="A",
        original_manufacturer="M1",
        candidate_mpn="B",
        candidate_manufacturer="M2",
        assessments=(),
        design_context="Test fixture",
    )
    assert alternate.check().status == "SKIP"
    assessments = tuple(
        Compatibility(
            criterion=c, compatible=True, explanation="Synthetic fixture", evidence=(evidence,)
        )
        for c in (
            "pinout",
            "electrical",
            "footprint",
            "thermal",
            "firmware",
            "assembly",
            "lifecycle",
        )
    )
    assert alternate.model_copy(update={"assessments": assessments}).check().status == "PASS"
    assert (
        alternate.model_copy(
            update={"assessments": (assessments[0].model_copy(update={"compatible": False}),)}
        )
        .check()
        .status
        == "FAIL"
    )


def test_change_plan_does_not_self_authorize_sensitive_edits():
    plan = ChangePlan(
        id="C1",
        input_digest="a" * 64,
        rationale="Test",
        affected_objects=("U1",),
        operations=("move",),
        expected_effects=("shorter route",),
        risks=(),
        verification_checks=("pcb.drc",),
        rollback_strategy="Restore snapshot",
        rollback_artifacts=("snapshot.json",),
        bank_voltage_changes=("bank0:1.8->3.3",),
    )
    with pytest.raises(PermissionError):
        plan.authorize("a" * 64)
    with pytest.raises(ValueError):
        plan.authorize("b" * 64)


def test_read_only_verifier_stdio_real_transport(tmp_path):
    before = set(tmp_path.iterdir())
    with StdioTransport((sys.executable, "-B", "-m", "astra_pcb.verifier")) as transport:
        tools = transport.request("tools/list", {})["tools"]
        assert len(tools) == 17 and all(t["annotations"]["readOnlyHint"] for t in tools)
        result = transport.request("tools/call", {"name": "check_bom", "arguments": {"items": []}})
        assert result["structuredContent"]["results"][0]["status"] == "SKIP"
        bad = transport.request(
            "tools/call", {"name": "check_bom", "arguments": {"items": [], "write_file": "x"}}
        )
        assert bad["isError"]
        with pytest.raises(ValueError):
            transport.request("tools/call", {"name": "save_board", "arguments": {}})
    assert set(tmp_path.iterdir()) == before


@pytest.mark.integration
def test_real_step_collision_overlap_clearance_and_separation(tmp_path):
    pytest.importorskip("OCP", reason="Optional geometry extra unavailable")
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    files = []
    for name, x in [("left", 0), ("overlap", 5), ("separated", 12)]:
        path = tmp_path / (name + ".step")
        writer = STEPControl_Writer()
        writer.Transfer(BRepPrimAPI_MakeBox(gp_Pnt(x, 0, 0), 10, 10, 10).Shape(), STEPControl_AsIs)
        writer.Write(str(path))
        files.append(path)
    args = {
        "minimum_clearance_mm": 1,
        "shared_frame_evidence": "Synthetic boxes in shared millimetre frame",
    }
    assert check_collision(files[0], files[1], **args).status == "FAIL"
    assert check_collision(files[0], files[2], **args).status == "PASS"
    assert (
        check_collision(files[0], files[2], **{**args, "minimum_clearance_mm": 3}).status == "FAIL"
    )


@pytest.mark.integration
def test_real_pcb_top_bottom_isometric(tmp_path):
    if not shutil.which("kicad-cli"):
        pytest.skip("KiCad CLI unavailable")
    root = Path(__file__).resolve().parents[1]
    report = render_board(root / "tests/fixtures/kicad/outline.kicad_pcb", tmp_path / "views")
    assert report.exit_code == 0


def test_bounded_check_cli_rejects_incomplete_bom_and_bad_inputs(tmp_path, capsys):
    import json

    from astra_pcb.cli import main

    assert main(["check", "check_bom", "examples/minimal-board/verifier-bom.json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert any(r["status"] == "FAIL" for r in report["results"])
    document = tmp_path / "invalid.json"
    document.write_text('{"items": [], "shell": "touch forbidden"}')
    assert main(["check", "check_bom", str(document)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["results"][0]["status"] == "ERROR"
