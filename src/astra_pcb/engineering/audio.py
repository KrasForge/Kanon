"""Declared audio levels, first-order noise and evidence-backed op-amp operating envelopes."""

import math
from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel, VerificationReport


class AudioStage(StrictModel):
    id: str = Field(min_length=1)
    gain_db: float
    input_maximum_vrms: float = Field(gt=0)
    output_maximum_vrms: float = Field(gt=0)
    input_impedance_ohm: float = Field(gt=0)
    output_impedance_ohm: float = Field(ge=0)
    input_mode: Literal["balanced", "unbalanced"]
    output_mode: Literal["balanced", "unbalanced"]
    coupling: Literal["ac", "dc"]
    filtering: str = Field(min_length=1)
    adc_full_scale_vrms: float | None = Field(default=None, gt=0)
    dac_full_scale_vrms: float | None = Field(default=None, gt=0)
    evidence: DatasheetEvidence


class AudioChain(StrictModel):
    nominal_input_vrms: float = Field(gt=0)
    maximum_input_vrms: float = Field(gt=0)
    required_headroom_db: float = Field(ge=0)
    stages: tuple[AudioStage, ...] = Field(min_length=1)
    level_convention: str = Field(min_length=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.nominal_input_vrms > self.maximum_input_vrms:
            raise ValueError("Nominal level exceeds maximum")
        if len({s.id for s in self.stages}) != len(self.stages):
            raise ValueError("Duplicate stage IDs")
        if any(abs(s.gain_db) > 200 for s in self.stages):
            raise ValueError("Unqualified gain magnitude")
        return self

    def audit(self) -> VerificationReport:
        nominal, maximum = self.nominal_input_vrms, self.maximum_input_vrms
        previous = None
        checks = []
        for stage in self.stages:
            gain = 10 ** (stage.gain_db / 20)
            input_limit = min(stage.input_maximum_vrms, stage.adc_full_scale_vrms or math.inf)
            output_limit = min(stage.output_maximum_vrms, stage.dac_full_scale_vrms or math.inf)
            headroom = min(
                20 * math.log10(input_limit / maximum),
                20 * math.log10(output_limit / (maximum * gain)),
            )
            interface_ok = previous is None or previous.output_mode == stage.input_mode
            # gain_db must include loading for the declared connected impedances.
            checks.append(
                CheckResult(
                    check_id=f"audio.headroom.{stage.id}",
                    name="Audio level/headroom",
                    status=CheckStatus.PASS
                    if headroom >= self.required_headroom_db and interface_ok
                    else CheckStatus.FAIL,
                    message=f"Nominal output {nominal * gain:.6g} Vrms; "
                    f"max {maximum * gain:.6g} Vrms; "
                    f"headroom {headroom:.4g} dB; interface compatible: {interface_ok}",
                    evidence=(stage.evidence.model_dump_json(), self.level_convention),
                    affected_objects=(stage.id,),
                    source="declared loaded-gain signal chain",
                )
            )
            nominal *= gain
            maximum *= gain
            previous = stage
        return VerificationReport(results=tuple(checks))


class NoiseSource(StrictModel):
    id: str = Field(min_length=1)
    kind: Literal["resistor", "amplifier-white", "converter"]
    output_gain: float = Field(gt=0)
    resistance_ohm: float = Field(default=0, ge=0)
    temperature_k: float = Field(default=293.15, ge=0)
    voltage_density_v_sqrt_hz: float = Field(default=0, ge=0)
    current_density_a_sqrt_hz: float = Field(default=0, ge=0)
    converter_noise_vrms: float | None = Field(default=None, gt=0)
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def required_parameters(self):
        if self.kind == "resistor" and self.resistance_ohm <= 0:
            raise ValueError("Resistor noise requires positive resistance")
        if (
            self.kind == "amplifier-white"
            and self.voltage_density_v_sqrt_hz <= 0
            and self.current_density_a_sqrt_hz <= 0
        ):
            raise ValueError("Amplifier noise density is unknown, not zero")
        if self.kind == "converter" and self.converter_noise_vrms is None:
            raise ValueError("Converter noise is unknown")
        return self


class NoiseBudget(StrictModel):
    equivalent_noise_bandwidth_hz: float = Field(gt=0)
    signal_vrms: float = Field(gt=0)
    maximum_noise_vrms: float = Field(gt=0)
    independent_sources: Literal[True]
    sources: tuple[NoiseSource, ...] = Field(min_length=1)
    assumptions: tuple[str, ...] = Field(min_length=1)

    def audit(self) -> CheckResult:
        if len({s.id for s in self.sources}) != len(self.sources):
            raise ValueError("Duplicate noise sources")
        squares = []
        for source in self.sources:
            if source.kind == "resistor":
                rms = math.sqrt(
                    4
                    * 1.380649e-23
                    * source.temperature_k
                    * source.resistance_ohm
                    * self.equivalent_noise_bandwidth_hz
                )
            elif source.kind == "amplifier-white":
                density = math.hypot(
                    source.voltage_density_v_sqrt_hz,
                    source.current_density_a_sqrt_hz * source.resistance_ohm,
                )
                rms = density * math.sqrt(self.equivalent_noise_bandwidth_hz)
            else:
                if source.converter_noise_vrms is None:
                    raise ValueError("Converter noise not supplied")
                rms = source.converter_noise_vrms
            squares.append((rms * source.output_gain) ** 2)
        noise = math.sqrt(sum(squares))
        snr = 20 * math.log10(self.signal_vrms / noise) if noise else math.inf
        return CheckResult(
            check_id="audio.noise",
            name="First-order uncorrelated noise budget",
            status=CheckStatus.PASS if noise <= self.maximum_noise_vrms else CheckStatus.FAIL,
            message=f"Output noise {noise:.6g} Vrms; modeled SNR {snr:.5g} dB",
            evidence=(self.model_dump_json(),),
            source="RSS/Johnson white-noise model; excludes undeclared sources",
        )


class OpAmpEnvelope(StrictModel):
    reference: str
    supply_minimum_v: float = Field(gt=0)
    supply_maximum_v: float = Field(gt=0)
    supply_v: float = Field(gt=0)
    common_mode_minimum_v: float
    common_mode_maximum_v: float
    input_minimum_v: float
    input_maximum_v: float
    output_limit_minimum_v: float
    output_limit_maximum_v: float
    output_minimum_v: float
    output_maximum_v: float
    noise_gain: float = Field(ge=1)
    minimum_stable_gain: float | None = Field(default=None, ge=1)
    gbw_hz: float = Field(gt=0)
    signal_bandwidth_hz: float = Field(gt=0)
    bandwidth_margin: float = Field(ge=1)
    capacitive_load_f: float = Field(ge=0)
    documented_capacitive_limit_f: float | None = Field(default=None, ge=0)
    topology: str = Field(min_length=1)
    applicability: str = Field(min_length=1)
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def limits(self):
        for low, high in [
            (self.supply_minimum_v, self.supply_maximum_v),
            (self.common_mode_minimum_v, self.common_mode_maximum_v),
            (self.input_minimum_v, self.input_maximum_v),
            (self.output_limit_minimum_v, self.output_limit_maximum_v),
            (self.output_minimum_v, self.output_maximum_v),
        ]:
            if low > high:
                raise ValueError("Inverted op-amp operating range")
        return self

    def audit(self) -> VerificationReport:
        checks = []
        flags = {
            "supply": self.supply_minimum_v <= self.supply_v <= self.supply_maximum_v,
            "common-mode": self.common_mode_minimum_v <= self.input_minimum_v
            and self.input_maximum_v <= self.common_mode_maximum_v,
            "swing": self.output_limit_minimum_v <= self.output_minimum_v
            and self.output_maximum_v <= self.output_limit_maximum_v,
            "bandwidth": self.gbw_hz
            >= self.signal_bandwidth_hz * self.noise_gain * self.bandwidth_margin,
            "stable-gain": None
            if self.minimum_stable_gain is None
            else self.noise_gain >= self.minimum_stable_gain,
            "capacitive-load": None
            if self.documented_capacitive_limit_f is None
            else self.capacitive_load_f <= self.documented_capacitive_limit_f,
        }
        for name, passed in flags.items():
            checks.append(
                CheckResult(
                    check_id=f"opamp.{self.reference}.{name}",
                    name=f"Op-amp {name}",
                    status=CheckStatus.SKIP
                    if passed is None
                    else CheckStatus.PASS
                    if passed
                    else CheckStatus.FAIL,
                    message="Applicable operating envelope satisfied"
                    if passed
                    else "Missing or violated operating envelope",
                    evidence=(self.model_dump_json(),),
                    source="declared op-amp topology/envelope",
                    affected_objects=(self.reference,),
                )
            )
        return VerificationReport(results=tuple(checks))
