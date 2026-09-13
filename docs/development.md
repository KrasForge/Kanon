# Local development

Install Python >=3.12 and uv, then run `uv sync --extra dev` (or create a venv and
`pip install -e '.[dev]'`). Run `uv run pytest` and `uv run ruff check .`.
`uv sync --extra science` enables optional NumPy/SciPy for future numerical workflows.

Install KiCad 10 and ngspice through a trusted platform installer. Put `kicad-cli` and
`ngspice` on PATH; macOS KiCad commonly needs its application binary directory added.
Run `astra-pcb environment` to inspect discovery. FreeCADCmd is optional; the tested official user-local installation is documented in
[FreeCAD setup](freecad.md). Discovery does
not certify supported versions or functional correctness. MCP endpoint presence is reported
without contacting endpoints or printing credentials. Copy .env.example for your harness;
this CLI does not automatically load .env. Never commit credentials.

The selected KiCad MCP installation and five-tool SWIG qualification are recorded in
[integrations.md](integrations.md). The implementation-neutral runtime boundary enforces
explicit tool inventory/capabilities; switching servers requires separate qualification. No tests call OpenAI or supplier services. Run commands from the
repository root; schema/config files are repository assets, not bundled wheel resources.

Unit tests mock process failures or use Python child processes. Integration tests explicitly
skip when external binaries are absent; the separate Fedora CI job installs real KiCad/ngspice and optional rendering/geometry
extras and exercises parser/export/simulation/visual/collision fixtures.
Keep input artifacts separate from outputs. Use disposable directories for export tests.

GitHub CI runs Python 3.12/3.13 unit tests and Ruff; no manufacturing release runs in CI.
Use `uv sync --extra dev --extra visual --extra geometry` for all local integration tests.
See .github/ISSUES.md for exact follow-up scope and dependencies.

## Foundation acceptance

See [foundation contracts](foundation.md) for version migration, units, provenance,
review records, public-key trust policy and opt-in MCP diagnostics. `uv sync --locked
--extra dev` uses the committed resolution. Foundation tests run under Python 3.12 and
3.13, including a local HTTP MCP handshake fixture and signed-approval adversarial tests.
