# Qualified model files, units and circuit corners

SimulationJob now requires `measurement_units` for every assertion and `unit` on each
assertion. The checker rejects unknown/mismatched dimensions and converts compatible
units such as V/mV and Hz/kHz before comparing bounds. Measurement units describe the
actual ngspice vector/expression; they are declarations that must be reviewed with the
netlist. The report binds circuit/model content and the complete job, including limits.

Local `.include`/`.inc` and `.lib file section` directives resolve only against an explicit
ModelFile inventory: relative path, SHA-256, allowed sections, license, approval provenance
and document evidence. Includes are expanded in bounded recursion before invoking ngspice.
Missing/changed/unapproved files, root escapes, cycles and unqualified library sections
fail. Every source hash is rechecked after simulation. There is no network model download
or automatic model approval. Unsafe control commands remain denied after flattening.
Some vendor dialects may require an explicit reviewed conversion; unsupported syntax is
an error, not a reason to skip source validation or silently substitute a primitive.

`astra-pcb simulate-corners audio-filter plan.yaml --output new-directory` runs every
specified R/C/source/load combination. Each circuit includes source/load impedances and
measures passband gain and cutoff relative to that corner's loaded DC gain. The plan
supplies gain and cutoff acceptance bounds and cited assumptions. Supported plans use the
AudioFilterSweep model; the integration test exercises 16 actual ngspice corners.

`astra-pcb simulate-corners power-source plan.yaml --output new-directory` runs declared
voltage/source-resistance/capacitance combinations with an approved local library section.
It measures 90% startup time, loaded rail level and recovery. This workflow qualifies a
linear source-impedance model, not every regulator topology; its settling-time envelope is
checked before simulation. Vendor regulator workflows can use SimulationJob with explicit
approved model files and startup/load assertions rather than pretending that ideal RC
behavior describes a switching control loop. The integration test exercises eight corners.

Inputs and logs remain in separate per-corner directories. A failed process never yields
passing measurement assertions. Tests cover library identity/cycles/escapes, dimension
mismatches, real loaded filter behavior and real startup/transient measurements.
