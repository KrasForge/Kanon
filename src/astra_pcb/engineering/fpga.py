"""Family-data-driven FPGA bank checks; no built-in manufacturer voltage assumptions."""

import math

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class IOStandard(StrictModel):
    name: str
    allowed_vcco_v: tuple[float, ...] = Field(min_length=1)
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def voltages(self):
        if any(v <= 0 or not math.isfinite(v) for v in self.allowed_vcco_v):
            raise ValueError("I/O standard requires positive finite bank voltages")
        return self


class FamilyRules(StrictModel):
    part: str
    package: str
    standards: dict[str, IOStandard]
    pin_banks: dict[str, str]


def check_banks(plan: dict, rules: FamilyRules) -> VerificationReport:
    fpga = plan["fpga"]
    results = []
    if fpga.get("part") != rules.part or fpga.get("package") != rules.package:
        return VerificationReport(
            results=(
                CheckResult(
                    check_id="fpga.identity",
                    name="FPGA identity",
                    status=CheckStatus.ERROR,
                    message="Pin-plan device/package does not match rule adapter",
                ),
            )
        )
    assigned = set()
    signal_names = set()
    for bank, definition in fpga["banks"].items():
        voltage = definition["voltage"]
        if type(voltage) not in (int, float) or not math.isfinite(voltage) or voltage <= 0:
            raise ValueError("Bank voltage must be positive and finite")
        for signal in definition["signals"]:
            standard = rules.standards.get(signal["io_standard"])
            pin = signal["pin"]
            required = signal["required_voltage_v"]
            if type(required) not in (int, float) or not math.isfinite(required) or required <= 0:
                raise ValueError("I/O voltage must be positive and finite")
            if not signal["name"] or signal["name"] in signal_names:
                raise ValueError("Duplicate/empty signal name")
            signal_names.add(signal["name"])
            reasons = []
            if abs(required - voltage) > 1e-6:
                reasons.append("required signal voltage differs from bank voltage")
            if pin in assigned:
                reasons.append("duplicate pin assignment")
            assigned.add(pin)
            if rules.pin_banks.get(pin) != bank:
                reasons.append("pin is not in the declared bank")
            if standard and (
                not any(abs(voltage - v) < 1e-6 for v in standard.allowed_vcco_v)
                or abs(signal["required_voltage_v"] - voltage) > 1e-6
            ):
                reasons.append("incompatible bank/I/O voltage")
            status = (
                CheckStatus.FAIL if reasons else CheckStatus.PASS if standard else CheckStatus.SKIP
            )
            results.append(
                CheckResult(
                    check_id=f"fpga.bank.{bank}.{signal['name']}",
                    name="FPGA bank assignment",
                    status=status,
                    message="; ".join(reasons)
                    if reasons
                    else "Assignment matches declared family rule"
                    if (standard)
                    else "Unknown I/O standard; no family rule available",
                    evidence=(standard.evidence.model_dump_json(),) if standard else (),
                    affected_objects=(pin, bank, signal["name"]),
                    source=rules.part,
                )
            )
    if not results:
        results.append(
            CheckResult(
                check_id="fpga.banks",
                name="FPGA banks",
                status=CheckStatus.SKIP,
                message="No signal assignments to validate",
            )
        )
    return VerificationReport(results=tuple(results))
