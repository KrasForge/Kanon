# Implementation status

| Capability | Present now | Not established |
|---|---|---|
| Verification | Versioned reports, content identity, exit codes, serialization | Trusted automated execution provenance |
| Release gates | YAML policy, mandatory gates, signed independent approvals/human waivers | Release transaction |
| Design inputs | Five JSON Schemas, semantic ranges/rail references/cycles, migration | FPGA device rules and physical constraints |
| KiCad | Bounded ERC/DRC/export command hooks | Report interpretation, complete export qualification, board fixtures |
| Simulation | ngspice invocation, scalar parsing and finite limit checks | Local real ngspice execution, power/audio workflows |
| BOM | Canonical rows, missing MPN/duplicate/conflict checks | CSV/KiCad importer, live sourcing, alternate qualification |
| Evidence | Datasheet document/revision/locator/constraint identity | Registry, extraction, authenticity and rule applicability |
| Agents/MCP | Role contracts, empty reviewer allowlist, substantive Skills | Harness, capability enforcement, server connections, lifecycle |
| Manufacturing | Unqualified example profile and review guidance | Qualified DFM, output consistency, manifest, release |
| CI | Python pytest/Ruff workflow and lockfile | Remote CI execution; no commit/push made |

The KiCad integration smoke test checks executable version and missing-input rejection.
It does not qualify ERC/DRC on a real board. The ngspice integration test skips explicitly
when ngspice is absent. A passing schema check only establishes document structure.
