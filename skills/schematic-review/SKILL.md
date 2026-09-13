---
name: schematic-review
description: Independently inspect schematic electrical intent and symbol-to-footprint consistency.
---

# Schematic Review

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Trace power

Enumerate every power pin including hidden pins and exposed pads; inspect power flags without using them to conceal a real ERC issue. Check local decoupling, rail sources, analog references and unused-pin handling against documentation.

## Trace startup

Check pull-ups/pull-downs, reset timing, boot straps, FPGA configuration pins and defaults during partial power. Ensure test points/programming headers make boot failures observable.

## Trace interfaces

Follow named nets through hierarchy and connector numbering; check connector protection, termination, voltage translation and intentional no-connects. Inspect repeated labels and accidental merges.

## Cross-check implementation

Compare manufacturer pin tables with symbol pins and footprint pad numbers, including orientation. Attach ERC results and source hash; enumerate findings with evidence and affected nets. ERC passing does not settle electrical intent.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
