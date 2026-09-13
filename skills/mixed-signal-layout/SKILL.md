---
name: mixed-signal-layout
description: Review mixed-signal placement and return paths using circuit topology and plane geometry.
---

# Mixed Signal Layout

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Follow current

Identify high-frequency current return paths for each clock, converter interface and analog loop. Inspect reference planes and via transitions; do not cross plane splits without a justified return strategy.

## Place by coupling

Place converters near their references and local supply networks. Separate switching-noise sources from sensitive analog nodes through geometry and current-loop control. Keep clock edges and switching nodes away from high-impedance references.

## Choose grounding deliberately

Reject cargo-cult analog/digital ground splitting. Prefer a continuous reference where appropriate and justify any split from manufacturer guidance and actual current paths; labels alone do not isolate noise.

## Review evidence

Inspect plane pours after refill, layer transitions, reference routing and analog signal integrity. Record geometric evidence and what requires measurement or field analysis; proximity to ground alone is not proof.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
