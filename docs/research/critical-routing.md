# Critical-net routing research (#46)

Decision: use agent decisions for constraints, floorplanning and routing order, and keep
native routing plus independent readback/DRC as the geometric execution boundary. There
is no evidence from this initialization that an LLM router outperforms KiCad's router or
a general autorouter on finished-board quality.

The [KiCad 10 PCB editor documentation](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html)
describes interactive shove/walk-around behavior, differential pairs and length tuning.
These operations address geometry that a simple coordinate trace-insertion tool does
not. Qualifying the external MCP's `route_trace` showed persistence of a requested segment;
independent DRC then reported its intentionally dangling end. This is evidence for a
write/readback/check contract, not automatic route completion or constraint satisfaction.

Prioritize short sensitive feedback/switching loops, reference distribution, analog
inputs, clocks, differential pairs and power routes before ordinary control wiring.
The objective differs by net class: matching length alone cannot establish controlled
impedance, return continuity, switching-loop inductance, thermal current capacity or
analog noise performance. Agent-generated ordering should be reviewed alongside placement
and stackup before mutations. Never change I/O voltages or stackup to make a route fit.

A controlled benchmark should freeze board, component positions, rules, stackup, tool
versions and time budget; compare native interactive routing, general autorouting and
agent-directed native operations. Record completion, DRC, critical-net review findings,
via/layer changes, skew, reroute churn, changes to previously approved nets and runtime.
Use held-out designs with obstacles and return-plane discontinuities. Keep failed runs.
A higher completion fraction or lower trace length alone is not an engineering win.

Next qualification targets are pad-to-pad routing, via transitions, differential-pair
routing and undo/readback semantics on populated boards. Server-advertised capability
counts are not evidence. This research establishes the evaluation and execution boundary;
it deliberately does not ship an unqualified autonomous critical-net routing algorithm.
