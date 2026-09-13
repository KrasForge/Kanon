# Engineering verification

M2 supplies deterministic checks over declared, evidence-backed engineering models.
The checks do not extract connectivity, geometry or datasheet values automatically.
A correct result over incorrect declared input is not board verification. Review the
input models against the frozen native design and manufacturer documents.

## BOM and supplier records

`astra-pcb check-bom bom.csv` imports canonical JSON or explicitly mapped CSV columns.
Grouped reference lists expand to individual rows; conflicting quantities, column
ambiguity, missing MPNs, duplicate references and contradictory value/package metadata
fail validation. Whitespace is normalized; part numbers are not rewritten or substituted.
`SupplierAdapter` accepts normalized optional MCP responses. `JLCSearch` performs real
credential-free HTTP lookup with bounded responses, exact code/MPN matching and safe
failure when offline. See [integration qualification](integrations.md). Lifecycle,
stock age and source diversity risks remain explicit, including unknown information.

## Evidence and electrical models

`datasheets.Registry` registers local document revision, manufacturer, components,
path and SHA-256. It refuses path escape, revision collisions and changed document
bytes. `SourcedLimit` compares an observation in explicit units against registered
constraints, preserving document citations. Registration proves file identity, not
that an extracted value is true. Human/independent review must check page, section,
conditions and transcription; PDF extraction is not implemented here.

`engineering.PowerTree` validates rail/load and sequencing dependency graphs, voltage
ranges and current budgets. Switching children propagate conservative input current
using declared minimum efficiency; linear children propagate output current and
quiescent demand. `check_regulator` checks input range, linear dropout and a first-order
worst-corner thermal estimate. No undocumented theta-JA is invented: missing parameters
or their applicable board conditions produce SKIP. Sequencing declarations are not
proof of measured startup waveforms. Unknown load corners require explicit resolution.

`engineering.fpga.check_banks` requires matching device/package family data, validates
physical pin-to-bank assignments, duplicate pins and compatible declared bank/I/O
voltages. Unknown standards produce SKIP. No device-family limits are hardcoded.
Dedicated/configuration pins, VREF and differential-pair constraints are M5 work.

`engineering.audits` checks declared local decoupling counts, effective capacitance
and optional distance; connector protection feature/net coverage; accessible test
points and probe clearance. Effective MLCC capacitance and requirements require
citations. Unknown required geometry/accessibility yields SKIP. These checks cannot
establish switching-loop inductance, ESD effectiveness or real return-path quality.

## Simulation

```sh
astra-pcb simulate examples/simulation/rc-filter.yaml --output artifacts/filter.log
astra-pcb simulate examples/simulation/power-transient.yaml --output artifacts/power.log
```

Output paths must be fresh. ngspice runs in a disposable directory with startup files
disabled, capturing exit status, logs, version and hashes. Only self-contained netlists
are currently accepted: flatten and review external model includes before running.
Control blocks admit analysis, scalar arithmetic and measurement commands; shell and
file commands are rejected. This restriction is not an OS sandbox for arbitrary
malicious simulator input; use isolated processes/containers for untrusted model corpora.

A zero process exit with an aborted analysis/error log is ERROR. Log warnings remain
WARN. Missing measurements are ERROR, failed numeric assertions FAIL, and skipped
assertions never PASS. Duplicate measurement names are rejected. Assertions declare
finite minimum and maximum bounds. The ideal RC filter and ideal supply-impedance
transient examples exercise actual ngspice; neither validates a real audio converter,
regulator stability, capacitor derating or manufacturing design.

Run `pytest -m integration` on a host with KiCad and ngspice. CI's Fedora integration
job supplies both. Offline unit tests exercise contract failures; live supplier lookup
is opt-in through the CLI and never required by CI.
