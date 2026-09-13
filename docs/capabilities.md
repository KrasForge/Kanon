# Implementation status

| Capability | Present now | Not established |
|---|---|---|
| Verification | Versioned reports, content identity, exit codes, golden status tests | Trusted automated execution provenance across distributed agents |
| Release gates | Mandatory YAML gates, signed independent approvals/human waivers | Release transaction |
| Design inputs | Five schemas, semantic ranges/references/cycles, migration | Complete physical constraints and vendor device-family datasets |
| KiCad | Real ERC/DRC, export receipts, snapshots and mutation workflow; narrow external MCP SWIG qualification | Interactive IPC and populated-board qualification |
| Simulation | Real ngspice execution, log-error detection, declarative assertions, ideal power/audio examples | Vendor regulator stability, external model ingestion, board-level analog validation |
| BOM | JSON/CSV import, missing MPN/duplicate/conflict checks, public JLCSearch lookup, sourcing risk | Account-gated official supplier API, alternate qualification |
| Evidence | Content-addressed document registry and cited numeric limits | PDF extraction, authenticity and automatic applicability verification |
| Electrical checks | Declared FPGA bank, current/thermal, decoupling, connector protection and test-point audits | Automatic native connectivity/geometry extraction for all audits |
| Agents/MCP | Lifecycle gates, typed roles, frozen review/remediation, critical-net coverage, quantified placement | Live model API transport and OS sandbox for arbitrary agent code |
| Manufacturing | Unqualified example profile and substantive review guidance | Qualified DFM, output consistency, manifest, release |
| CI | Passing remote Python and real KiCad/ngspice jobs on M0/M1 PRs; M2 adds simulation/golden regressions | Reproducible live supplier or GUI server in CI |

Read [integration qualification](integrations.md) for the exact external tools tested.
The native KiCad fixtures are empty parser/export controls, not fabricated electronics.
Electrical checks assess their declared inputs; independent review must reconcile those
inputs against native design state and manufacturer evidence. Unknown information and
skipped checks never become successful mandatory gates.
