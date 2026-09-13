# Agent lifecycle and independent review

`agents.Lifecycle` implements the prescribed thirteen states from SPEC through RELEASED.
It rejects skipped transitions, inconsistent persisted event chains, stale report hashes
and unknown design authors. Each destination has minimum mandatory gates. Manual gates
require independently signed attestations through the existing release policy engine.
A changed input identity explicitly invalidates prior evidence and restarts at SPEC;
this conservative first version does not guess which earlier approvals can be retained.
The final transition requires a deterministic release-transaction result (M4 coordinator).
Lifecycle records must be stored by a trusted harness; editable JSON alone is not an
authenticated event log and cannot authorize manufacturing.

`config/agents.yaml` is now a validated `agents.roles.Roles` policy. Architect and Reviewer
can only inspect frozen snapshots and their object queries; neither has source mounts,
shell, or the live KiCad transport. Designer gets only the qualified board operations.
The deterministic release role cannot be configured with an LLM. `RoleTools` refuses a
live Designer transport attached to a read role and rejects tools outside the role's
allowlist. The trusted harness owns Python objects: do not execute model-generated
Python in that process. OS-level isolation is required if executing arbitrary agent code.

`independent_review` passes a serialized packet containing frozen source/evidence,
current verification and requested scope to a supplied reviewer harness invocation.
The returned structured review must match the independently selected reviewer, revision,
snapshot and requested scope. Missing evidence becomes a limitation. Even a review with
no findings produces WARN until a separate authenticated approval exists. Passing DRC
never causes automatic approval. The model target is GPT-6 Astra; this module does not
implement or qualify OpenAI API transport, and unit-test reviewers are synthetic callbacks.
A Codex-compatible harness can supply the invocation while preserving the tool boundary.

`remediate` selects stable finding IDs, refuses a stale review, invokes the Designer fix,
then snapshots and runs independent checks through `mutate_verify`. Findings move to
in-progress and require another independent review. No edit or passing DRC automatically
resolves findings. `reconcile` prevents disappearance, identity/severity rewriting and
unsupported transitions; resolved findings require resolution evidence.

Critical-net classification covers power, clocks, differential/high-speed, analog inputs
and outputs, references, switch nodes, feedback, ordinary digital and control. Coverage
checks compare the declared inventory against source net names and require explicit
class-specific review topics on the current snapshot from someone other than the Designer.
Topic coverage is evidence bookkeeping, not an electromagnetic analysis or a signed
release decision. The mandatory critical-net manual gate still requires authentication.

`layout.Floorplan` represents functional rectangles and component anchors. Native KiCad
footprint anchors can be extracted from a snapshot using explicit reference-to-region
assignments. Quantified rules check anchor distance or proximity to an explicitly
rectangular edge. Missing geometry returns SKIP. These are useful locality/floorplanning
constraints for decoupling, clocks, feedback components and connectors; anchor distance
cannot establish pad-loop inductance, courtyard clearance or return-path quality.
