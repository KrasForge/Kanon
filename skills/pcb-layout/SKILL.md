---
name: pcb-layout
description: Plan and review PCB placement, critical routing and electrical return paths.
---

# Pcb Layout

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Floorplan first

Fix outline, connectors, mounting and testability; partition functional regions. Place power conversion, clocks and sensitive analog before general routing; review connector orientation against mating hardware.

## Route by risk

Route critical nets first: differential pairs, clocks, analog feedback loops, switching loops and high-current power routes. Apply justified width/spacing/length constraints; avoid tuning length without a timing requirement.

## Trace returns

For every critical route reason about return-current continuity, plane changes and stitching vias. Inspect via current capacity, layer transitions, zones and actual filled geometry; do not infer continuity from unfilled outlines.

## Close the loop

Save and read back mutations, run independent ERC/DRC as applicable, and attach diffs and reports. Inspect test-point accessibility and probe clearance. Hand a frozen state to the separate reviewer.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
