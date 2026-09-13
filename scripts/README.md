# Developer entry points

Run from the repository root after installing the package. `verify.py`,
`check_environment.py` and `release.py` delegate to the corresponding CLI commands.
Release uses the two-phase project/gate/approval workflow documented in
[manufacturing-release.md](../docs/manufacturing-release.md).

`check_bom.py` accepts a JSON array of canonical per-reference rows. The decoupling,
pinmap and bank scripts delegate to the bounded `astra-pcb check` tools and accept the
JSON/YAML input schemas advertised by the [verifier](../docs/pcb-verifier.md).
`check_datasheet_limits.py observations.yaml --registry registry.json --root hardware`
loads a content-addressed registry and a list of `{limit, value, unit}` observations.
Each limit must have applicability, units, bounds and a registered hashed citation.

`simulate_power.py` and `simulate_filter.py` accept a SimulationJob YAML plus a required
fresh `--output` directory, just like `astra-pcb simulate`. Use the ideal examples under
examples/simulation as reproducible controls. A topology-specific vendor model needs
separate model/licensing/physics qualification. These scripts never return fabricated
success when a tool or required input is unavailable.

`qualify_freecad.py` is executed by the optional integration test through FreeCADCmd,
not ordinary Python. Its fresh output directory comes from KANON_FREECAD_SMOKE_ROOT.
See [FreeCAD qualification](../docs/freecad.md).
