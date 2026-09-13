# Advanced engineering contracts

The M5 modules validate declared engineering facts. They do not extract a complete
physical/electrical model from an arbitrary board. Every reported PASS is limited to
its named check, input assumptions and cited rule set.

`engineering.audio.AudioChain` uses loaded voltage gains and sine-equivalent RMS levels.
It propagates nominal and maximum signals, checks ADC/DAC and stage full-scale envelopes,
headroom, and balanced/unbalanced interface declarations. The caller must account for
loading, DC offsets, frequency dependence and crest factor in the declared limits.
`NoiseBudget` computes first-order Johnson, white amplifier and integrated converter noise
using output gains, equivalent noise bandwidth and root-sum-square combination. Correlated
sources are rejected; 1/f spectra and frequency-dependent transfer functions are not inferred.
`OpAmpEnvelope` checks supply/common-mode/output/GBW constraints and cited minimum stable
gain/capacitive load limits. Unknown stability data is SKIP; it is not a loop-gain solver.

`engineering.fpga_device.DeviceRules` extends the bank adapter with physical pin functions,
clock capability, reciprocal differential partners, VREF requirements, configuration pins,
boot interfaces/straps/qualified flash MPNs, sequencing and device-specific decoupling.
No real vendor-family database is bundled. Rules must be reviewed against the exact
part/package/revision. Rail timing observations distinguish power-up and power-down;
supply separate ordered rules for each direction. Never assume reverse sequencing is valid.
Missing timing/rule information or a device-rule citation is SKIP. Declared boot compatibility does not test hardware.

`engineering.clocks.ClockTree` validates a graph and checks declared ratios, fanout,
termination, jitter budgets and domain changes. It does not establish timing closure or
clock-domain crossing correctness. `bom.alternates.Alternate` requires separate evidence
for pinout, electrical, footprint, thermal, firmware, assembly and lifecycle compatibility.
It never substitutes parts. `agents.change_plan.ChangePlan` records intended operations,
affected objects, checks, risks and rollback artifacts. Explicit-user-intent text must
come from the trusted harness; a model filling that field cannot authorize itself.

## Geometry and visual artifacts

Install `uv sync --extra dev --extra visual --extra geometry` for optional Gerbonara and
OpenCascade dependencies. `mechanical.collision.check_collision` reads two immutable STEP
solids in an explicitly evidenced shared coordinate frame. It measures actual boolean
intersection volume and minimum separation in millimetres in a bounded worker. Invalid
or surface-only models cannot prove collision freedom. The test uses overlapping and
separated solids with known 500 mm³ overlap and 2 mm clearance. Geometry completeness,
connector mating space, cable bends and tolerances still require review. FreeCAD remains
an optional unqualified integration; OpenCascade is the qualified geometry backend here.

`kicad.visual.render_board` generates top, bottom and isometric PNGs using KiCad 10 and
records hashes/source receipts. Manufacturing Gerber rendering uses explicit Gerbonara
layer mappings. Artifact-generation PASS is not visual approval. Use the
[visual rubric](../skills/pcb-red-team/references/visual-review.md) and retain view/layer/
revision identity. Empty native fixtures qualify the tool path, not populated-board quality.

See the [verifier MCP API](pcb-verifier.md) for check schemas and the bounded CLI. The
[PDF ingestion](research/datasheet-ingestion.md), [return-path](research/return-paths.md)
and [critical-routing](research/critical-routing.md) research reports document observed
failure modes, source citations, practical approaches and remaining experiments.
