# Release gate

Deterministic tooling, not an LLM role. Follow AGENTS.md and config/release-gates.yaml.

## Required authority

Execute independent ERC/DRC, parity where available, BOM/footprint checks, applicable
simulations and policy checks. Require current independent architecture, schematic,
power, critical-net, mechanical, DFM and final reviews. Only a signed human waiver
accepted by explicit per-gate policy may override failure. No private signing key belongs
in the agent environment.

## Release transaction to implement

Freeze source/config/library/model identity; run mandatory checks; stop on failure or
missing evidence; generate manufacturing exports in a fresh directory; check artifact
completeness; hash a manifest and produce the final release report. No upload/order step.
Detect any source changes during the transaction and invalidate the result.

Current code only aggregates supplied results conservatively. Manual gates require signed independent approvals.
The release CLI still errors because the release transaction and artifact validation are
unfinished. Supplied JSON PASS values are not authenticated release evidence.
