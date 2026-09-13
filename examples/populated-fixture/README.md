# Populated software qualification coupon

This project-owned test design has two synthetic 1k resistors in parallel, two nets, two
routed tracks, a 20 × 18 × 1.6 mm outline, footprint courtyards and simple 3D bodies. It
is a reproducible **software integration fixture**, not a commercial BOM or fabrication
recommendation. The `SYNTHETIC-1K` MPN explicitly names a fixture, not a fabricated vendor part.
All native symbol, footprint and STEP geometry here was authored for this project.

Architecture: a passive two-terminal 500-ohm nominal network; no clocks, FPGA, regulator or
active circuitry. The 0.3 mm tracks connect corresponding pins without crossings. STEP
bodies are 4 × 1.6 × 0.8 mm geometric controls, not manufacturer-qualified models. Component
selection and thermal/current limits are intentionally outside a software fixture's scope.
For a physical product, replace these parts and constraints using manufacturer documentation.

The checked-in KiCad project enables all otherwise ignored ERC/DRC checks. KiCad 10.0.6
reports zero ERC violations, zero DRC violations, zero unconnected items and zero parity
issues, with no ignored checks. The generator used the native SWIG PCB API plus a complete
local schematic symbol library; no external MCP schematic construction is claimed.

```sh
uv run astra-pcb validate examples/populated-fixture/design-spec.yaml
uv run pytest tests/test_populated_release.py -v
```

The test copies this project to a disposable Git repository, creates a clearly synthetic
manufacturing profile and test signer, runs actual CLI ERC/DRC/parity/exports, requires
fresh artifact signatures, verifies final manifest hashes, then checks that a source
mutation invalidates prior approvals. No fake exporters or mocked verification results
are used. The private key exists only within this test. Production signing belongs to
independent principals outside agent tools.

There is deliberately no committed `profile.yaml`, approval or ready-to-order package.
An ordinary release invocation fails until genuine project-specific evidence is supplied.
