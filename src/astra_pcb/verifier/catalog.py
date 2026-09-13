"""Only implemented, pure-data checks are exposed. No paths, network or mutations."""

from pydantic import Field

from astra_pcb.bom import BOMItem, check_board_bom, check_bom
from astra_pcb.bom.alternates import Alternate
from astra_pcb.bom.sourcing import SourcingRecord, sourcing_risk
from astra_pcb.engineering.audio import AudioChain, NoiseBudget, OpAmpEnvelope
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
from astra_pcb.engineering.clocks import ClockTree
from astra_pcb.engineering.fpga import FamilyRules, check_banks
from astra_pcb.engineering.fpga_device import BootPlan, DeviceRules, check_pin_plan
from astra_pcb.engineering.power import PowerTree, Regulator, check_regulator
from astra_pcb.manufacturing import Feature, ManufacturingProfile, check_dfm
from astra_pcb.models import CheckResult, StrictModel, VerificationReport


class BOMInput(StrictModel):
    items: tuple[BOMItem, ...] = Field(max_length=500)


class BoardBOMInput(BOMInput):
    board_text: str = Field(max_length=500000)


class SourcingInput(StrictModel):
    record: SourcingRecord
    needed: int = Field(gt=0)


class RegulatorInput(StrictModel):
    tree: PowerTree
    regulator: Regulator


class BanksInput(StrictModel):
    plan: dict
    rules: FamilyRules


class DeviceInput(StrictModel):
    plan: dict
    rules: DeviceRules


class BootInput(StrictModel):
    plan: BootPlan
    rules: DeviceRules


class DecouplingInput(StrictModel):
    rules: tuple[DecouplingRule, ...]
    capacitors: tuple[Capacitor, ...]
    references: frozenset[str]


class ProtectionInput(StrictModel):
    rules: tuple[ConnectorRule, ...]
    devices: tuple[Protection, ...]
    references: frozenset[str]


class TestpointsInput(StrictModel):
    required: dict[str, float]
    points: tuple[TestPoint, ...]


class DFMInput(StrictModel):
    profile: ManufacturingProfile
    features: tuple[Feature, ...]
    layer_count: int = Field(ge=2)
    thickness_mm: float = Field(gt=0)


# name -> (validated input, pure callable, scope description)
CHECKS = {
    "check_power_tree": (PowerTree, lambda x: x.audit(), "Declared rail/load current budgets"),
    "check_regulator": (
        RegulatorInput,
        lambda x: check_regulator(x.tree, x.regulator),
        "Cited regulator range/thermal estimate",
    ),
    "check_bom": (
        BOMInput,
        lambda x: check_bom(list(x.items)),
        "Canonical MPN/metadata consistency",
    ),
    "check_native_bom": (
        BoardBOMInput,
        lambda x: check_board_bom(list(x.items), x.board_text),
        "Native footprint/value/reference parity",
    ),
    "check_bom_sourcing": (
        SourcingInput,
        lambda x: sourcing_risk(x.record, x.needed),
        "Declared lifecycle/stock/freshness/source diversity",
    ),
    "check_alternate": (
        Alternate,
        lambda x: x.check(),
        "Evidence coverage for alternate compatibility; never substitutes",
    ),
    "check_fpga_banks": (
        BanksInput,
        lambda x: check_banks(x.plan, x.rules),
        "Declared FPGA bank compatibility",
    ),
    "check_fpga_pin_plan": (
        DeviceInput,
        lambda x: check_pin_plan(x.plan, x.rules),
        "Device-data dedicated/pair/VREF/clock pin assignments",
    ),
    "check_fpga_boot": (
        BootInput,
        lambda x: x.plan.audit(x.rules),
        "Declared configuration/flash/strap expectations",
    ),
    "check_decoupling": (
        DecouplingInput,
        lambda x: check_decoupling(x.rules, x.capacitors, x.references),
        "Declared capacitance/count/distance rules",
    ),
    "check_connector_protection": (
        ProtectionInput,
        lambda x: check_protection(x.rules, x.devices, x.references),
        "Declared protection feature/net coverage",
    ),
    "check_testpoint_coverage": (
        TestpointsInput,
        lambda x: check_testpoints(x.required, x.points),
        "Declared accessible test-point coverage",
    ),
    "check_clock_topology": (
        ClockTree,
        lambda x: x.audit(),
        "Declared clock topology/termination/domain expectations",
    ),
    "check_audio_signal_chain": (
        AudioChain,
        lambda x: x.audit(),
        "Declared loaded-gain/headroom envelope",
    ),
    "check_audio_noise": (
        NoiseBudget,
        lambda x: x.audit(),
        "First-order uncorrelated noise budget",
    ),
    "check_opamp": (
        OpAmpEnvelope,
        lambda x: x.audit(),
        "Cited operating ranges; not a phase-margin solver",
    ),
    "check_manufacturability": (
        DFMInput,
        lambda x: check_dfm(
            x.profile, x.features, layer_count=x.layer_count, thickness_mm=x.thickness_mm
        ),
        "Declared measured DFM features and profile",
    ),
}


def execute(name: str, arguments: dict) -> VerificationReport:
    if name not in CHECKS:
        raise ValueError("Unimplemented or unavailable verification tool")
    model, check, _ = CHECKS[name]
    value = check(model.model_validate(arguments))
    if isinstance(value, VerificationReport):
        return value
    if isinstance(value, CheckResult):
        return VerificationReport(results=(value,))
    return VerificationReport(results=tuple(value))
