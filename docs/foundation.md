# Foundation contracts and operation

## Design inputs and units

The canonical specification is schemas/design-spec.schema.json. Numeric field suffixes
are units: V, A, Hz, ps and °C; monetary values require currency and quantity. Unknown
properties and wrong types are rejected. Semantic validation rejects nonfinite values,
inverted rail/environment ranges, nominal voltages outside limits, duplicate IDs, unknown
rail dependencies/interface voltage domains, forbidden selected parts and supply cycles.
`rails[].source` identifies the upstream rail; regulator/load details belong in the power
model introduced in M2. Input sources may refer to named external supplies. Physical
suitability, device-family rules and requirement truth need separate engineering checks.

Draft 0.1 specifications migrate the `requirements` field to `functional_requirements`
and version 1.0 without mutating caller data. Missing fields still fail. Ambiguous legacy
fields and unknown future versions are rejected. Current templates are already 1.0.

## Reports, decisions and reviews

Reports support 1.0 import and 1.1 metadata: unique report ID, timezone-aware timestamp,
input digest, design-author identity and tool versions. Legacy data is preserved; absent
identity is not invented. InputIdentity hashes named files and the revision into a stable
aggregate digest. `verify --identity identity.json --root project/` recomputes file hashes
and rejects missing, changed or escaping paths. Verification result statuses remain intact
in the input report; gate verdicts explain why a result satisfied or blocked policy.

Decision has required alternatives, exact datasheet evidence and invalidation conditions.
Its Markdown format includes a canonical JSON block for lossless round-trip; editing the
rendered prose alone does not change the canonical record. Review findings keep stable IDs
across explicit open/in_progress/resolved/accepted transitions. Resolutions and accepted
risks require evidence; unresolved major/blocker findings or limitations still block review.
An accepted risk is not itself a release waiver. JSON Schemas are generated from these models.

## Signed independent approvals and waivers

`astra-pcb verify --report report.json --identity identity.json --root project/`
can additionally read `--attestations attestations.json --trusted-signers trusted.json`.
Attestations are a JSON array; trusted signers map an issuer name to
`public_key_base64` (raw 32-byte Ed25519 public key) and roles (`reviewer`, `human`).
No private key or signing command is supplied by this package. Operators must provision
public trust policy outside designer-controlled files and keep private keys in an external
human review/signing service. A deployed release worker must enforce that separation.

Sign UTF-8 JSON from `Attestation.payload()`: sorted keys, compact separators, all fields
except signature_base64, timestamps as Pydantic JSON encodes them. Include issuer, purpose
(approval/waiver), exact check_id, input_digest, reason, evidence, issued_at and expires_at.
Manual approval requires a reviewer distinct from the report's known design_author.
A waiver requires a human role and `allow_human_waiver: true` on the individual gate.
Default policy enables no waivers. Invalid signatures, stale identity, future/expired
records, unknown issuers, duplicates or mismatched gate purposes fail closed. Audit output
includes the exact attestation and reason. This verifies an attestation's origin and scope,
not whether an electrical claim is true. M4 must bind this engine to trusted execution.

## Environment diagnostics

`astra-pcb environment` discovers Python >=3.12, Git >=2, KiCad major 10, ngspice >=42,
and optional FreeCAD >=1. Missing optional tools are SKIP; present but unsupported tools
FAIL, and process errors ERROR. These ranges describe adapter qualification targets.

`--probe-mcp` performs a bounded opt-in HTTP initialize/initialized exchange for protocol
2025-06-18. Configured but unprobed endpoints are SKIP. Remote endpoints require HTTPS;
loopback HTTP is permitted. Environment variables NAME_MCP_URL and optional NAME_MCP_TOKEN
supply endpoints/tokens. Credentials and endpoint response bodies are omitted from errors;
redirects are rejected. JSON and single-line SSE initialization responses are supported.
Other protocols/transports are reported unsupported, not silently passed. A successful
handshake does not qualify a server's editing tools.

Protocol references:
- https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle
- https://modelcontextprotocol.io/specification/2025-06-18/basic/transports

Decision link verification uses `models.decision_links.validate_links(decision, root, registry)`.
Citation source paths or canonical registry URLs must match document title/manufacturer/revision
and SHA-256. Calculation Markdown links resolve to local project artifacts and record their
hashes; missing files, path escapes and remote calculation links fail. This validates evidence
identity and link targets, not the correctness of the cited electrical interpretation.
The decision-link regression covers valid round-trip, missing calculation artifacts,
path traversal and a changed registered document. URL citations are matched to local
registered documents; validation does not fetch arbitrary remote URLs.
