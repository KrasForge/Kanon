---
name: manufacturing-release
description: Assemble and inspect mandatory revision-bound evidence before manufacturing release.
---

# Manufacturing Release

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Freeze inputs

Require requirements, architecture/component approvals, source schematic/PCB, exact libraries, manufacturing profile, BOM and design revision/content hashes. Dirty work needs content identity; a Git commit alone is insufficient.

## Require verification

Require fresh ERC, DRC, parity where available, BOM/footprint checks, simulation assertions, power and critical-net reviews, mechanical review, DFM and final independent review. Mandatory FAIL/ERROR/SKIP/missing evidence blocks release.

## Validate outputs

Generate Gerbers, drills, STEP and placement outputs where required into a new invocation directory. Inspect expected layers, plated/non-plated drills, units, outline and artifact completeness. Hash manifest entries and associate reports with the same inputs.

## Apply authority boundary

LLM judgment cannot override mandatory failure. Human waivers need explicit identity, reason, scope, revision and expiry; the gate engine verifies external Ed25519 signatures, with waiver support disabled per gate by default. Visual Gerber review supplements deterministic checks. Do not upload or order boards without separate explicit intent.

## Report honestly

List every gate, warning, waiver if supported, reviewer and artifact. Until the release pipeline exists, report blocked and preserve evidence; do not turn export command success into manufacturing approval.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
