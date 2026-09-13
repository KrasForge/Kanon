# KiCad closed-loop qualification

KiCadCLI supports major version 10 only and invokes the independent executable without a
shell. Existing output paths (including symlinks) are rejected. Missing inputs/tools,
unsupported versions, timeouts, mutated source and empty/missing exports are errors.
Each execution captures command, exit code, stdout/stderr, tool version, source digest,
artifact paths and artifact hashes. Timeout output is retained. Project-level identity
must additionally include project settings, hierarchies and libraries through Snapshot;
the command's source digest alone covers only its direct design file.

`interpret` validates actual KiCad ERC/DRC JSON, source identity, version, report hash and
all severity categories. Unconnected items and parity findings are included; exclusions
and ignored rules are visible warnings. A caller may supply an explicit approved ignored-rule
set, which must be part of project policy. Unknown report structures fail closed. Parity is
an explicit DRC option. Verification never requests source-saving or zone-refill flags;
the Designer must persist current zone fills before independent verification.

Exports cover Gerbers with explicit optional layer selection, Excellon drills, STEP,
schematic BOM and netlist hooks. M4 performs fabrication-layer consistency and release
manifest validation; an export receipt is not a manufacturing approval.

## Snapshot and capability boundary

`capture(root, paths, revision)` stores exact UTF-8 source content and hashes, parses native
S-expressions and supports object inspection/diffs. Include all schematic hierarchy,
project, rule, symbol/footprint library and relevant configuration files in `paths`.
The snapshot schema validates document content against identity on every load. Raw source
preserves information not yet normalized into electrical models; geometry queries are
not an electrical connectivity solver. External binary models need manifest handling in M4.

DesignerTools maps audited logical operations to named tools through a transport protocol.
The stdio implementation performs MCP 2025-06-18 initialization and bounded JSON-RPC calls.
Unknown/missing server tools cause startup refusal; WRITE calls require explicit dispatch
permission. Unsolicited messages, unsupported versions and tool errors are rejected.
This intentionally restricted client does not support prompts, sampling or notifications.
Other transports can implement the same request protocol without changing core operations.

ReviewerTools is a separate snapshot-only implementation. It contains no MCP transport,
source path, shell or mutation tool. Its entire callable surface is snapshot.read and
snapshot.objects; returned data is copied from serialized, identity-checked content.
The model must receive only that surface. The M3 harness additionally controls process,
credential and filesystem isolation; exposing arbitrary Python or shell would defeat it.

`mutate_verify` records before/after snapshots, invokes a persistence callback, independently
runs applicable ERC/DRC and writes snapshot/report artifacts into a fresh directory.
Changed input identity invalidates previous evidence. The callback must complete the
selected MCP's save/readback operation; MCP success alone never satisfies verification.

## Tests and limits

Local KiCad 10.0.0 and the Fedora 44 CI job exercise empty/ERC and outline/DRC controls,
a deliberately broken outline, Gerbers, drill and STEP generation. These are parser/export
controls, not example electronics or fabrication-ready boards. Unit fixtures cover all
report statuses, ignored/excluded checks, unknown tools and forbidden reviewer mutations.
A real local stdio fixture exercises protocol transport without depending on a particular
third-party KiCad MCP installation. No live editing server is configured on this checkout.

Use `astra-pcb check-kicad --schematic design.kicad_sch --board design.kicad_pcb
--output artifacts/new-invocation` for fresh checks and structured execution receipts.
Add `--parity` for schematic/PCB parity. Output directories must not already exist. The
aggregate report intentionally lacks a complete project identity until all referenced
project/library inputs are captured by the workflow; it cannot satisfy signed release gates.
