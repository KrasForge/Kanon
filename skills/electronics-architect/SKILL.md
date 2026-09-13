---
name: electronics-architect
description: Decompose hardware specifications into evidence-backed architecture before schematic design.
---

# Electronics Architect

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Extract requirements

Separate functional targets, acceptance tests and unresolved assumptions. Give each requirement an ID, units, operating corners and owner; distinguish desired from mandatory behavior.

## Decompose subsystems

Identify signal-chain stages, interfaces and direction, voltage domains and isolation boundaries. Trace every interface to connector/device pins and its electrical standard.

## Plan infrastructure

Draw the power tree with sources, rail budgets, sequencing and discharge paths; draw the clock tree with frequencies and consumers. Specify reset/boot defaults, programming and debug access, and behavior with partial power.

## Resolve risk

Inventory thermal, sourcing, mechanical, signal-integrity and bring-up risks. Establish constraints and review gates before expensive layout. Record alternatives, evidence, calculations and invalidation conditions in hardware/decisions/.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
