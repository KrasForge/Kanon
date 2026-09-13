# Kanon / Astra PCB

An evidence-driven foundation for an agentic PCB engineering workbench targeting GPT-6
Astra, KiCad 10, MCP and deterministic verification. This repository does not yet design
boards autonomously. Manufacturing release requires deterministic checks and independent
signed input/artifact approvals.

Implemented: typed reports and signed release-gate decisions; schema/semantic validation;
independent KiCad ERC/DRC and export receipts; a qualified external MCP board-editing path;
real ngspice assertions and ideal circuit workflows; BOM import and credential-free JLCSearch/Adafruit sourcing lookups;
a local datasheet registry; declared power, FPGA-bank and rule-driven electrical audits;
role-isolated lifecycle/review orchestration and quantified placement constraints;
a two-phase release coordinator with content-addressed manifests and Gerber rendering;
advanced audio/FPGA/clock checks, optional solid collision analysis, PCB renders and a
read-only verifier MCP exposing 17 implemented checks.

```sh
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run astra-pcb validate examples/minimal-board/design-spec.yaml
uv run astra-pcb environment
uv run astra-pcb verify
```

Environment returns 2 for missing optional tools/unprobed endpoints. Verify returns 1 with
pending mandatory gates. Release requires an explicit project; package preparation returns 2 until artifact approval.
A schema-valid specification is not an electrically validated design.

See [capability status](docs/capabilities.md), [architecture](docs/architecture.md), [development](docs/development.md),
[engineering checks](docs/engineering-verification.md), [advanced checks](docs/advanced-engineering.md),
[verifier MCP](docs/pcb-verifier.md), [integrations](docs/integrations.md),
[walkthrough](docs/walkthrough.md), [backlog](.github/ISSUES.md), and [policy](AGENTS.md).
The original MIT LICENSE is preserved.
