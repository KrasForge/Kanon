---
name: fpga-board-design
description: Plan FPGA rails, configuration and evidence-backed package pin assignments.
---

# Fpga Board Design

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Establish device data

Record full device/package/speed grade and family documentation revision. Enumerate FPGA banks and I/O voltages; validate I/O standards, VREF and dedicated/reserved pins through device-specific data.

## Plan configuration

Trace configuration interface, boot flash compatibility, mode straps, JTAG chain and programming access. Verify configuration-bank supply requirements and power-up defaults; never silently change bank voltages.

## Plan infrastructure

Review clocks, clock-capable pins, PLL supply/filter guidance, rail sequencing and decoupling. Budget startup current and provide debug access. Handle unused pins per family guidance.

## Validate pin plan

Cross-check package pin IDs, differential pairs/polarity, external interfaces and bank assignments against schematic/netlist. Structural schema validation cannot detect all bank conflicts; missing family rules block approval.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
