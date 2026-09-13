# Implementation status

| Capability | Present now | Not established |
|---|---|---|
| Verification | Versioned reports, content identity, exit codes, golden status tests | Trusted automated execution provenance across distributed agents |
| Release gates | Mandatory YAML gates, signed independent approvals/human waivers | Deployment trust/key provisioning |
| Design inputs | Design schemas, semantic ranges/references/cycles, migration | Complete physical constraints and vendor device-family datasets |
| KiCad | Real ERC/DRC, export receipts, snapshots and mutation workflow; narrow external MCP SWIG qualification | Interactive IPC and populated-board qualification |
| Simulation | Real ngspice execution, log-error detection, declarative assertions, ideal power/audio examples | Vendor regulator stability, external model ingestion, board-level analog validation |
| BOM | JSON/CSV import, missing MPN/duplicate/conflict checks, credential-free JLCSearch/Adafruit lookup, sourcing risk | Account-gated official supplier API, qualification of real alternate parts |
| Evidence | Content-addressed document registry and cited numeric limits | PDF extraction, authenticity and automatic applicability verification |
| Electrical checks | Declared device-specific FPGA/boot/sequencing, clock, audio/noise/op-amp, current/thermal, decoupling, protection and test-point audits | Automatic native connectivity/geometry extraction for all audits |
| Agents/MCP | Lifecycle gates, typed roles, frozen review/remediation, critical-net coverage, quantified placement | Live model API transport and OS sandbox for arbitrary agent code |
| Manufacturing | Profile/schema rules, native stackup/BOM parity, two-phase manifests, artifact approval, real optional STEP collision and Gerber/PCB rendering | Actual fabrication capability qualification and FreeCAD MCP qualification |
| Verifier MCP | 17 bounded pure-data checks with no source-file or mutation API | Automatic native extraction for every proposed check |
| CI | Python 3.12/3.13 and Fedora real KiCad/ngspice/render/geometry jobs | Reproducible live supplier or GUI server in CI |

FreeCAD 1.1.3 GUI/console and STEP/native round trips are now locally qualified; its MCP
profile remains unqualified. See [FreeCAD setup](freecad.md) and the per-issue
[acceptance audit](issue-acceptance.md), which distinguishes merged code from complete issue scope.

Read [integration qualification](integrations.md) for the exact external tools tested.
The native KiCad fixtures are empty parser/export controls, not fabricated electronics.
Electrical checks assess their declared inputs; independent review must reconcile those
inputs against native design state and manufacturer evidence. Unknown information and
skipped checks never become successful mandatory gates.
