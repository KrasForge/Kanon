---
name: power-design
description: Analyze rail budgets, regulator constraints, thermal margin and power-layout requirements.
---

# Power Design

Read ../../AGENTS.md and the project specification. Treat draft assumptions as unresolved.

## Budget corners

Build rail tree and load table with steady, startup, transient and fault current. Include regulator quiescent draw, dependencies and sequencing. Check input/output voltage tolerance and headroom across temperature and load.

## Calculate losses

Use scripts for linear regulator loss (Vin−Vout)×I plus quiescent terms; use evidence-backed efficiency for switchers. Record thermal resistance assumptions and board conditions; never invent package thermal parameters.

## Specify capacitance

Check MLCC DC-bias/temperature/aging derating using manufacturer curves, bulk/local capacitance and regulator ESR/stability requirements. Consider transient loads, cable inductance and inrush.

## Inspect behavior and geometry

Review switching loops, switch-node area, feedback sensing and return paths. Evaluate power-up/down, backfeed, discharge and brownout. Produce rail margin table and placement constraints with unresolved models explicit.

## Deliverable

Record evidence in hardware/reviews/ or hardware/decisions/ using the templates. Include
source revision/page, units, assumptions, calculations, affected objects and remaining
unknowns. This Skill guides engineering work; it does not implement a deterministic check.
