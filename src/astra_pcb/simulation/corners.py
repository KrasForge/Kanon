"""Reproducible source/load/component-corner workflows using actual ngspice measurements."""

import itertools
import math
from pathlib import Path

from pydantic import Field

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import StrictModel, VerificationReport
from astra_pcb.models.provenance import file_digest
from astra_pcb.simulation.models import ModelFile
from astra_pcb.simulation.workflow import SimulationJob, run_job


class AudioFilterSweep(StrictModel):
    resistance_ohm: tuple[float, ...] = Field(min_length=1, max_length=3)
    capacitance_f: tuple[float, ...] = Field(min_length=1, max_length=3)
    source_ohm: tuple[float, ...] = Field(min_length=1, max_length=3)
    load_ohm: tuple[float, ...] = Field(min_length=1, max_length=3)
    gain_min_db: float
    gain_max_db: float
    cutoff_min_hz: float = Field(gt=0)
    cutoff_max_hz: float = Field(gt=0)
    evidence: DatasheetEvidence

    def run(self, output: Path) -> VerificationReport:
        output.mkdir(parents=True, exist_ok=False)
        checks = []
        for index, (resistance, capacitance, source, load) in enumerate(
            itertools.product(
                self.resistance_ohm, self.capacitance_f, self.source_ohm, self.load_ohm
            )
        ):
            if min(resistance, capacitance, load) <= 0 or source < 0:
                raise ValueError("Invalid circuit corner")
            folder = output / f"corner-{index}"
            folder.mkdir()
            dc_gain = 20 * math.log10(load / (load + source + resistance))
            # Each corner includes physical source and load impedances.
            circuit = f"""Qualified loaded RC filter corner
Vinput in 0 AC 1
Rsource in r {max(source, 1e-9):.12g}
Rseries r out {resistance:.12g}
Cfilter out 0 {capacitance:.12g}
Rload out 0 {load:.12g}
.control
ac dec 300 1 100Meg
let gain = db(v(out))
let relative_gain = gain - ({dc_gain:.12g})
meas ac passband FIND gain AT=1
meas ac cutoff WHEN relative_gain=-3.010299956 CROSS=1
quit
.endc
.end
"""
            (folder / "circuit.cir").write_text(circuit)
            job = SimulationJob.model_validate(
                {
                    "netlist": "circuit.cir",
                    "description": "Loaded RC filter corner",
                    "assumptions": [
                        "Linear passive RC, no parasitic/THD/active stability claim",
                        self.evidence.model_dump_json(),
                    ],
                    "measurement_units": {"passband": "dB", "cutoff": "Hz"},
                    "assertions": {
                        "passband": {
                            "min": self.gain_min_db,
                            "max": self.gain_max_db,
                            "unit": "dB",
                        },
                        "cutoff": {
                            "min": self.cutoff_min_hz,
                            "max": self.cutoff_max_hz,
                            "unit": "Hz",
                        },
                    },
                }
            )
            report = run_job(job, folder, folder / "simulation.log")
            checks.extend(
                r.model_copy(update={"check_id": f"filter.{index}.{r.check_id}"})
                for r in report.results
            )
        return VerificationReport(results=tuple(checks))


class PowerSweep(StrictModel):
    source_v: tuple[float, ...] = Field(min_length=1, max_length=3)
    source_resistance_ohm: tuple[float, ...] = Field(min_length=1, max_length=3)
    capacitance_f: tuple[float, ...] = Field(min_length=1, max_length=3)
    load_a: float = Field(gt=0)
    evidence: DatasheetEvidence

    def run(self, output: Path) -> VerificationReport:
        output.mkdir(parents=True, exist_ok=False)
        checks = []
        for index, (voltage, resistance, capacitance) in enumerate(
            itertools.product(self.source_v, self.source_resistance_ohm, self.capacitance_f)
        ):
            if min(voltage, resistance, capacitance) <= 0:
                raise ValueError("Invalid power corner")
            if resistance * capacitance > 0.0001:
                raise ValueError("Corner exceeds qualified settling-time envelope")
            folder = output / f"corner-{index}"
            folder.mkdir()
            model = folder / "supply.lib"
            model.write_text(
                ".lib RC\n.subckt SUPPLY vin out\n"
                f"Rsrc vin out {resistance:.12g}\nCbulk out 0 {capacitance:.12g}\n"
                ".ends SUPPLY\n.endl RC\n"
            )
            rail = voltage - self.load_a * resistance
            if rail <= 0:
                raise ValueError("Invalid declared source/load headroom")
            (
                folder / "circuit.cir"
            ).write_text(f"""Qualified source-impedance startup and load-step corner
.lib "supply.lib" RC
Vsource source 0 PWL(0 0 1m {voltage:.12g})
Xrail source rail SUPPLY
Iload rail 0 PULSE(0 {self.load_a:.12g} 3m 1u 1u 2m 8m)
.control
tran 1u 7m
meas tran startup WHEN v(rail)={voltage * 0.9:.12g} RISE=1
meas tran loaded FIND v(rail) AT=4.5m
meas tran recovered FIND v(rail) AT=6.5m
quit
.endc
.end
""")
            approved = ModelFile(
                path="supply.lib",
                sha256=file_digest(model),
                sections=("RC",),
                license="Project-owned synthetic primitive circuit",
                approved_by="Explicit ideal-circuit workflow",
                evidence=self.evidence,
            )
            job = SimulationJob.model_validate(
                {
                    "netlist": "circuit.cir",
                    "description": "Source impedance corner",
                    "models": [approved.model_dump()],
                    "assumptions": [
                        "Ideal RC source model; no regulator topology equivalence",
                        self.evidence.model_dump_json(),
                    ],
                    "measurement_units": {"startup": "s", "loaded": "V", "recovered": "V"},
                    "assertions": {
                        "startup": {"min": 0.0008, "max": 0.0012, "unit": "s"},
                        "loaded": {"min": rail - 0.002, "max": rail + 0.002, "unit": "V"},
                        "recovered": {"min": voltage - 0.002, "max": voltage + 0.002, "unit": "V"},
                    },
                }
            )
            report = run_job(job, folder, folder / "simulation.log")
            checks.extend(
                r.model_copy(update={"check_id": f"power.{index}.{r.check_id}"})
                for r in report.results
            )
        return VerificationReport(results=tuple(checks))
