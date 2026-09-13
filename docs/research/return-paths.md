# Return-path analysis research (#45)

Decision: treat geometric checks as counterexample detectors and evidence for review,
not a binary proof of electromagnetic correctness. A nearby GND object is insufficient.
A useful analysis needs the routed segment, the adjacent reference plane geometry,
voids/antipads, layer transitions, stitching paths, stackup and the relevant edge spectrum.

The reproducible `research/return_path_probe.py` compares three synthetic grid planes.
Both signal endpoints lie over copper in every case. The continuous plane has a
16-step path; a partial slot forces a 24-step detour; a full slot disconnects the two
regions. `return-path-probe.json` contains the measurements. This demonstrates a failure
of endpoint/nearby-ground heuristics. Grid path length is not current density, impedance,
loop inductance or radiation, and the chosen grid is not a production field solver.

TI's [high-speed interface guidance](https://www.ti.com/lit/an/spma056/spma056.pdf)
discusses avoiding reference-plane discontinuities beneath high-speed signals.
[High-speed layout guidance](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf) also treats
return paths and functional placement. The implementation should preserve plane continuity
and reason about where currents close, without prescribing arbitrary analog/digital splits.

Candidate pipeline: read saved filled-zone polygons and layer adjacency; project each
critical route onto its actual reference plane; detect crossing of voids/disconnected
copper; inspect return-transfer structures at vias; report affected native UUIDs and a
geometric overlay. Respect fill freshness and net identity. A coarse corridor can nominate
regions for review but cannot certify an entire net, especially across power references,
frequency-dependent capacitive paths or connector/cable returns.

Evaluate against continuous-plane, slot, neck, isolated-pour, layer-change, stitching-via,
connector and mixed-signal cases at multiple resolutions. Compare nominated problems
with field-solver or measured reference cases before deriving quantitative thresholds.
No release-gate implementation is exposed for return paths yet: unresolved geometry,
frequency or reference selection must remain unknown. The current mandatory critical-net
review remains independent and evidence-backed.
