"""Device-adapter pin, boot, sequencing and decoupling rules; no universal FPGA assumptions."""

import math
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.engineering.audits import Capacitor, DecouplingRule, check_decoupling
from astra_pcb.engineering.fpga import FamilyRules, check_banks
from astra_pcb.engineering.power import Sequence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class Pin(StrictModel):
    role: Literal[
        "io", "clock", "configuration", "jtag", "power", "ground", "reserved", "no-connect"
    ]
    clock_capable: bool = False
    function: str | None = None
    differential_partner: str | None = None
    evidence: DatasheetEvidence


class DeviceRules(StrictModel):
    banks: FamilyRules
    pins: dict[str, Pin] = Field(min_length=1)
    vref_by_standard: dict[str, float] = {}
    differential_standards: tuple[str, ...] = ()
    boot_interfaces: tuple[str, ...] = Field(min_length=1)
    required_configuration_pins: dict[str, str]
    required_boot_straps: dict[str, dict[str, Literal["high", "low"]]] = {}
    qualified_boot_mpns: tuple[str, ...] = ()
    reserved_pins: tuple[str, ...] = ()
    sequencing: tuple[Sequence, ...] = ()
    decoupling: tuple[DecouplingRule, ...] = ()
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def references(self):
        for name, pin in self.pins.items():
            if pin.differential_partner is not None:
                other = self.pins.get(pin.differential_partner)
                if other is None or other.differential_partner != name:
                    raise ValueError("Device differential pair map must be reciprocal")
        if (
            set(self.required_configuration_pins) - self.pins.keys()
            or set(self.reserved_pins) - self.pins.keys()
        ):
            raise ValueError("Device config/reserved pin missing physical pin data")
        if any(v <= 0 for v in self.vref_by_standard.values()):
            raise ValueError("Positive VREF required")
        return self


def check_pin_plan(plan: dict, rules: DeviceRules) -> VerificationReport:
    base = check_banks(plan, rules.banks)
    if any(c.status == CheckStatus.ERROR for c in base.results):
        return base
    fpga = plan["fpga"]
    checks = list(base.results)
    clock_destinations = {
        destination for clock in fpga.get("clocks", []) for destination in clock["destinations"]
    }
    signals = {s["pin"]: s for bank in fpga["banks"].values() for s in bank["signals"]}
    for bank_name, bank in fpga["banks"].items():
        for signal in bank["signals"]:
            pin = rules.pins.get(signal["pin"])
            faults = []
            unknown = []
            if pin is None:
                unknown.append("No physical device-pin rule")
            else:
                if (
                    pin.role in {"power", "ground", "reserved", "no-connect"}
                    or signal["pin"] in rules.reserved_pins
                ):
                    faults.append("Non-I/O/reserved pin used as signal")
                if (
                    signal.get("requires_clock_pin") or signal["name"] in clock_destinations
                ) and not pin.clock_capable:
                    faults.append("Clock requires dedicated-capable pin")
                if pin.role in {"configuration", "jtag"} and signal["name"] != pin.function:
                    faults.append("Dedicated function mismatch")
                required_vref = rules.vref_by_standard.get(signal["io_standard"])
                if required_vref is not None:
                    if bank.get("vref_v") is not None and not math.isfinite(bank["vref_v"]):
                        raise ValueError("Nonfinite VREF")
                    if bank.get("vref_v") is None:
                        unknown.append("Required VREF missing")
                    elif abs(bank["vref_v"] - required_vref) > 1e-6:
                        faults.append("VREF mismatch")
                if signal["io_standard"] in rules.differential_standards:
                    partner = signals.get(pin.differential_partner)
                    if partner is None or signal.get("differential_partner") != partner["name"]:
                        faults.append("Missing/wrong differential partner")
                    elif (
                        partner.get("differential_partner") != signal["name"]
                        or partner["io_standard"] != signal["io_standard"]
                    ):
                        faults.append("Nonreciprocal/mixed-standard pair")
            checks.append(
                CheckResult(
                    check_id=f"fpga.pin.{signal['name']}",
                    name="Device-family pin plan",
                    status=CheckStatus.FAIL
                    if faults
                    else CheckStatus.SKIP
                    if unknown
                    else CheckStatus.PASS,
                    message="; ".join(faults + unknown) or "Assignment matches device adapter",
                    affected_objects=(signal["pin"], bank_name),
                    evidence=(rules.evidence.model_dump_json(),),
                )
            )
    dedicated = fpga.get("dedicated_pins", {})
    for pin, function in rules.required_configuration_pins.items():
        actual = dedicated.get(pin) or signals.get(pin, {}).get("name")
        checks.append(
            CheckResult(
                check_id=f"fpga.dedicated.{pin}",
                name="Dedicated configuration pin",
                status=CheckStatus.PASS if actual == function else CheckStatus.FAIL,
                message=f"Required {function}; declared {actual}",
                affected_objects=(pin,),
                evidence=(rules.pins[pin].evidence.model_dump_json(),),
            )
        )
    for pin in dedicated:
        if pin not in rules.required_configuration_pins:
            checks.append(
                CheckResult(
                    check_id=f"fpga.dedicated.unknown.{pin}",
                    name="Unknown dedicated pin",
                    status=CheckStatus.FAIL,
                    message="Dedicated assignment not present in family rules",
                )
            )
    return VerificationReport(results=tuple(checks))


