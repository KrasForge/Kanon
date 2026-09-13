# Kanon / Astra PCB

An evidence-driven foundation for an agentic PCB engineering workbench targeting GPT-6
Astra, KiCad 10, MCP and deterministic verification. This repository does not yet design
boards autonomously or authorize manufacturing release.

Implemented: typed reports and signed release-gate decisions; schema/semantic validation;
independent KiCad ERC/DRC and export receipts; a qualified external MCP board-editing path;
real ngspice assertions and ideal circuit workflows; BOM import and public sourcing lookup;
a local datasheet registry; declared power, FPGA-bank and rule-driven electrical audits;
role-isolated lifecycle/review orchestration and quantified placement constraints.

```sh
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run astra-pcb validate examples/minimal-board/design-spec.yaml
uv run astra-pcb environment
uv run astra-pcb verify
```

Environment returns 2 for missing optional tools/unprobed endpoints. Verify returns 1 with
pending mandatory gates. Release deliberately returns 1 until the full pipeline exists.
A schema-valid specification is not an electrically validated design.

See [capability status](docs/capabilities.md), [architecture](docs/architecture.md), [development](docs/development.md),
[engineering checks](docs/engineering-verification.md), [integrations](docs/integrations.md),
[walkthrough](docs/walkthrough.md), [backlog](.github/ISSUES.md), and [policy](AGENTS.md).
The original MIT LICENSE is preserved.
