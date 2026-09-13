# Design a board with Astra

This walkthrough separates working tooling from the engineering work a Designer and
independent Reviewer must supply. The populated software fixture is not a fabrication-ready product.
The Codex-compatible harness supplies model invocation; Kanon provides policy, state,
verification and evidence APIs. Loading model configuration does not run GPT-6 Astra.

1. Copy `templates/design-spec.yaml`, extract requirements and resolve unknown interfaces,
   voltage domains, power/clock/reset/boot/debug and mechanical/manufacturing constraints.
   Run `astra-pcb validate path/to/spec.yaml`. Validation checks declared structure/semantics;
   independent requirements approval establishes completeness for the intended product.
2. Use `skills/electronics-architect/SKILL.md` to build the architecture, rail/load model,
   clock/reset tree, risks and decisions. Register source documents with `datasheets.Registry`
   and cite pages/sections. Record calculations and what would invalidate each decision.
   Advance `agents.Lifecycle` only with the required current signed gate evidence.
3. Select manufacturer parts, packages and explicit compatible alternates. Import/check the
   canonical BOM and inspect sourcing risk. `astra-pcb source-part C21190` demonstrates a
   real mirror lookup, not approval of that part for a circuit. Unknown stock age and
   manufacturer/currency information remain explicit; do not silently substitute parts.
4. The Designer constructs the schematic in KiCad or through a separately qualified MCP
   schematic path. The selected server's schematic tools are not yet qualified/exposed by
   the narrow default Kanon profile. Use `astra-pcb check-kicad --schematic board.kicad_sch
   --output artifacts/erc-1` for independent ERC. Build a frozen review packet with native
   state, BOM, decisions, documents and relevant simulations. Reviewer seeks counterexamples
   and returns structured findings; passing ERC never auto-approves the schematic.
5. Define floorplan regions and component assignments. Read native footprint anchors,
   check explicit distance constraints and place before routing. Classify every net;
   route/review critical nets before ordinary signals. The qualified Designer MCP supports
   board open/read, a trace operation, save and backend state. Wrap persistent mutations
   in `kicad.workflow.mutate_verify`; it captures state and runs independent ERC/DRC.
6. Use power/current/thermal, bank, decoupling, protection and test-point audits on declared
   inputs reconciled against the frozen design. Run simulation jobs where an applicable
   model exists. Example filter and supply-impedance jobs are ideal infrastructure controls,
   not vendor regulator/codec models. Independently review return currents, planes, switching
   loops, analog references, clocks and critical nets; do not cargo-cult split ground planes.
7. Apply fixes through the finding-preserving remediation loop, reverify, and obtain another
   independent review. Never let a finding disappear or resolve solely because a write or
   DRC invocation succeeded. Record mechanical and DFM reviews against the actual revision.
8. Qualify the manufacturing profile and follow [the two-phase release procedure](manufacturing-release.md).
   Prepare runs mandatory checks and exports a candidate; review actual fabrication artifacts
   before signed finalization. The final manifest records exact source/artifact hashes and
   Git revision. Ordering boards is always a separate explicit action.

The reproducible CI example covers spec validation, checks, export integrity, manifest
contracts and blocked release behavior. It does not demonstrate autonomous end-to-end PCB
design or eliminate engineering judgment. See [capabilities](capabilities.md) for limits.

## Reproducible populated integration path

The [populated coupon](../examples/populated-fixture/README.md) now exercises native
schematic → routed PCB → independent CLI checks → actual Gerber/drill/STEP/placement
exports → blocked candidate → signed finalization. Run
`uv run pytest tests/test_populated_release.py -v`. Native source files, library tables,
courtyards, 3D geometry and net classifications are committed for inspection. The test
uses a temporary repository and explicitly synthetic manufacturing/review approvals;
it does not ask an LLM to approve its own physical design.

For a real project, follow steps 1–8 above with real component/data evidence and separate
review principals. Supply a `critical_net_plan` covering native net names, an assembly
plan for package/side/courtyard/polarity/placement checks, and all assigned 3D model files
inside the input identity. Model omissions require explicit per-reference rationale.
STEP export uses a fixed 0 × 0 mm native-board origin and millimetre length units. Coordinate
transform into an enclosure remains a reviewed mechanical constraint.

The optional FreeCAD MCP subset can construct/read primitive geometry in an explicitly
selected local Designer session; see [qualification](freecad.md). It is not passed to
Reviewer. A full model-driven schematic authoring/routing session still requires the
Codex-compatible deployment harness and its independently qualified tool capabilities.
