---
name: audio-electronics
description: Analyze audio signal chains, levels, noise and stability before schematic or layout approval.
---

# Audio Electronics

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Normalize levels

State RMS, peak and peak-to-peak explicitly; document balanced/unbalanced conventions and ADC/DAC full-scale definitions. Calculate gain staging, clipping and headroom over supply/load corners.

## Check interfaces

Review input/output protection and impedance, DC coupling/blocking, bias currents, common-mode range and startup pops. Verify codec/reference supplies and reference decoupling against manufacturer requirements.

## Evaluate filters and amplifiers

Model anti-alias and reconstruction filters including source/load impedance and tolerance. Check op-amp stability, noise gain, capacitive loading, output swing and bandwidth; record model limitations.

## Budget quality

Estimate noise and THD using supported data and distinguish estimates from measured performance. Review clocks/jitter against converter needs without inventing a universal jitter threshold. Deliver level/noise budgets and simulation assertions.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
