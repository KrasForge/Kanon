# Manufacturing release

Release is a local, deterministic two-phase transaction. It never orders boards or
uploads design files. The coordinator executes its own ERC/DRC, native BOM parity and
other mandatory checks; it does not accept an LLM's automation-result JSON as proof.

## Required inputs

Provide a `ReleaseProject` YAML file with project-relative schematic, PCB, canonical BOM,
specification, manufacturing profile and additional local evidence/library/model paths.
Native hierarchical design and local library/model files beneath the schematic/PCB
directories are included in the identity. Freeze external 3D models locally; unresolved
environment or outside-project model references block release. Include datasheets,
simulation results, decisions and mechanical evidence in `additional_inputs` when they
underlie the review. Keep generated artifacts outside these input directories.

`astra-pcb release --project project/release.yaml --identity-only` prints the exact Git
revision and SHA-256 input map for independent review/approval. Dirty inputs are bound
by their actual bytes, not assumed equal to HEAD. A change to any bound input invalidates
its approvals. Trust policy, verifier code and signing keys belong to the trusted harness;
Designer cannot replace them or choose an alternative check executor. The public CLI
exposes no arbitrary shell check or fake exporter option. Python API dependency injection
exists for testing and is not exposed to model tools.

A manufacturing profile starts UNQUALIFIED. QUALIFIED requires dated evidence of current
fabricator capabilities and independent DFM review; old/future dates fail. Native layer
count and board thickness must match the declared profile, and all native copper layers
must be exported. Detailed copper weights, Dk, package/assembly suitability and soldermask
process still require the independent profile/DFM review. The example JLCPCB profile is
not automatically qualified. `check_dfm` can compare explicit measured features to its
minimum trace/spacing/drill/annular-ring/edge/mask constraints; it does not extract all
manufacturing geometry automatically.

BOM parity compares populated native reference/value/footprint IDs with the per-reference
BOM and refuses an empty product. Excluded-from-BOM/DNP footprints are omitted. The
canonical `package` used for this check is the native footprint ID, not an inferred body
size. Schematic/PCB parity is mandatory through KiCad 10 DRC. Device electrical and
mechanical suitability still require cited independent review.

## Prepare, inspect, finalize

```sh
astra-pcb release --project project/release.yaml --root . \
  --gates config/release-gates.yaml --reviews reviews.json \
  --attestations input-approvals.json --trusted-signers trusted-public-keys.json \
  --output artifacts/release-candidate
```

The supplied reviews must match the input digest/revision, come from an independent
reviewer and have no unresolved blockers/major findings or limitations. Mandatory manual
gates require externally signed approvals. Mandatory warnings, missing/skipped/error
checks block preparation. Explicit human waivers are honored only for gates configured
to allow them; raw failing results remain in verification evidence. No tool here creates
signatures or provides agent access to signing keys.

If input gates pass, prepare exports Gerbers, Excellon drills, STEP and optional millimetre
pick-and-place CSV to fresh paths. It checks receipts, hashes, expected layers, X2 layer
identity, file envelopes and current source identity. It writes a **candidate-manifest.json**
and returns WARN/exit 2 pending review of the actual generated artifacts. A STEP envelope
check proves file identity/existence, not collision freedom or completeness of 3D models.

Inspect the actual Gerbers, drills, PnP, STEP and all release evidence. The candidate's
approval identity is `canonical_digest(candidate.model_dump(mode="json"))` using the
`Manifest` model. Obtain separate signed approvals for `gerber.review` and
`review.final-artifacts` against that identity, then:

```sh
astra-pcb release --finalize --root . --output artifacts/release-candidate \
  --attestations artifact-approvals.json --trusted-signers trusted-public-keys.json
```

Finalize rechecks every candidate artifact, source hash, Git revision and authenticated
artifact approvals. Success writes a new final report and **manifest.json**; prepared
artifacts remain unchanged so the signed candidate is independently auditable. A final
manifest explicitly lists schematic, PCB, Gerbers, drills, BOM, STEP, reviews, verification,
manufacturing profile, Git revision, hashes, and PnP when requested. Missing or altered
artifacts fail verification. Preserve failed invocation directories for diagnosis; do not
reuse them as fresh output targets. A candidate manifest alone is not a release.

## Visual and mechanical evidence

`manufacturing.visual.render_layers` uses optional Gerbonara 1.6.3 in a bounded subprocess
with explicit layer mappings to render actual Gerber geometry to SVG. Install with
`uv sync --extra dev --extra visual`. Local qualification rendered KiCad 10 X2 files with
no parser warnings. The alternative gerbv adapter preserves warnings/errors; installed
Gerbv 2.10 reported unsupported X2 metadata and is not the qualified default path.
Vision supplements connectivity, electrical calculations, ERC/DRC and BOM checks.

`MechanicalConstraints` records outline, keep-outs, mounting holes, connector locations,
height limits, enclosure hashes and coordinate frame. The optional FreeCAD MCP profile
selects neka-nat/freecad-mcp and remains disabled/unqualified until its addon and FreeCAD
are available. Fedora's configured repositories on this host had no `freecad` package.
The Reviewer never receives that mutation-capable server. STEP export has been exercised
through actual KiCad; a FreeCAD session or collision analysis is not claimed by M4.

The minimal-board example deliberately lacks native board/schematic/BOM files. Its spec
validates, but its release command fails. Unit tests use explicitly synthetic exporters
and signing keys to test successful package/finalization transactions; separate integration
tests exercise real KiCad exports and Gerber rendering. Neither fixture is a product PCB.
