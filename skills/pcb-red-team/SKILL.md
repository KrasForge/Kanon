---
name: pcb-red-team
description: Independently attempt to invalidate a frozen PCB design and produce actionable findings.
---

# Pcb Red Team

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Establish independence

Use a read-only snapshot, BOM, evidence, simulations, ERC/DRC and outputs. Refuse mutation tools or writable source access. Record scope, input hashes and unavailable artifacts before drawing conclusions.

## Attack identity and startup

Seek pinout mismatches, wrong footprints, reversed connectors, wrong voltage domains, FPGA bank conflicts, missing pull resistors and configuration errors. Follow power paths for insufficient regulator headroom, current-limit problems and bad thermal assumptions.

## Attack electrical behavior

Look for missing ESD, decoupling errors, unstable op-amp circuits, switching regulator layout mistakes, poor return paths and unintended current loops. Check worst-case assumptions and source citations independently; passing ERC/DRC is only one input.

## Attack build and bring-up

Seek inaccessible test points, mechanical collisions, manufacturing hazards, misleading silkscreen and lifecycle/sourcing risks. Use renders to form hypotheses and confirm against connectivity, geometry and part drawings.

## Write findings

For each blocker/major/minor/observation include ID, evidence, affected subsystem/nets/components, failure mechanism and suggested remediation. Preserve IDs across revisions. Missing evidence is a limitation or finding; never fabricate success or directly fix the design.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
