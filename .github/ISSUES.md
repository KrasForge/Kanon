# Complete initialization backlog

Published to KrasForge/Kanon: 76 leaf issues and six milestone trackers. All remain open and unassigned. Native sub-issue/dependency relationships were read back and verified. Initial implementations do not satisfy every issue acceptance criterion.

- **M0 – Foundation** — tracker [#77](https://github.com/KrasForge/Kanon/issues/77); #1, #2, #3, #4, #5, #6, #69, #74, #75
- **M1 – KiCad Closed Loop** — tracker [#78](https://github.com/KrasForge/Kanon/issues/78); #7, #8, #9, #10, #11, #12, #13, #14, #70
- **M2 – Engineering Verification** — tracker [#79](https://github.com/KrasForge/Kanon/issues/79); #15, #16, #17, #18, #19, #21, #22, #23, #24, #25, #26, #28, #29, #30, #31, #32, #33, #34, #71, #72
- **M3 – Agentic PCB Designer** — tracker [#80](https://github.com/KrasForge/Kanon/issues/80); #36, #37, #38, #39, #40, #41, #43, #44
- **M4 – Manufacturing Release** — tracker [#81](https://github.com/KrasForge/Kanon/issues/81); #47, #48, #49, #51, #52, #53, #54, #55, #56, #73, #76
- **M5 – Advanced Engineering** — tracker [#82](https://github.com/KrasForge/Kanon/issues/82); #20, #27, #35, #42, #45, #46, #50, #57, #58, #59, #60, #61, #62, #63, #64, #65, #66, #67, #68

## [#1: P0 — Define canonical PCB design specification schema](https://github.com/KrasForge/Kanon/issues/1)

Milestone: M0 – Foundation

Labels: priority:P0, type:feature

## Motivation

Define canonical PCB design specification schema is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate complete project metadata, functional requirements, interfaces, inputs/rails, clocks, devices/FPGA, audio, environment, mechanical/manufacturing constraints, sourcing, cost, tests, forbidden parts/packages and debug; add version migration and semantic cross-reference/unit/range validation beyond initial structural schema.

## Acceptance criteria

- [ ] Validate complete project metadata, functional requirements, interfaces, inputs/rails, clocks, devices/FPGA, audio, environment, mechanical/manufacturing constraints, sourcing, cost, tests, forbidden parts/packages and debug; add version migration and semantic cross-reference/unit/range validation beyond initial structural schema.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- No prerequisite implementation issue.

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#2: P0 — Implement verification result and report model](https://github.com/KrasForge/Kanon/issues/2)

Milestone: M0 – Foundation

Labels: priority:P0, area:verification, type:feature

## Motivation

Implement verification result and report model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Harden typed PASS/FAIL/WARN/SKIP/ERROR, severity, evidence, affected objects, remediation and source; add report identity, schema evolution and round-trip compatibility fixtures to the initial model.

## Acceptance criteria

- [ ] Harden typed PASS/FAIL/WARN/SKIP/ERROR, severity, evidence, affected objects, remediation and source; add report identity, schema evolution and round-trip compatibility fixtures to the initial model.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- No prerequisite implementation issue.

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#3: P0 — Implement configurable release-gate engine](https://github.com/KrasForge/Kanon/issues/3)

Milestone: M0 – Foundation

Labels: priority:P0, area:verification, type:feature

## Motivation

Implement configurable release-gate engine is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Extend current conservative aggregation with validated policy, revision-bound evidence, authenticated manual approvals and explicit human waiver audit; missing mandatory evidence must block and no LLM override is accepted.

## Acceptance criteria

- [ ] Extend current conservative aggregation with validated policy, revision-bound evidence, authenticated manual approvals and explicit human waiver audit; missing mandatory evidence must block and no LLM override is accepted.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#4: P0 — Implement environment diagnostics](https://github.com/KrasForge/Kanon/issues/4)

Milestone: M0 – Foundation

Labels: priority:P0, type:feature

## Motivation

Implement environment diagnostics is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Qualify Python, KiCad CLI, ngspice and Git versions; distinguish configured MCP endpoints from successful protocol handshakes and report optional FreeCAD accurately without exposing secrets.

## Acceptance criteria

- [ ] Qualify Python, KiCad CLI, ngspice and Git versions; distinguish configured MCP endpoints from successful protocol handshakes and report optional FreeCAD accurately without exposing secrets.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#5: P1 — Define engineering decision record model](https://github.com/KrasForge/Kanon/issues/5)

Milestone: M0 – Foundation

Labels: priority:P1, type:feature

## Motivation

Define engineering decision record model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Align machine-readable and Markdown hardware decisions with alternatives, evidence, calculations, risks, chosen solution, consequences and invalidation conditions; validate links and round-trip without losing information.

## Acceptance criteria

- [ ] Align machine-readable and Markdown hardware decisions with alternatives, evidence, calculations, risks, chosen solution, consequences and invalidation conditions; validate links and round-trip without losing information.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#6: P1 — Define structured engineering review/finding schema](https://github.com/KrasForge/Kanon/issues/6)

Milestone: M0 – Foundation

Labels: priority:P1, area:verification, type:feature

## Motivation

Define structured engineering review/finding schema is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Version blocker/major/minor/observation findings with stable IDs, source hashes, affected objects, evidence and resolution status; reject invalid transitions and preserve review limitations.

## Acceptance criteria

- [ ] Version blocker/major/minor/observation findings with stable IDs, source hashes, affected objects, evidence and resolution status; reject invalid transitions and preserve review limitations.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#7: P0 — Implement robust `kicad-cli` adapter](https://github.com/KrasForge/Kanon/issues/7)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:kicad, type:integration

## Motivation

Implement robust `kicad-cli` adapter is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Qualify initial command hooks against KiCad 10; preserve diagnostics including timeout output, validate inputs/version, isolate output directories and capture exact artifacts with hashes and tool identity.

## Acceptance criteria

- [ ] Qualify initial command hooks against KiCad 10; preserve diagnostics including timeout output, validate inputs/version, isolate output directories and capture exact artifacts with hashes and tool identity.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model
- #4: P0 — Implement environment diagnostics

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#8: P0 — Implement schematic ERC verification](https://github.com/KrasForge/Kanon/issues/8)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:kicad, area:verification, type:integration

## Motivation

Implement schematic ERC verification is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Invoke independent KiCad ERC and parse actual JSON sheets/violations into structured results; distinguish warnings, exclusions, violations, tool errors and malformed/missing output.

## Acceptance criteria

- [ ] Invoke independent KiCad ERC and parse actual JSON sheets/violations into structured results; distinguish warnings, exclusions, violations, tool errors and malformed/missing output.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #7: P0 — Implement robust `kicad-cli` adapter
- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#9: P0 — Implement PCB DRC verification](https://github.com/KrasForge/Kanon/issues/9)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:kicad, area:verification, type:integration

## Motivation

Implement PCB DRC verification is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Run DRC from persisted PCB independently of MCP; interpret violations and unconnected items, document zone-fill behavior and schematic parity availability without mutating reviewer input.

## Acceptance criteria

- [ ] Run DRC from persisted PCB independently of MCP; interpret violations and unconnected items, document zone-fill behavior and schematic parity availability without mutating reviewer input.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #7: P0 — Implement robust `kicad-cli` adapter
- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#10: P0 — Implement deterministic manufacturing exports](https://github.com/KrasForge/Kanon/issues/10)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:kicad, area:manufacturing, type:integration

## Motivation

Implement deterministic manufacturing exports is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Generate Gerbers, drills and STEP in fresh output directories; capture tool/version/exit output and verify expected artifacts with hashes, rejecting stale or incomplete results.

## Acceptance criteria

- [ ] Generate Gerbers, drills and STEP in fresh output directories; capture tool/version/exit output and verify expected artifacts with hashes, rejecting stale or incomplete results.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #7: P0 — Implement robust `kicad-cli` adapter

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#11: P0 — Define KiCad MCP abstraction boundary](https://github.com/KrasForge/Kanon/issues/11)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:kicad, area:mcp, type:feature

## Motivation

Define KiCad MCP abstraction boundary is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Implement selectable server adapters with explicit READ/WRITE capability mappings, deny unknown tools and test protocol/error behavior; keep IPC optional and avoid provider-specific core assumptions.

## Acceptance criteria

- [ ] Implement selectable server adapters with explicit READ/WRITE capability mappings, deny unknown tools and test protocol/error behavior; keep IPC optional and avoid provider-specific core assumptions.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #4: P0 — Implement environment diagnostics

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#12: P0 — Enforce read-only reviewer tool policy](https://github.com/KrasForge/Kanon/issues/12)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P0, area:agents, area:mcp, type:feature

## Motivation

Enforce read-only reviewer tool policy is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Enforce absence of mutation-capable KiCad tools, shell and write mounts in runtime; fail startup for unclassified tools or unsafe proxy access, using separate reviewer credentials/snapshots.

## Acceptance criteria

- [ ] Enforce absence of mutation-capable KiCad tools, shell and write mounts in runtime; fail startup for unclassified tools or unsafe proxy access, using separate reviewer credentials/snapshots.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #11: P0 — Define KiCad MCP abstraction boundary

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#13: P1 — Implement board/schematic state snapshot abstraction](https://github.com/KrasForge/Kanon/issues/13)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P1, area:kicad, type:feature

## Motivation

Implement board/schematic state snapshot abstraction is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Capture connectivity, symbols, footprints, pads, routes, zones, stackup and provenance from saved state; produce stable content hashes/diffs and invalidate evidence on relevant changes.

## Acceptance criteria

- [ ] Capture connectivity, symbols, footprints, pads, routes, zones, stackup and provenance from saved state; produce stable content hashes/diffs and invalidate evidence on relevant changes.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #7: P0 — Implement robust `kicad-cli` adapter
- #11: P0 — Define KiCad MCP abstraction boundary

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#14: P1 — Add design mutation → verify workflow](https://github.com/KrasForge/Kanon/issues/14)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P1, area:kicad, area:verification, type:feature

## Motivation

Add design mutation → verify workflow is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Persist mutation, read back state, run applicable ERC/DRC, emit structured report and invalidate old approvals; stop on failed persistence, verification or mismatched state.

## Acceptance criteria

- [ ] Persist mutation, read back state, run applicable ERC/DRC, emit structured report and invalidate old approvals; stop on failed persistence, verification or mismatched state.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #8: P0 — Implement schematic ERC verification
- #9: P0 — Implement PCB DRC verification
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#15: P0 — Implement canonical BOM model and importer](https://github.com/KrasForge/Kanon/issues/15)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:bom, type:feature

## Motivation

Implement canonical BOM model and importer is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Extend initial per-reference model with validated CSV/KiCad import, quantity/reference semantics, manufacturer/MPN, supplier number, package, lifecycle, stock, currency/cost, assembly class and alternates; preserve unknowns.

## Acceptance criteria

- [ ] Extend initial per-reference model with validated CSV/KiCad import, quantity/reference semantics, manufacturer/MPN, supplier number, package, lifecycle, stock, currency/cost, assembly class and alternates; preserve unknowns.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#16: P0 — Validate manufacturer part-number completeness](https://github.com/KrasForge/Kanon/issues/16)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:bom, area:verification, type:feature

## Motivation

Validate manufacturer part-number completeness is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Extend initial missing-MPN checks to ambiguous ordering suffixes and policy-controlled non-populated/mechanical exclusions; identify affected references and evidence without guessing parts.

## Acceptance criteria

- [ ] Extend initial missing-MPN checks to ambiguous ordering suffixes and policy-controlled non-populated/mechanical exclusions; identify affected references and evidence without guessing parts.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #15: P0 — Implement canonical BOM model and importer
- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#17: P1 — Implement BOM normalization and inconsistency checks](https://github.com/KrasForge/Kanon/issues/17)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:bom, type:feature

## Motivation

Implement BOM normalization and inconsistency checks is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Normalize declared metadata without corrupting case-sensitive MPNs; detect conflicting values/packages/manufacturers and duplicate references with actionable diagnostics and provenance.

## Acceptance criteria

- [ ] Normalize declared metadata without corrupting case-sensitive MPNs; detect conflicting values/packages/manufacturers and duplicate references with actionable diagnostics and provenance.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #15: P0 — Implement canonical BOM model and importer

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#18: P1 — Add JLCPCB/LCSC sourcing adapter](https://github.com/KrasForge/Kanon/issues/18)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:bom, area:mcp, type:integration

## Motivation

Add JLCPCB/LCSC sourcing adapter is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Optional live adapter exposes timestamped stock, currency/quantity price, LCSC number, package and Basic/Extended status when available; offline/unconfigured/rate-limited states never fabricate data.

## Acceptance criteria

- [ ] Optional live adapter exposes timestamped stock, currency/quantity price, LCSC number, package and Basic/Extended status when available; offline/unconfigured/rate-limited states never fabricate data.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #15: P0 — Implement canonical BOM model and importer
- #11: P0 — Define KiCad MCP abstraction boundary

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#19: P1 — Add part lifecycle and sourcing-risk model](https://github.com/KrasForge/Kanon/issues/19)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:bom, type:feature

## Motivation

Add part lifecycle and sourcing-risk model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent lifecycle, stock age, sole-source risk and evidence provenance with transparent policy scoring; unknown data remains explicit and manufacturer lifecycle outranks unsupported inference.

## Acceptance criteria

- [ ] Represent lifecycle, stock age, sole-source risk and evidence provenance with transparent policy scoring; unknown data remains explicit and manufacturer lifecycle outranks unsupported inference.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #15: P0 — Implement canonical BOM model and importer
- #18: P1 — Add JLCPCB/LCSC sourcing adapter

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#20: P2 — Implement alternate-part compatibility representation](https://github.com/KrasForge/Kanon/issues/20)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:bom, type:feature

## Motivation

Implement alternate-part compatibility representation is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent electrical, pinout, package, timing, thermal, firmware and assembly differences plus qualification evidence; matching value/package never implies automatic interchangeability.

## Acceptance criteria

- [ ] Represent electrical, pinout, package, timing, thermal, firmware and assembly differences plus qualification evidence; matching value/package never implies automatic interchangeability.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #15: P0 — Implement canonical BOM model and importer
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#21: P0 — Implement FPGA bank-voltage validator](https://github.com/KrasForge/Kanon/issues/21)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:verification, type:feature

## Motivation

Implement FPGA bank-voltage validator is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate declared bank supply versus device-specific I/O standard voltage requirements; detect conflicting assignments, unknown standards and missing bank evidence without silently changing voltages.

## Acceptance criteria

- [ ] Validate declared bank supply versus device-specific I/O standard voltage requirements; detect conflicting assignments, unknown standards and missing bank evidence without silently changing voltages.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#22: P0 — Implement power-tree model](https://github.com/KrasForge/Kanon/issues/22)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:verification, type:feature

## Motivation

Implement power-tree model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Model sources, regulators, rails, loads, expected and peak currents, dependencies and sequencing; reject cycles, duplicate rails, invalid ranges and dangling supply references.

## Acceptance criteria

- [ ] Model sources, regulators, rails, loads, expected and peak currents, dependencies and sequencing; reject cycles, duplicate rails, invalid ranges and dangling supply references.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#23: P1 — Implement regulator power/thermal calculation checks](https://github.com/KrasForge/Kanon/issues/23)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement regulator power/thermal calculation checks is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Compute input/output/load corners, dissipation, evidence-backed efficiency and thermal margin with explicit units; missing package thermal parameters produce unresolved results, never invented estimates.

## Acceptance criteria

- [ ] Compute input/output/load corners, dissipation, evidence-backed efficiency and thermal margin with explicit units; missing package thermal parameters produce unresolved results, never invented estimates.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #22: P0 — Implement power-tree model
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#24: P1 — Implement decoupling audit framework](https://github.com/KrasForge/Kanon/issues/24)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement decoupling audit framework is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Associate IC power pins/rails with evidence-backed local decoupling rules; flag missing coverage and unresolved data, separating schematic rules from geometric/electromagnetic claims.

## Acceptance criteria

- [ ] Associate IC power pins/rails with evidence-backed local decoupling rules; flag missing coverage and unresolved data, separating schematic rules from geometric/electromagnetic claims.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#25: P1 — Implement connector protection audit](https://github.com/KrasForge/Kanon/issues/25)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement connector protection audit is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent ESD, overvoltage, current limiting and termination expectations per interface; trace protection strategy to connector nets and report unsupported applicability.

## Acceptance criteria

- [ ] Represent ESD, overvoltage, current limiting and termination expectations per interface; trace protection strategy to connector nets and report unsupported applicability.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #13: P1 — Implement board/schematic state snapshot abstraction
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#26: P1 — Implement test-point coverage audit](https://github.com/KrasForge/Kanon/issues/26)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement test-point coverage audit is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate project-required rails/signals against accessible test points and declared probe constraints; distinguish missing point from unverified physical accessibility.

## Acceptance criteria

- [ ] Validate project-required rails/signals against accessible test points and declared probe constraints; distinguish missing point from unverified physical accessibility.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#27: P2 — Implement clock-topology checker](https://github.com/KrasForge/Kanon/issues/27)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:verification, type:feature

## Motivation

Implement clock-topology checker is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate sources/destinations, frequencies, clock domains, expected termination and documented fanout rules; detect unresolved clock references without pretending to calculate signal integrity.

## Acceptance criteria

- [ ] Validate sources/destinations, frequencies, clock domains, expected termination and documented fanout rules; detect unresolved clock references without pretending to calculate signal integrity.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #13: P1 — Implement board/schematic state snapshot abstraction
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#28: P0 — Implement ngspice process adapter](https://github.com/KrasForge/Kanon/issues/28)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:simulation, type:integration

## Motivation

Implement ngspice process adapter is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Qualify initial batch adapter with real ngspice fixtures, timeouts, model include resolution, diagnostics and artifact identity; failed simulations must not yield passing assertions.

## Acceptance criteria

- [ ] Qualify initial batch adapter with real ngspice fixtures, timeouts, model include resolution, diagnostics and artifact identity; failed simulations must not yield passing assertions.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model
- #4: P0 — Implement environment diagnostics

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#29: P1 — Add declarative simulation assertions](https://github.com/KrasForge/Kanon/issues/29)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:simulation, type:feature

## Motivation

Add declarative simulation assertions is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate named measurements with min/max ranges such as gain_db 5.8–6.2 and cutoff_hz 19500–20500; define units, missing/nonfinite handling and link assertions to successful simulation inputs.

## Acceptance criteria

- [ ] Validate named measurements with min/max ranges such as gain_db 5.8–6.2 and cutoff_hz 19500–20500; define units, missing/nonfinite handling and link assertions to successful simulation inputs.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #28: P0 — Implement ngspice process adapter
- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#30: P1 — Add audio filter simulation workflow](https://github.com/KrasForge/Kanon/issues/30)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:simulation, type:feature

## Motivation

Add audio filter simulation workflow is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Provide reproducible representative anti-alias/reconstruction circuits with source/load impedances, corners, gain/cutoff assertions and documented model validity limits.

## Acceptance criteria

- [ ] Provide reproducible representative anti-alias/reconstruction circuits with source/load impedances, corners, gain/cutoff assertions and documented model validity limits.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #28: P0 — Implement ngspice process adapter
- #29: P1 — Add declarative simulation assertions

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#31: P1 — Add power-circuit simulation workflow](https://github.com/KrasForge/Kanon/issues/31)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:simulation, type:feature

## Motivation

Add power-circuit simulation workflow is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Add reusable power-circuit harness with approved models, startup/load-transient assertions and limitations; reject unavailable models and avoid assuming regulator topologies are SPICE-equivalent.

## Acceptance criteria

- [ ] Add reusable power-circuit harness with approved models, startup/load-transient assertions and limitations; reject unavailable models and avoid assuming regulator topologies are SPICE-equivalent.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #28: P0 — Implement ngspice process adapter
- #29: P1 — Add declarative simulation assertions
- #22: P0 — Implement power-tree model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#32: P0 — Implement datasheet evidence model](https://github.com/KrasForge/Kanon/issues/32)

Milestone: M2 – Engineering Verification

Labels: priority:P0, area:datasheets, type:feature

## Motivation

Implement datasheet evidence model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Harden current document/manufacturer/revision/page/section/constraint/source identity with content hash and serialization compatibility; validate exact locators and distinguish extracted claims from verified limits.

## Acceptance criteria

- [ ] Harden current document/manufacturer/revision/page/section/constraint/source identity with content hash and serialization compatibility; validate exact locators and distinguish extracted claims from verified limits.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#33: P1 — Build local datasheet registry](https://github.com/KrasForge/Kanon/issues/33)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:datasheets, type:feature

## Motivation

Build local datasheet registry is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Index component, manufacturer, document revision, local path, content hash and canonical URL; detect stale/missing/duplicate documents and preserve redistribution restrictions.

## Acceptance criteria

- [ ] Index component, manufacturer, document revision, local path, content hash and canonical URL; detect stale/missing/duplicate documents and preserve redistribution restrictions.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #32: P0 — Implement datasheet evidence model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#34: P1 — Associate verified constraints with evidence](https://github.com/KrasForge/Kanon/issues/34)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:datasheets, area:verification, type:feature

## Motivation

Associate verified constraints with evidence is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Bind numerical limits and applicability/corners to revision/page/section evidence; checks report the rule source and become unresolved when evidence is missing or invalidated.

## Acceptance criteria

- [ ] Bind numerical limits and applicability/corners to revision/page/section evidence; checks report the rule source and become unresolved when evidence is missing or invalidated.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #32: P0 — Implement datasheet evidence model
- #33: P1 — Build local datasheet registry

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#35: P2 — Research reliable datasheet ingestion/extraction pipeline](https://github.com/KrasForge/Kanon/issues/35)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:datasheets, type:research

## Motivation

Research reliable datasheet ingestion/extraction pipeline is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Evaluate representative PDFs, tables, scanned pages, structured citations and revision changes using an annotated corpus; publish extraction accuracy/error taxonomy and go/no-go recommendation, not an OCR-only production claim.

## Acceptance criteria

- [ ] Evaluate representative PDFs, tables, scanned pages, structured citations and revision changes using an annotated corpus; publish extraction accuracy/error taxonomy and go/no-go recommendation, not an OCR-only production claim.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Use a documented evaluation corpus, baselines and counterexamples; publish reproducible results, failure cases and a justified recommendation.

## Dependencies

- #33: P1 — Build local datasheet registry

## Non-goals

No production integration is implied by research results.

Milestone tracker: #82


## [#36: P0 — Implement design lifecycle state machine](https://github.com/KrasForge/Kanon/issues/36)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P0, area:agents, type:feature

## Motivation

Implement design lifecycle state machine is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Enforce SPEC→ARCHITECTURE→COMPONENT_SELECTION→SCHEMATIC→SCHEMATIC_REVIEW→FLOORPLAN→CRITICAL_ROUTING→GENERAL_ROUTING→PCB_REVIEW→DFM→MECHANICAL→RELEASE_REVIEW→RELEASED with gate prerequisites and invalidation on edits.

## Acceptance criteria

- [ ] Enforce SPEC→ARCHITECTURE→COMPONENT_SELECTION→SCHEMATIC→SCHEMATIC_REVIEW→FLOORPLAN→CRITICAL_ROUTING→GENERAL_ROUTING→PCB_REVIEW→DFM→MECHANICAL→RELEASE_REVIEW→RELEASED with gate prerequisites and invalidation on edits.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #3: P0 — Implement configurable release-gate engine
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#37: P0 — Implement Architect/Designer/Reviewer role definitions](https://github.com/KrasForge/Kanon/issues/37)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P0, area:agents, type:feature

## Motivation

Implement Architect/Designer/Reviewer role definitions is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Load and validate machine-readable model/tool capability contracts; architect plans, designer edits, reviewer has no mutations, deterministic release has no model authority; configuration alone is insufficient.

## Acceptance criteria

- [ ] Load and validate machine-readable model/tool capability contracts; architect plans, designer edits, reviewer has no mutations, deterministic release has no model authority; configuration alone is insufficient.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #11: P0 — Define KiCad MCP abstraction boundary
- #12: P0 — Enforce read-only reviewer tool policy

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#38: P0 — Implement independent reviewer workflow](https://github.com/KrasForge/Kanon/issues/38)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P0, area:agents, area:verification, type:feature

## Motivation

Implement independent reviewer workflow is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Supply a frozen design snapshot and evidence to an isolated reviewer; emit structured adversarial findings, track identity/scope and never approve solely because ERC/DRC pass.

## Acceptance criteria

- [ ] Supply a frozen design snapshot and evidence to an isolated reviewer; emit structured adversarial findings, track identity/scope and never approve solely because ERC/DRC pass.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #6: P1 — Define structured engineering review/finding schema
- #12: P0 — Enforce read-only reviewer tool policy
- #13: P1 — Implement board/schematic state snapshot abstraction
- #37: P0 — Implement Architect/Designer/Reviewer role definitions

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#39: P1 — Implement review → remediation loop](https://github.com/KrasForge/Kanon/issues/39)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P1, area:agents, type:feature

## Motivation

Implement review → remediation loop is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Designer consumes stable finding IDs, records changes and re-verifies, then independent reviewer rechecks resolution; preserve iteration history and stop on repeated unresolved blockers.

## Acceptance criteria

- [ ] Designer consumes stable finding IDs, records changes and re-verifies, then independent reviewer rechecks resolution; preserve iteration history and stop on repeated unresolved blockers.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #14: P1 — Add design mutation → verify workflow
- #38: P0 — Implement independent reviewer workflow

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#40: P1 — Add critical-net classification](https://github.com/KrasForge/Kanon/issues/40)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P1, area:agents, area:kicad, type:feature

## Motivation

Add critical-net classification is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent power, clock, differential, high-speed, analog input/output, reference, switch-node, feedback, ordinary digital and control classes with explicit rationale and overrides.

## Acceptance criteria

- [ ] Represent power, clock, differential, high-speed, analog input/output, reference, switch-node, feedback, ordinary digital and control classes with explicit rationale and overrides.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#41: P1 — Enforce critical-net review before release](https://github.com/KrasForge/Kanon/issues/41)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P1, area:verification, type:feature

## Motivation

Enforce critical-net review before release is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Require class-appropriate review evidence for each critical net, tied to current geometry/connectivity and constraints; missing or stale class reviews block release.

## Acceptance criteria

- [ ] Require class-appropriate review evidence for each critical net, tied to current geometry/connectivity and constraints; missing or stale class reviews block release.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #40: P1 — Add critical-net classification
- #38: P0 — Implement independent reviewer workflow
- #3: P0 — Implement configurable release-gate engine

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#42: P2 — Add engineering change-plan representation](https://github.com/KrasForge/Kanon/issues/42)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:agents, type:feature

## Motivation

Add engineering change-plan representation is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent planned large mutations, affected objects, rationale, anticipated checks and rollback considerations; bind plan to starting snapshot and identify scope deviations.

## Acceptance criteria

- [ ] Represent planned large mutations, affected objects, rationale, anticipated checks and rollback considerations; bind plan to starting snapshot and identify scope deviations.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #36: P0 — Implement design lifecycle state machine

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#43: P1 — Define PCB floorplanning model](https://github.com/KrasForge/Kanon/issues/43)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P1, area:kicad, type:feature

## Motivation

Define PCB floorplanning model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent approximate power, FPGA/MCU, converter, analog input/output, connector, memory and clock regions plus hard/soft constraints and mechanical anchors.

## Acceptance criteria

- [ ] Represent approximate power, FPGA/MCU, converter, analog input/output, connector, memory and clock regions plus hard/soft constraints and mechanical anchors.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#44: P1 — Implement placement-rule checks](https://github.com/KrasForge/Kanon/issues/44)

Milestone: M3 – Agentic PCB Designer

Labels: priority:P1, area:kicad, area:verification, type:feature

## Motivation

Implement placement-rule checks is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Quantify declared decoupling distance, connector-to-edge, crystal proximity, switching-loop component and feedback-network locality rules; define units/geometry and mark unsupported analyses unresolved.

## Acceptance criteria

- [ ] Quantify declared decoupling distance, connector-to-edge, crystal proximity, switching-loop component and feedback-network locality rules; define units/geometry and mark unsupported analyses unresolved.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #24: P1 — Implement decoupling audit framework
- #43: P1 — Define PCB floorplanning model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #80


## [#45: P2 — Research return-path analysis](https://github.com/KrasForge/Kanon/issues/45)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:kicad, type:research

## Motivation

Research return-path analysis is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Evaluate board/plane geometry, reference transitions and frequency-dependent return-path methods against counterexamples; publish feasibility and limits beyond simplistic ground-nearby heuristics.

## Acceptance criteria

- [ ] Evaluate board/plane geometry, reference transitions and frequency-dependent return-path methods against counterexamples; publish feasibility and limits beyond simplistic ground-nearby heuristics.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Use a documented evaluation corpus, baselines and counterexamples; publish reproducible results, failure cases and a justified recommendation.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #40: P1 — Add critical-net classification

## Non-goals

No production integration is implied by research results.

Milestone tracker: #82


## [#46: P2 — Research automatic critical-net routing strategies](https://github.com/KrasForge/Kanon/issues/46)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:kicad, type:research

## Motivation

Research automatic critical-net routing strategies is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Compare agent-directed and general routing on clocks, analog, power, switch nodes, feedback and differential pairs using reproducible boards and electrical/geometric metrics.

## Acceptance criteria

- [ ] Compare agent-directed and general routing on clocks, analog, power, switch nodes, feedback and differential pairs using reproducible boards and electrical/geometric metrics.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Use a documented evaluation corpus, baselines and counterexamples; publish reproducible results, failure cases and a justified recommendation.

## Dependencies

- #14: P1 — Add design mutation → verify workflow
- #40: P1 — Add critical-net classification
- #43: P1 — Define PCB floorplanning model

## Non-goals

No production integration is implied by research results.

Milestone tracker: #82


## [#47: P1 — Implement STEP-export verification pipeline](https://github.com/KrasForge/Kanon/issues/47)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:mechanical, area:kicad, type:integration

## Motivation

Implement STEP-export verification pipeline is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Confirm STEP is newly generated, nonempty and associated with current design/model revision; record missing 3D models and units/origin limitations instead of claiming full mechanical fidelity.

## Acceptance criteria

- [ ] Confirm STEP is newly generated, nonempty and associated with current design/model revision; record missing 3D models and units/origin limitations instead of claiming full mechanical fidelity.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #10: P0 — Implement deterministic manufacturing exports
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#48: P1 — Add FreeCAD MCP integration profile](https://github.com/KrasForge/Kanon/issues/48)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:mechanical, area:mcp, type:integration

## Motivation

Add FreeCAD MCP integration profile is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Implement optional selectable FreeCAD profile with read/write separation, isolated reviewer access and explicit offline behavior; document supported operations and qualification tests.

## Acceptance criteria

- [ ] Implement optional selectable FreeCAD profile with read/write separation, isolated reviewer access and explicit offline behavior; document supported operations and qualification tests.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #11: P0 — Define KiCad MCP abstraction boundary
- #12: P0 — Enforce read-only reviewer tool policy

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#49: P1 — Implement mechanical constraint representation](https://github.com/KrasForge/Kanon/issues/49)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:mechanical, type:feature

## Motivation

Implement mechanical constraint representation is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent outline, keep-outs, mounting holes, connector positions, maximum component height and enclosure references with coordinate systems, units and tolerances.

## Acceptance criteria

- [ ] Represent outline, keep-outs, mounting holes, connector positions, maximum component height and enclosure references with coordinate systems, units and tolerances.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#50: P2 — Implement mechanical collision review](https://github.com/KrasForge/Kanon/issues/50)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:mechanical, type:feature

## Motivation

Implement mechanical collision review is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Detect board/enclosure/connector collisions where models permit, respecting transforms/tolerances; incomplete or missing geometry yields limited/unresolved review rather than passing.

## Acceptance criteria

- [ ] Detect board/enclosure/connector collisions where models permit, respecting transforms/tolerances; incomplete or missing geometry yields limited/unresolved review rather than passing.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #47: P1 — Implement STEP-export verification pipeline
- #48: P1 — Add FreeCAD MCP integration profile
- #49: P1 — Implement mechanical constraint representation

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#51: P0 — Implement manufacturing profile schema](https://github.com/KrasForge/Kanon/issues/51)

Milestone: M4 – Manufacturing Release

Labels: priority:P0, area:manufacturing, type:feature

## Motivation

Implement manufacturing profile schema is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate layer count, stackup/thickness/copper, trace/space, via/annular/edge/mask limits, package/assembly policies and sourcing with current capability evidence and qualification date.

## Acceptance criteria

- [ ] Validate layer count, stackup/thickness/copper, trace/space, via/annular/edge/mask limits, package/assembly policies and sourcing with current capability evidence and qualification date.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #32: P0 — Implement datasheet evidence model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#52: P0 — Build release artifact manifest](https://github.com/KrasForge/Kanon/issues/52)

Milestone: M4 – Manufacturing Release

Labels: priority:P0, area:manufacturing, type:feature

## Motivation

Build release artifact manifest is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

List schematic, PCB, Gerbers, drills, BOM, placement when required, STEP, reviews, verification, manufacturing profile and Git revision plus dirty-content hashes/tool versions; reject stale/missing artifacts.

## Acceptance criteria

- [ ] List schematic, PCB, Gerbers, drills, BOM, placement when required, STEP, reviews, verification, manufacturing profile and Git revision plus dirty-content hashes/tool versions; reject stale/missing artifacts.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #10: P0 — Implement deterministic manufacturing exports
- #13: P1 — Implement board/schematic state snapshot abstraction
- #51: P0 — Implement manufacturing profile schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#53: P0 — Implement release command](https://github.com/KrasForge/Kanon/issues/53)

Milestone: M4 – Manufacturing Release

Labels: priority:P0, area:manufacturing, area:verification, type:feature

## Motivation

Implement release command is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Run mandatory gates, stop on failure, generate and validate outputs, create hashed manifest and final report; ensure evidence remains current throughout invocation and never upload/order PCBs.

## Acceptance criteria

- [ ] Run mandatory gates, stop on failure, generate and validate outputs, create hashed manifest and final report; ensure evidence remains current throughout invocation and never upload/order PCBs.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #3: P0 — Implement configurable release-gate engine
- #8: P0 — Implement schematic ERC verification
- #9: P0 — Implement PCB DRC verification
- #10: P0 — Implement deterministic manufacturing exports
- #38: P0 — Implement independent reviewer workflow
- #52: P0 — Build release artifact manifest
- #54: P1 — Implement configurable DFM rules
- #55: P1 — Add fabrication-output consistency tests

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#54: P1 — Implement configurable DFM rules](https://github.com/KrasForge/Kanon/issues/54)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:manufacturing, area:verification, type:feature

## Motivation

Implement configurable DFM rules is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Evaluate measurable fabrication/assembly constraints against qualified manufacturing profile; distinguish errors/warnings/unsupported checks and retain geometry evidence.

## Acceptance criteria

- [ ] Evaluate measurable fabrication/assembly constraints against qualified manufacturing profile; distinguish errors/warnings/unsupported checks and retain geometry evidence.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #51: P0 — Implement manufacturing profile schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#55: P1 — Add fabrication-output consistency tests](https://github.com/KrasForge/Kanon/issues/55)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:manufacturing, type:test

## Motivation

Add fabrication-output consistency tests is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Verify exact expected Gerber layers/drill categories and current-invocation identity; exercise stale, missing, empty, extra-layer and mismatched-revision outputs.

## Acceptance criteria

- [ ] Verify exact expected Gerber layers/drill categories and current-invocation identity; exercise stale, missing, empty, extra-layer and mismatched-revision outputs.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #10: P0 — Implement deterministic manufacturing exports
- #52: P0 — Build release artifact manifest

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#56: P1 — Add visual Gerber review workflow](https://github.com/KrasForge/Kanon/issues/56)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:manufacturing, type:feature

## Motivation

Add visual Gerber review workflow is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Generate/integrate render artifacts with layer/origin metadata and recorded independent review; clearly supplement DRC and output consistency rather than replacing them.

## Acceptance criteria

- [ ] Generate/integrate render artifacts with layer/origin metadata and recorded independent review; clearly supplement DRC and output consistency rather than replacing them.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #10: P0 — Implement deterministic manufacturing exports
- #38: P0 — Implement independent reviewer workflow
- #55: P1 — Add fabrication-output consistency tests

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#57: P1 — Implement audio signal-chain specification model](https://github.com/KrasForge/Kanon/issues/57)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement audio signal-chain specification model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent nominal/max levels with RMS/peak conventions, gain stages, impedance, coupling, filtering, ADC/DAC full scale and headroom requirements with units and evidence.

## Acceptance criteria

- [ ] Represent nominal/max levels with RMS/peak conventions, gain stages, impedance, coupling, filtering, ADC/DAC full scale and headroom requirements with units and evidence.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#58: P1 — Implement gain/headroom audit](https://github.com/KrasForge/Kanon/issues/58)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:verification, type:feature

## Motivation

Implement gain/headroom audit is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Propagate declared signal-chain levels through gains and tolerances; identify clipping, common-mode and headroom incompatibilities with clear stage/corner diagnostics.

## Acceptance criteria

- [ ] Propagate declared signal-chain levels through gains and tolerances; identify clipping, common-mode and headroom incompatibilities with clear stage/corner diagnostics.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #57: P1 — Implement audio signal-chain specification model
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#59: P2 — Implement audio noise-budget model](https://github.com/KrasForge/Kanon/issues/59)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:verification, type:feature

## Motivation

Implement audio noise-budget model is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Calculate first-order thermal/op-amp/converter noise with bandwidth, integration and correlation assumptions; identify unsupported sources and compare against documented reference calculations.

## Acceptance criteria

- [ ] Calculate first-order thermal/op-amp/converter noise with bandwidth, integration and correlation assumptions; identify unsupported sources and compare against documented reference calculations.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #57: P1 — Implement audio signal-chain specification model
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#60: P2 — Implement op-amp configuration checks](https://github.com/KrasForge/Kanon/issues/60)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:verification, type:feature

## Motivation

Implement op-amp configuration checks is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Check declared topology against supply range, common-mode, output swing, gain-bandwidth and evidenced capacitive-load/stability constraints; unsupported stability claims remain unresolved.

## Acceptance criteria

- [ ] Check declared topology against supply range, common-mode, output swing, gain-bandwidth and evidenced capacitive-load/stability constraints; unsupported stability claims remain unresolved.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #57: P1 — Implement audio signal-chain specification model
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#61: P0 — Complete FPGA pin-plan validator](https://github.com/KrasForge/Kanon/issues/61)

Milestone: M5 – Advanced Engineering

Labels: priority:P0, area:verification, type:feature

## Motivation

Complete FPGA pin-plan validator is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Extend bank checks to dedicated, clock-capable, configuration, differential pair, reserved pins and VREF; use device-family data adapters with package-specific provenance.

## Acceptance criteria

- [ ] Extend bank checks to dedicated, clock-capable, configuration, differential pair, reserved pins and VREF; use device-family data adapters with package-specific provenance.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #21: P0 — Implement FPGA bank-voltage validator
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#62: P1 — Add FPGA power-sequencing representation](https://github.com/KrasForge/Kanon/issues/62)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:verification, type:feature

## Motivation

Add FPGA power-sequencing representation is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent device-specific rail order, ramp windows, delays, discharge and partial-power constraints with evidence; detect contradictory sequencing declarations.

## Acceptance criteria

- [ ] Represent device-specific rail order, ramp windows, delays, discharge and partial-power constraints with evidence; detect contradictory sequencing declarations.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #22: P0 — Implement power-tree model
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#63: P1 — Add FPGA configuration/boot audit](https://github.com/KrasForge/Kanon/issues/63)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:verification, type:feature

## Motivation

Add FPGA configuration/boot audit is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Check boot device, straps, configuration interface, programming header, pull resistors and flash compatibility against device-specific constraints and pin plan.

## Acceptance criteria

- [ ] Check boot device, straps, configuration interface, programming header, pull resistors and flash compatibility against device-specific constraints and pin plan.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #61: P0 — Complete FPGA pin-plan validator
- #34: P1 — Associate verified constraints with evidence

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#64: P1 — Add FPGA decoupling-rule framework](https://github.com/KrasForge/Kanon/issues/64)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:verification, area:datasheets, type:feature

## Motivation

Add FPGA decoupling-rule framework is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Represent family/device-specific decoupling requirements with source revision, package/rail applicability and placement limitations; missing rules cannot imply complete coverage.

## Acceptance criteria

- [ ] Represent family/device-specific decoupling requirements with source revision, package/rail applicability and placement limitations; missing rules cannot imply complete coverage.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #24: P1 — Implement decoupling audit framework
- #34: P1 — Associate verified constraints with evidence
- #61: P0 — Complete FPGA pin-plan validator

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#65: P2 — Build PCB visual-review artifact pipeline](https://github.com/KrasForge/Kanon/issues/65)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:kicad, type:feature

## Motivation

Build PCB visual-review artifact pipeline is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Produce consistent top, bottom and 3D views with source hash, layer visibility, camera/origin and tool versions; flag incomplete 3D models and unavailable renderers.

## Acceptance criteria

- [ ] Produce consistent top, bottom and 3D views with source hash, layer visibility, camera/origin and tool versions; flag incomplete 3D models and unavailable renderers.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #13: P1 — Implement board/schematic state snapshot abstraction
- #47: P1 — Implement STEP-export verification pipeline

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#66: P2 — Define visual PCB review rubric](https://github.com/KrasForge/Kanon/issues/66)

Milestone: M5 – Advanced Engineering

Labels: priority:P2, area:skills, type:feature

## Motivation

Define visual PCB review rubric is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Evaluate backwards connectors, bizarre placement, unreadable silkscreen, overlap, mechanical obstruction and obvious routing anomalies using known-defect fixtures; record occlusion and require nonvisual corroboration.

## Acceptance criteria

- [ ] Evaluate backwards connectors, bizarre placement, unreadable silkscreen, overlap, mechanical obstruction and obvious routing anomalies using known-defect fixtures; record occlusion and require nonvisual corroboration.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #65: P2 — Build PCB visual-review artifact pipeline
- #6: P1 — Define structured engineering review/finding schema

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#67: P1 — Design read-only `pcb-verifier` MCP API](https://github.com/KrasForge/Kanon/issues/67)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:mcp, area:verification, type:feature

## Motivation

Design read-only `pcb-verifier` MCP API is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Specify check_power_tree, check_decoupling, check_pin_electrical_types, check_fpga_banks, check_connector_protection, check_clock_topology, check_testpoint_coverage, check_bom_lifecycle, check_bom_stock, check_footprint_datasheet_match, check_mounting_clearance, check_high_current_paths, check_audio_signal_chain and check_manufacturability with provenance/errors and read-only source contract.

## Acceptance criteria

- [ ] Specify check_power_tree, check_decoupling, check_pin_electrical_types, check_fpga_banks, check_connector_protection, check_clock_topology, check_testpoint_coverage, check_bom_lifecycle, check_bom_stock, check_footprint_datasheet_match, check_mounting_clearance, check_high_current_paths, check_audio_signal_chain and check_manufacturability with provenance/errors and read-only source contract.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model
- #11: P0 — Define KiCad MCP abstraction boundary
- #13: P1 — Implement board/schematic state snapshot abstraction

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#68: P1 — Implement initial `pcb-verifier` MCP server](https://github.com/KrasForge/Kanon/issues/68)

Milestone: M5 – Advanced Engineering

Labels: priority:P1, area:mcp, area:verification, type:integration

## Motivation

Implement initial `pcb-verifier` MCP server is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Expose only checks backed by working implementations via the approved API; enforce read-only design access, bounded execution and explicit unavailable/error results. Add tools incrementally after check qualification.

## Acceptance criteria

- [ ] Expose only checks backed by working implementations via the approved API; enforce read-only design access, bounded execution and explicit unavailable/error results. Add tools incrementally after check qualification.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #67: P1 — Design read-only `pcb-verifier` MCP API
- #12: P0 — Enforce read-only reviewer tool policy
- #16: P0 — Validate manufacturer part-number completeness

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #82


## [#69: P0 — Add unit-test and Ruff CI](https://github.com/KrasForge/Kanon/issues/69)

Milestone: M0 – Foundation

Labels: priority:P0, area:ci, type:test

## Motivation

Add unit-test and Ruff CI is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Harden initial Python >=3.12 pytest/Ruff workflow, dependency reproducibility and failure reporting; tests run without KiCad/ngspice and integration omissions are explicit.

## Acceptance criteria

- [ ] Harden initial Python >=3.12 pytest/Ruff workflow, dependency reproducibility and failure reporting; tests run without KiCad/ngspice and integration omissions are explicit.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#70: P1 — Add KiCad integration-test job](https://github.com/KrasForge/Kanon/issues/70)

Milestone: M1 – KiCad Closed Loop

Labels: priority:P1, area:ci, area:kicad, type:test

## Motivation

Add KiCad integration-test job is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Provide a reliable pinned/qualified KiCad 10 environment and valid schematic/PCB fixtures for ERC/DRC/export success and known failures; never label mocked execution as integration coverage.

## Acceptance criteria

- [ ] Provide a reliable pinned/qualified KiCad 10 environment and valid schematic/PCB fixtures for ERC/DRC/export success and known failures; never label mocked execution as integration coverage.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #7: P0 — Implement robust `kicad-cli` adapter
- #8: P0 — Implement schematic ERC verification
- #9: P0 — Implement PCB DRC verification
- #10: P0 — Implement deterministic manufacturing exports
- #69: P0 — Add unit-test and Ruff CI

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #78


## [#71: P1 — Add ngspice integration tests](https://github.com/KrasForge/Kanon/issues/71)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:ci, area:simulation, type:test

## Motivation

Add ngspice integration tests is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Run real batch simulation with representative measure success/failure fixtures, include errors and limit violations; skip explicitly only when tool is unavailable outside qualified CI.

## Acceptance criteria

- [ ] Run real batch simulation with representative measure success/failure fixtures, include errors and limit violations; skip explicitly only when tool is unavailable outside qualified CI.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #28: P0 — Implement ngspice process adapter
- #29: P1 — Add declarative simulation assertions
- #69: P0 — Add unit-test and Ruff CI

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#72: P1 — Add golden verification-report tests](https://github.com/KrasForge/Kanon/issues/72)

Milestone: M2 – Engineering Verification

Labels: priority:P1, area:ci, area:verification, type:test

## Motivation

Add golden verification-report tests is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Add stable serialized PASS/FAIL/WARN/SKIP/ERROR fixtures, mandatory/optional/manual aggregation and stale/duplicate evidence cases with deliberate schema migration review.

## Acceptance criteria

- [ ] Add stable serialized PASS/FAIL/WARN/SKIP/ERROR fixtures, mandatory/optional/manual aggregation and stale/duplicate evidence cases with deliberate schema migration review.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #2: P0 — Implement verification result and report model
- #3: P0 — Implement configurable release-gate engine
- #69: P0 — Add unit-test and Ruff CI

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #79


## [#73: P1 — Add end-to-end minimal-board test](https://github.com/KrasForge/Kanon/issues/73)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:ci, type:test

## Motivation

Add end-to-end minimal-board test is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Reproducibly exercise spec validation, real qualified checks and release report; distinguish spec-only foundation test from completed schematic/PCB/release path and assert blocked incomplete inputs.

## Acceptance criteria

- [ ] Reproducibly exercise spec validation, real qualified checks and release report; distinguish spec-only foundation test from completed schematic/PCB/release path and assert blocked incomplete inputs.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #53: P0 — Implement release command
- #70: P1 — Add KiCad integration-test job
- #72: P1 — Add golden verification-report tests

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#74: P0 — Write architecture documentation](https://github.com/KrasForge/Kanon/issues/74)

Milestone: M0 – Foundation

Labels: priority:P0, area:docs, type:feature

## Motivation

Write architecture documentation is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Maintain trust-boundary/lifecycle/evidence diagrams, capability matrix and current implementation status; explain why generative success and export success are not verification.

## Acceptance criteria

- [ ] Maintain trust-boundary/lifecycle/evidence diagrams, capability matrix and current implementation status; explain why generative success and export success are not verification.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #1: P0 — Define canonical PCB design specification schema
- #2: P0 — Implement verification result and report model

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#75: P0 — Document local development setup](https://github.com/KrasForge/Kanon/issues/75)

Milestone: M0 – Foundation

Labels: priority:P0, area:docs, type:feature

## Motivation

Document local development setup is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Validate clean Python/KiCad/ngspice/Git/MCP and optional FreeCAD setup, tests and missing-dependency behavior; distinguish repository contracts from deployable harness configuration.

## Acceptance criteria

- [ ] Validate clean Python/KiCad/ngspice/Git/MCP and optional FreeCAD setup, tests and missing-dependency behavior; distinguish repository contracts from deployable harness configuration.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #4: P0 — Implement environment diagnostics
- #69: P0 — Add unit-test and Ruff CI

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #77


## [#76: P1 — Write “Design a board with Astra” walkthrough](https://github.com/KrasForge/Kanon/issues/76)

Milestone: M4 – Manufacturing Release

Labels: priority:P1, area:docs, type:feature

## Motivation

Write “Design a board with Astra” walkthrough is needed to make the PCB workflow evidence-driven and reviewable. The initialization provides only the capabilities documented in README; this issue tracks the complete acceptance scope.

## Scope

Demonstrate spec→architecture→schematic→PCB→independent review→release using reproducible artifacts only after dependencies work; keep current spec-only path explicitly limited.

## Acceptance criteria

- [ ] Demonstrate spec→architecture→schematic→PCB→independent review→release using reproducible artifacts only after dependencies work; keep current spec-only path explicitly limited.
- [ ] Document supported inputs, limitations and explicit unknown/error behavior.
- [ ] Attach reproducible evidence satisfying this issue; scaffolding alone does not close it.

## Tests/verification

Add valid, invalid, boundary and unavailable-input fixtures for this scope. Assert structured diagnostics and provenance; run pytest and Ruff. External tool tests must use qualified versions and explicit integration markers, with mocks identified as unit tests.

## Dependencies

- #14: P1 — Add design mutation → verify workflow
- #38: P0 — Implement independent reviewer workflow
- #53: P0 — Implement release command
- #73: P1 — Add end-to-end minimal-board test

## Non-goals

No fabrication ordering, silent design changes, or success responses for unimplemented analysis. Unrelated domain checks remain separate issues.

Milestone tracker: #81


## [#77: M0 tracking — Foundation](https://github.com/KrasForge/Kanon/issues/77)

Milestone: M0 – Foundation

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #1 — P0 — Define canonical PCB design specification schema
- [ ] #2 — P0 — Implement verification result and report model
- [ ] #3 — P0 — Implement configurable release-gate engine
- [ ] #4 — P0 — Implement environment diagnostics
- [ ] #5 — P1 — Define engineering decision record model
- [ ] #6 — P1 — Define structured engineering review/finding schema
- [ ] #69 — P0 — Add unit-test and Ruff CI
- [ ] #74 — P0 — Write architecture documentation
- [ ] #75 — P0 — Document local development setup

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.

## [#78: M1 tracking — KiCad Closed Loop](https://github.com/KrasForge/Kanon/issues/78)

Milestone: M1 – KiCad Closed Loop

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #7 — P0 — Implement robust `kicad-cli` adapter
- [ ] #8 — P0 — Implement schematic ERC verification
- [ ] #9 — P0 — Implement PCB DRC verification
- [ ] #10 — P0 — Implement deterministic manufacturing exports
- [ ] #11 — P0 — Define KiCad MCP abstraction boundary
- [ ] #12 — P0 — Enforce read-only reviewer tool policy
- [ ] #13 — P1 — Implement board/schematic state snapshot abstraction
- [ ] #14 — P1 — Add design mutation → verify workflow
- [ ] #70 — P1 — Add KiCad integration-test job

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.

## [#79: M2 tracking — Engineering Verification](https://github.com/KrasForge/Kanon/issues/79)

Milestone: M2 – Engineering Verification

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #15 — P0 — Implement canonical BOM model and importer
- [ ] #16 — P0 — Validate manufacturer part-number completeness
- [ ] #17 — P1 — Implement BOM normalization and inconsistency checks
- [ ] #18 — P1 — Add JLCPCB/LCSC sourcing adapter
- [ ] #19 — P1 — Add part lifecycle and sourcing-risk model
- [ ] #21 — P0 — Implement FPGA bank-voltage validator
- [ ] #22 — P0 — Implement power-tree model
- [ ] #23 — P1 — Implement regulator power/thermal calculation checks
- [ ] #24 — P1 — Implement decoupling audit framework
- [ ] #25 — P1 — Implement connector protection audit
- [ ] #26 — P1 — Implement test-point coverage audit
- [ ] #28 — P0 — Implement ngspice process adapter
- [ ] #29 — P1 — Add declarative simulation assertions
- [ ] #30 — P1 — Add audio filter simulation workflow
- [ ] #31 — P1 — Add power-circuit simulation workflow
- [ ] #32 — P0 — Implement datasheet evidence model
- [ ] #33 — P1 — Build local datasheet registry
- [ ] #34 — P1 — Associate verified constraints with evidence
- [ ] #71 — P1 — Add ngspice integration tests
- [ ] #72 — P1 — Add golden verification-report tests

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.

## [#80: M3 tracking — Agentic PCB Designer](https://github.com/KrasForge/Kanon/issues/80)

Milestone: M3 – Agentic PCB Designer

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #36 — P0 — Implement design lifecycle state machine
- [ ] #37 — P0 — Implement Architect/Designer/Reviewer role definitions
- [ ] #38 — P0 — Implement independent reviewer workflow
- [ ] #39 — P1 — Implement review → remediation loop
- [ ] #40 — P1 — Add critical-net classification
- [ ] #41 — P1 — Enforce critical-net review before release
- [ ] #43 — P1 — Define PCB floorplanning model
- [ ] #44 — P1 — Implement placement-rule checks

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.

## [#81: M4 tracking — Manufacturing Release](https://github.com/KrasForge/Kanon/issues/81)

Milestone: M4 – Manufacturing Release

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #47 — P1 — Implement STEP-export verification pipeline
- [ ] #48 — P1 — Add FreeCAD MCP integration profile
- [ ] #49 — P1 — Implement mechanical constraint representation
- [ ] #51 — P0 — Implement manufacturing profile schema
- [ ] #52 — P0 — Build release artifact manifest
- [ ] #53 — P0 — Implement release command
- [ ] #54 — P1 — Implement configurable DFM rules
- [ ] #55 — P1 — Add fabrication-output consistency tests
- [ ] #56 — P1 — Add visual Gerber review workflow
- [ ] #73 — P1 — Add end-to-end minimal-board test
- [ ] #76 — P1 — Write “Design a board with Astra” walkthrough

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.

## [#82: M5 tracking — Advanced Engineering](https://github.com/KrasForge/Kanon/issues/82)

Milestone: M5 – Advanced Engineering

Labels: type:meta

## Motivation

Track milestone delivery by demonstrated acceptance, not scaffolding.

## Scope and dependencies

- [ ] #20 — P2 — Implement alternate-part compatibility representation
- [ ] #27 — P2 — Implement clock-topology checker
- [ ] #35 — P2 — Research reliable datasheet ingestion/extraction pipeline
- [ ] #42 — P2 — Add engineering change-plan representation
- [ ] #45 — P2 — Research return-path analysis
- [ ] #46 — P2 — Research automatic critical-net routing strategies
- [ ] #50 — P2 — Implement mechanical collision review
- [ ] #57 — P1 — Implement audio signal-chain specification model
- [ ] #58 — P1 — Implement gain/headroom audit
- [ ] #59 — P2 — Implement audio noise-budget model
- [ ] #60 — P2 — Implement op-amp configuration checks
- [ ] #61 — P0 — Complete FPGA pin-plan validator
- [ ] #62 — P1 — Add FPGA power-sequencing representation
- [ ] #63 — P1 — Add FPGA configuration/boot audit
- [ ] #64 — P1 — Add FPGA decoupling-rule framework
- [ ] #65 — P2 — Build PCB visual-review artifact pipeline
- [ ] #66 — P2 — Define visual PCB review rubric
- [ ] #67 — P1 — Design read-only `pcb-verifier` MCP API
- [ ] #68 — P1 — Implement initial `pcb-verifier` MCP server

## Acceptance criteria

- [ ] Every child meets its acceptance criteria with review evidence.
- [ ] Cross-issue integration is demonstrated and remaining limitations documented.

## Tests/verification

Review child test evidence and run milestone integration checks. No child may be closed solely because an interface or Skill exists.

## Non-goals

This tracker does not override child dependencies or approve manufacturing.
