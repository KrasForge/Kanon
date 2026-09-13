---
name: component-selection
description: Select and justify electronic components against electrical, sourcing and assembly requirements.
---

# Component Selection

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Build a selection table

Compare electrical limits over voltage, load and temperature corners, not typical headline values. Obtain manufacturer documentation with revision and source; distinguish absolute maximum from recommended operation.

## Check physical suitability

Match package, pinout and footprint land pattern; account for assembly constraints, exposed pads, inspection, rework, height and preferred package sizes. Verify temperature grade and ordering suffix.

## Assess sourcing

Record lifecycle, timestamped stock, authorized supplier, MOQ, cost at quantity and Basic/Extended classification if verified. Unknown stock is unknown. Consolidate BOM MPNs where requirements actually match.

## Control alternates

Record alternates with differences in pinout, ratings, tolerances, timing, layout and qualification. Never silently substitute. A matching value/package is insufficient; submit tradeoffs and decision evidence.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
