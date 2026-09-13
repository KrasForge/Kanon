"""Engineering counterexamples use explicit synthetic rules, never real device claims."""

import copy
import json
from datetime import UTC, datetime, timedelta

import pytest

from astra_pcb.bom import check_bom
from astra_pcb.bom.importer import import_bom
from astra_pcb.bom.jlcsearch import JLCSearch
from astra_pcb.bom.sourcing import SupplierAdapter, sourcing_risk
from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.datasheets.registry import Document, Registry, SourcedLimit
from astra_pcb.engineering.audits import (
    Capacitor,
    ConnectorRule,
    DecouplingRule,
    Protection,
    TestPoint,
    check_decoupling,
    check_protection,
    check_testpoints,
)
from astra_pcb.engineering.fpga import FamilyRules, IOStandard, check_banks
from astra_pcb.engineering.power import PowerTree, Regulator, check_regulator
from astra_pcb.models.provenance import file_digest


@pytest.fixture
def evidence():
    return DatasheetEvidence(
        document="Synthetic test rules, not a manufacturer datasheet",
        manufacturer="Test fixture",
        revision="1",
        page="1",
        extracted_constraint="Synthetic test limit",
        source_location="fixture.txt",
    )


def test_grouped_bom_and_conflicts(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_text(
        "References,Qty,Value,Footprint,Manufacturer,MPN\n"
        '"R1,R2",2,1k,0603,Example,PART-A\nR3,1,2k,0603,Example,PART-A\n'
    )
    items = import_bom(path)
    assert [x.reference for x in items] == ["R1", "R2", "R3"]
    assert check_bom(items)[0].status == "FAIL"
    path.write_text('Reference,Qty,Value,Footprint,MPN\n"R1 R2",3,1k,0603,X\n')
    with pytest.raises(ValueError, match="quantity"):
        import_bom(path)
    path.write_text("Reference,Reference\nR1,R2\n")
    with pytest.raises(ValueError, match="duplicate"):
        import_bom(path)


def test_bom_missing_ambiguous_and_normalized(tmp_path):
    path = tmp_path / "bom.json"
    path.write_text(
        json.dumps(
            [{"reference": " R1 ", "value": " 1k ", "package": "0603", "mpn": "PART-A or PART-B"}]
        )
    )
    assert "Ambiguous" in check_bom(import_bom(path))[0].message
    path.write_text('[{"reference":"R1","value":"1k","package":"0603"}]')
    assert check_bom(import_bom(path))[0].status == "FAIL"


@pytest.fixture
def supplier_row():
    return {
        "lcsc": 21190,
        "mfr": "0603WAF1001T5E",
        "package": "0603",
        "stock": 123,
        "price": "1-99:0.1",
        "is_basic": True,
    }


def test_mirror_never_fabricates_identity_price_currency_or_freshness(supplier_row):
    adapter = JLCSearch(fetch=lambda _: {"components": [supplier_row]})
    record, check = adapter.lookup("C21190", expected_mpn=supplier_row["mfr"])
    assert check.status == "WARN"
    assert record.stock == 123 and record.manufacturer is None
    assert record.unit_cost is None and record.stock_updated_at is None
    assert record.raw_price_tiers == "1-99:0.1"
    assert sourcing_risk(record, 200).status == "WARN"
    assert adapter.lookup("C21190", expected_mpn="different")[1].status == "ERROR"
    assert SupplierAdapter().lookup("Example", "X")[1].status == "SKIP"


@pytest.mark.parametrize("rows", [[], [{"lcsc": 99}], [None]])
def test_supplier_missing_exact_identity(rows):
    assert JLCSearch(fetch=lambda _: {"components": rows}).lookup("C21190")[1].status == "ERROR"


def test_supplier_offline_duplicate_and_stale(supplier_row):
    def offline(_):
        raise OSError("offline")

    assert JLCSearch(fetch=offline).lookup("C21190")[1].status == "ERROR"
    assert (
        JLCSearch(fetch=lambda _: {"components": [supplier_row] * 2}).lookup("C21190")[1].status
        == "ERROR"
    )
    record, _ = JLCSearch(fetch=lambda _: {"components": [supplier_row]}).lookup("C21190")
    record = record.model_copy(update={"observed_at": datetime.now(UTC) - timedelta(days=2)})
    assert "stale" in sourcing_risk(record, 1).message
    with pytest.raises(ValueError):
        JLCSearch("https://user:password@example.com")


def test_registry_revision_hash_and_units(tmp_path):
    source = tmp_path / "rules.txt"
    source.write_text("Synthetic limit: supply maximum 3.6 V; unit-test evidence only.")
    document = Document(
        id="fixture-v1",
        components=("EXAMPLE",),
        manufacturer="Fixture",
        title="Test rules",
        revision="1",
        local_path="rules.txt",
        sha256=file_digest(source),
    )
    registry = Registry(tmp_path)
    registry.register(document)
    registry.save(tmp_path / "index.json")
    registry = Registry.load(tmp_path, tmp_path / "index.json")
    evidence = registry.citation("fixture-v1", constraint="Maximum 3.6 V", page="1")
    limit = SourcedLimit(
        id="supply", maximum=3.6, unit="V", applicability="Test fixture", evidence=evidence
    )
    assert limit.check(3.3, "V", registry).status == "PASS"
    assert limit.check(5, "V", registry).status == "FAIL"
    assert limit.check(3300, "mV", registry).status == "ERROR"
    source.write_text("Changed rules")
    assert limit.check(3.3, "V", registry).status == "ERROR"
    with pytest.raises(ValueError):
        registry.register(document.model_copy(update={"local_path": "../outside.txt"}))


@pytest.fixture
def power():
    return PowerTree.model_validate(
        {
            "rails": [
                {
                    "id": "input",
                    "conversion": "source",
                    "minimum_v": 4.75,
                    "nominal_v": 5,
                    "maximum_v": 5.25,
                    "current_limit_a": 1,
                },
                {
                    "id": "logic",
                    "source": "input",
                    "conversion": "linear",
                    "minimum_v": 3.2,
                    "nominal_v": 3.3,
                    "maximum_v": 3.4,
                    "current_limit_a": 0.5,
                },
            ],
            "loads": [{"id": "load", "rail": "logic", "expected_a": 0.2, "peak_a": 0.4}],
        }
    )


def test_power_budget_and_conservative_thermal(power, evidence):
    assert power.demand("input") == pytest.approx(0.4)
    assert power.audit().exit_code == 0
    regulator = Regulator(
        reference="U1",
        output_rail="logic",
        input_minimum_v=4,
        input_maximum_v=6,
        dropout_v=0.3,
        ambient_maximum_c=85,
        junction_maximum_c=125,
        evidence=evidence,
    )
    assert check_regulator(power, regulator).results[1].status == "SKIP"
    regulator = regulator.model_copy(
        update={"theta_ja_c_per_w": 60, "thermal_conditions": "Synthetic test board"}
    )
    assert check_regulator(power, regulator).results[1].status == "FAIL"  # 85 + .82*60 = 134.2
    too_low = regulator.model_copy(update={"input_maximum_v": 5})
    assert check_regulator(power, too_low).results[0].status == "FAIL"


def test_power_cycles_and_switching_propagation(power):
    data = power.model_dump()
    data["sequencing"] = [{"before": "logic", "after": "input"}]
    with pytest.raises(ValueError, match="Cyclic"):
        PowerTree.model_validate(data)
    data["sequencing"] = []
    data["rails"][1].update(conversion="switching", efficiency_min=0.8)
    switched = PowerTree.model_validate(data)
    assert switched.demand("input") == pytest.approx(0.4 * 3.4 / (4.75 * 0.8))
    data["rails"][0]["current_limit_a"] = 0.1
    assert PowerTree.model_validate(data).audit().exit_code == 1


def test_fpga_conflict_unknown_and_duplicate(evidence):
    rules = FamilyRules(
        part="TEST",
        package="TEST_PACKAGE",
        pin_banks={"A1": "0", "A2": "0"},
        standards={"TEST33": IOStandard(name="TEST33", allowed_vcco_v=(3.3,), evidence=evidence)},
    )
    plan = {
        "fpga": {
            "part": "TEST",
            "package": "TEST_PACKAGE",
            "banks": {
                "0": {
                    "voltage": 3.3,
                    "signals": [
                        {
                            "pin": "A1",
                            "name": "signal",
                            "io_standard": "TEST33",
                            "required_voltage_v": 3.3,
                        }
                    ],
                }
            },
        }
    }
    assert check_banks(plan, rules).exit_code == 0
    bad = copy.deepcopy(plan)
    bad["fpga"]["banks"]["0"]["voltage"] = 1.8
    assert check_banks(bad, rules).exit_code == 1
    signal = plan["fpga"]["banks"]["0"]["signals"][0]
    signal["io_standard"] = "unknown"
    assert check_banks(plan, rules).results[0].status == "SKIP"
    signal["io_standard"] = "TEST33"
    plan["fpga"]["banks"]["0"]["signals"].append({**signal, "name": "other"})
    assert check_banks(plan, rules).results[1].status == "FAIL"


def test_declared_decoupling_unknown_geometry_and_missing_component(evidence):
    rule = DecouplingRule(
        component="U1",
        power_pin="1",
        rail="3V3",
        minimum_effective_f=50e-9,
        maximum_distance_mm=3,
        evidence=evidence,
    )
    capacitor = Capacitor(
        reference="C1", rail="3V3", local_to="U1", effective_f=70e-9, evidence=evidence
    )
    refs = frozenset({"U1", "C1"})
    assert check_decoupling((rule,), (capacitor,), refs).results[0].status == "SKIP"
    near = capacitor.model_copy(update={"distance_mm": 2})
    assert check_decoupling((rule,), (near,), refs).exit_code == 0
    assert check_decoupling((rule,), (near,), frozenset({"C1"})).exit_code == 1
    assert (
        check_decoupling((rule,), (near.model_copy(update={"distance_mm": 8}),), refs).exit_code
        == 1
    )


def test_connector_and_probe_coverage(evidence):
    rule = ConnectorRule(reference="J1", interface="test", required={"ESD": ("D+", "D-")})
    device = Protection(reference="D1", feature="ESD", nets=("D+",), evidence=evidence)
    assert check_protection((rule,), (device,), frozenset({"J1", "D1"})).exit_code == 1
    complete = device.model_copy(update={"nets": ("D+", "D-")})
    assert check_protection((rule,), (complete,), frozenset({"J1", "D1"})).exit_code == 0
    point = TestPoint(reference="TP1", net="3V3")
    assert check_testpoints({"3V3": 1}, (point,)).results[0].status == "SKIP"
    accessible = point.model_copy(update={"accessible": True, "probe_clearance_mm": 1.2})
    assert check_testpoints({"3V3": 1}, (accessible,)).exit_code == 0
    assert check_testpoints({"GND": 1}, (accessible,)).exit_code == 1