class BootPlan(StrictModel):
    part: str
    package: str
    interface: str
    boot_mpn: str = Field(min_length=1)
    compatible_boot_mpns: tuple[str, ...] = Field(min_length=1)
    flash_supply_v: float = Field(gt=0)
    bank_supply_v: float = Field(gt=0)
    programming_header: str | None = None
    required_straps: dict[str, Literal["high", "low"]]
    actual_straps: dict[str, Literal["high", "low", "floating"]]
    pull_resistors: dict[str, float]
    evidence: DatasheetEvidence

    def audit(self, rules: DeviceRules) -> CheckResult:
        failures = []
        unknown = []
        expected_straps = rules.required_boot_straps.get(self.interface)
        if expected_straps is None:
            unknown.append("Family boot-strap rules absent")
        elif self.required_straps != expected_straps:
            failures.append("Project omitted/changed family strap expectations")
        if not rules.qualified_boot_mpns:
            unknown.append("No family-qualified boot parts")
        elif self.boot_mpn not in rules.qualified_boot_mpns:
            failures.append("Boot part not qualified by family data")
        if self.part != rules.banks.part or self.package != rules.banks.package:
            failures.append("Device/package mismatch")
        if self.interface not in rules.boot_interfaces:
            failures.append("Unsupported configuration interface")
        if self.boot_mpn not in self.compatible_boot_mpns:
            failures.append("Boot flash not evidence-qualified")
        if abs(self.flash_supply_v - self.bank_supply_v) > 1e-6:
            failures.append("Configuration voltage mismatch; declare translator separately")
        if not self.programming_header:
            failures.append("Programming header missing")
        for net, level in self.required_straps.items():
            if self.actual_straps.get(net) != level:
                failures.append("Wrong/floating strap: " + net)
            if not 0 < self.pull_resistors.get(net, 0):
                failures.append("Missing pull resistor: " + net)
        return CheckResult(
            check_id="fpga.boot",
            name="FPGA configuration/boot audit",
            status=CheckStatus.FAIL
            if failures
            else CheckStatus.SKIP
            if unknown
            else CheckStatus.PASS,
            message="; ".join(failures + unknown) or "Declared boot requirements satisfied",
            evidence=(self.model_dump_json(), rules.evidence.model_dump_json()),
        )


class RailTiming(StrictModel):
    rail: str
    power_up_ms: float = Field(ge=0)
    power_down_ms: float = Field(ge=0)


def check_sequence(
    timings: tuple[RailTiming, ...],
    rules: tuple[Sequence, ...],
    *,
    direction: Literal["up", "down"] = "up",
    evidence: DatasheetEvidence | None = None,
) -> VerificationReport:
    if len({t.rail for t in timings}) != len(timings):
        raise ValueError("Duplicate rail timings")
    observed = {t.rail: t.power_up_ms if direction == "up" else t.power_down_ms for t in timings}
    checks = []
    for index, rule in enumerate(rules):
        delay = observed.get(rule.after, 0) - observed.get(rule.before, 0)
        known = rule.after in observed and rule.before in observed
        passed = (
            known
            and delay >= rule.minimum_delay_ms
            and (rule.maximum_delay_ms is None or delay <= rule.maximum_delay_ms)
        )
        checks.append(
            CheckResult(
                check_id=f"fpga.sequence.{direction}.{index}",
                name="FPGA rail timing",
                status=CheckStatus.SKIP
                if not known or (passed and evidence is None)
                else CheckStatus.PASS
                if passed
                else CheckStatus.FAIL,
                message=(
                    f"Observed {delay if known else None} ms "
                    f"between {rule.before} and {rule.after}; "
                    f"device rule citation present: {evidence is not None}"
                ),
                evidence=(rule.model_dump_json(),)
                + ((evidence.model_dump_json(),) if evidence else ()),
                affected_objects=(rule.before, rule.after),
            )
        )
    if not checks:
        checks.append(
            CheckResult(
                check_id="fpga.sequence",
                name="FPGA sequencing",
                status=CheckStatus.SKIP,
                message="No device-specific sequence rules",
            )
        )
    return VerificationReport(results=tuple(checks))


def check_device_decoupling(
    part: str,
    package: str,
    capacitors: tuple[Capacitor, ...],
    references: frozenset[str],
    rules: DeviceRules,
) -> VerificationReport:
    if (part, package) != (rules.banks.part, rules.banks.package):
        return VerificationReport(
            results=(
                CheckResult(
                    check_id="fpga.decoupling",
                    name="Device decoupling",
                    status=CheckStatus.ERROR,
                    message="Device/package does not match decoupling rule adapter",
                ),
            )
        )
    return check_decoupling(rules.decoupling, capacitors, references)
