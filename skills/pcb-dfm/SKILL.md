---
name: pcb-dfm
description: Review PCB fabrication and assembly against a qualified manufacturing profile.
---

# Pcb Dfm

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Qualify profile

Check current fab and assembly capabilities for layer count, stackup, copper, trace/space, via drill, annular rings and edge clearance. Example profile values are project preferences, not certified fab limits.

## Inspect fabrication

Review soldermask webs/expansion, slots, plated versus non-plated holes, via tenting/fill requirements, panel considerations and copper-to-edge constraints. Ensure drill intent matches outputs.

## Inspect assembly

Check package limits, BGA/0402 policy, fiducials, polarity marking, courtyard collisions, exposed-pad paste and rework access. Confirm single/double-sided assembly implications.

## Cross-check deliverables

Compare BOM, footprint, pick-and-place origin/rotation/side and assembly drawing. Verify connector polarity and readable silkscreen. Record supplier-specific rotation uncertainties for independent confirmation.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
