# Review enforcement qualification

The reviewer worker runs through `isolated_review` in the Linux namespace/seccomp
boundary described in [reviewer isolation](reviewer-isolation.md). It receives a frozen
packet over stdin and can return structured findings only. The integration test exercises
a deterministic worker with a known fault; it does not qualify a live GPT transport.
The dedicated CI job requires the isolation boundary rather than silently skipping it.

`remediate` records each incoming independent review in a locked, fsynced JSONL history.
Finding continuity survives process restarts. Three consecutive observations of the same
unresolved blocker/major finding stop automatic mutations. A harness may choose a stricter
positive limit. The harness owns this history outside reviewer/designer capabilities;
the hash chain detects accidental edits and truncation within retained history, but is not
an externally anchored signature against a malicious rewrite of the entire file.

Release now requires an input-hashed `critical_net_plan` file containing `nets` declarations.
The native PCB net inventory must match it exactly. Each critical class requires its
specific topics from `agents/critical_nets.py`, current input digest, independent reviewer,
and no unresolved findings. The CLI accepts external `--critical-net-reviews` JSON/YAML.
Every contributing reviewer must sign a `critical-nets.review` approval containing evidence
`critical-net-reviews-sha256:<digest>`, where digest is `canonical_digest` of
`{"reviews": [each complete NetReview serialized in supplied order]}`. This binds the actual
review payload without creating a self-referential source identity. Missing, stale,
unsigned or changed coverage blocks the mandatory automated gate. An ordinary-digital-only
inventory needs no class-specific review payload; the manual review gate remains mandatory.

Floorplan regions can be hard (failure) or soft (warning). Mechanical anchors always enforce
position and optional orientation tolerances. These are quantified placement checks, not
claims about electrical performance or enclosure collision.

Qualification: `pytest` on Python 3.13 / KiCad 10.0.6 / ngspice 47 / FreeCAD 1.1.3:
137 passed, no skips. `ruff check .` passed. Fixtures cover history continuity, stop-before-
mutation, hard/soft constraints, isolated review, native net inventory and signed-payload
replacement. Manufacturing release tests here use explicitly synthetic approvals/exporters.
