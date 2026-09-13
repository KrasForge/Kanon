# Architecture and trust boundaries

The target lifecycle is SPEC → ARCHITECTURE → COMPONENT_SELECTION → SCHEMATIC →
SCHEMATIC_REVIEW → FLOORPLAN → CRITICAL_ROUTING → GENERAL_ROUTING → PCB_REVIEW → DFM →
MECHANICAL → RELEASE_REVIEW → RELEASED. PCB_REVIEW includes power/return-path review;
RELEASE_REVIEW includes Gerber inspection. Lifecycle enforcement is backlog work.

Architect decomposes requirements, power/signal/clock trees and risks. Designer owns source
mutations via a selectable KiCad MCP implementation. Reviewer tries to invalidate a frozen
snapshot using read-only design/evidence access. Release tooling evaluates deterministic
checks and revision-bound independent approvals. No generative result is verification.

## Boundaries
MCP config is an application contract, not a directly installable Codex MCP file. A future
harness must map explicitly audited tools to READ/WRITE capabilities, deny unknown tools,
and refuse startup when reviewer isolation cannot be enforced. Reviewer allowlists are
empty by default. Do not give reviewer the designer server, generic shell, scripting,
filesystem-write or MCP passthrough tools. Read-only source mounts and separate credentials
are required beyond prompt policy. IPC access is optional behind the same adapter boundary.
M1 adds an audited stdio client and a separate snapshot-only reviewer surface;
no multi-agent model runtime is implemented yet.

## Verification semantics
CheckStatus describes execution/conclusion; severity describes engineering impact. PASS,
FAIL, WARN, SKIP and ERROR remain distinct in input reports. Exit codes: 0 all PASS;
1 failure/error or empty report; 2 warnings/skips only. Gate evaluation requires every
mandatory automated check to PASS; WARN/SKIP/missing also block. Manual gates require Ed25519-signed, revision-bound independent approvals.
Waivers require an explicitly trusted human signer and per-gate permission (disabled by
default). Private signing keys are external to agent tools; see foundation.md. An imported JSON PASS is untrusted aggregation input, not release proof.

KiCad command hooks capture exit status/output/artifacts, refuse existing export targets
and never turn missing executables into success. M1 parses JSON violations and qualifies KiCad 10, captures export hashes and provides
persisted-source snapshots. Complete fabrication validation remains in M4. ngspice
supports process capture and scalar `.measure` parsing; circuit workflows and validated
models remain pending. BOM checks are offline and do not establish live stock or suitability.

## Evidence and release
Future snapshots must bind source/library/model/config hashes, dirty-tree content, tool
versions, simulation inputs, decisions and report identities. Every mutation invalidates
affected evidence. Release must run fresh checks, export into a new directory, validate all
expected layers/drills/BOM/placement/STEP artifacts, hash a manifest, and obtain independent
review. Generated files alone are insufficient. No release bundle is currently produced.

## Sources checked during initialization
- [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html): command syntax reference.
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra): target model;
  deployment access and harness support must be established locally. No model calls here.
