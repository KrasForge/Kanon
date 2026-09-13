# Selected integrations and qualification boundaries

Kanon selects [mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server)
2.7.0, commit `ac716d1a8bfad325b4aa93a398222645b3f78fd7`, as the initial external
Designer MCP. It is MIT licensed, provides schematic and PCB editing, and can use
SWIG or an experimental IPC backend. Kanon's successful local qualification covers
only SWIG board open/read, trace creation, save and backend identification on KiCad
10.0.0. Schematic editing, interactive IPC and all other server tools need separate
qualification. The server's own success and DRC claims are not release evidence.

The test added one isolated trace to a disposable outline fixture. Native readback
found the saved segment; independent `kicad-cli` DRC correctly reported its dangling
end and unapproved ignored rules. This is a negative integration control, not a board.

`config/integrations/qualification.json` records the source revision, tool inventory,
qualified operations and dependency digests. The original npm lock had six vulnerable
runtime dependencies. The qualified lock includes compatible security updates and
`npm audit --omit=dev` reported zero findings. The deployment manifest excludes the external development/test servers and retains
only runtime dependencies plus TypeScript build dependencies; its complete npm audit
also reports zero findings. The Python runtime lock excludes pip (installation uses uv).

## Reproduce the installation

Install Node.js and the Python that can import the installed KiCad `pcbnew` module.
For Fedora this is system Python, not necessarily Kanon's uv Python.
Clone the repository into an external installation directory and detach at the commit
above. Copy `config/integrations/kicad-mcp-package.json` over its package.json and
`config/integrations/kicad-mcp-package-lock.json` over its package-lock.json,
then run `npm ci --ignore-scripts` and `npm run build` in that external checkout.
Create its `venv` with `python3 -m venv --system-site-packages venv` and install
`config/integrations/kicad-mcp-requirements.txt` using `uv pip install --python venv/bin/python`.
Check the runtime dependency audit again when installing.

Set `KANON_KICAD_MCP_ROOT` to the checkout. The launch command is:

```sh
KICAD_BACKEND=swig KICAD_AUTO_LAUNCH=false KICAD_MCP_LOG_LEVEL=error \
  node "$KANON_KICAD_MCP_ROOT/dist/index.js"
```

The host installation is `/home/ik/.local/share/kanon/integrations/kicad-mcp`.
Do not commit host-specific configuration or credentials. `config/integrations/kicad-mcp.json`
is a Kanon capability profile; `${KANON_KICAD_MCP_ROOT}` must be expanded by the launcher.
The MCP tool inventory must match the pinned digest. Only the five listed operations
are exposed by DesignerTools; all other server tools remain unavailable through that facade.
Raw transport access belongs to the trusted harness, never the Reviewer.

The server responds to MCP initialize before its Python backend is ready. Read-only
backend probes may temporarily report `isError`; a harness must bound its readiness
wait and must never retry a mutation automatically. On Fedora `xvfb-run` merges stderr
into stdout and corrupts MCP framing. Use a separately started Xvfb for isolated tests.
Reviewer receives frozen snapshot tools only and never launches this server.

## Sourcing

The default credential-free source is [JLCSearch](https://github.com/tscircuit/jlcsearch),
a public JLCPCB catalog mirror based on jlcparts. `astra-pcb source-part C21190
--expected-mpn 0603WAF1001T5E` performs an exact supplier-code lookup and refuses a
mismatched MPN. It exposes reported stock, package and Basic/Extended classification.
Raw price tiers are retained as unqualified evidence because this endpoint omits
currency. Manufacturer identity and stock observation age also remain unknown.
Fetching a mirror today does not prove its inventory was updated today. The lookup
therefore returns WARN (exit 2), never manufacturing sourcing approval.

Use the actual supplier before procurement. The [official LCSC API](https://www.lcsc.com/docs/openapi/index.html)
requires an account key and signed requests. No account key is configured here;
Kanon does not pretend this account-gated path was exercised. A normalized supplier
MCP adapter remains available behind the same canonical record boundary. Credentials
must be supplied through environment variables in an external launcher. Neither
adapter orders components, uploads designs or silently substitutes alternates.

## Independent credential-free alternative: Adafruit

`astra-pcb source-part 2821 --provider adafruit --expected-mpn ADA2821` uses the
[public product API](https://www.adafruit.com/api/products/2821) without an account, token
or API key. Adafruit documents public catalog access in its
[product viewer guide](https://learn.adafruit.com/pyportal-new-new-new-product-viewer?view=all).
This is a different supplier from LCSC/JLCPCB, useful for modules, connectors and stocked
components. It does not provide the entire LCSC catalog or JLCPCB assembly classifications.

The adapter checks exact supplier product ID and optional expected MPN, preserving the
manufacturer's returned MPN separately from the product ID. It refuses missing/mismatched
MPNs and malformed responses. Numeric inventory is retained; text such as `in stock` is
availability text with unknown quantity. The response does not establish package, lifecycle,
price currency or inventory update time, so these stay unknown and lookup returns WARN.
Raw price tiers and lifecycle text are evidence, not qualified purchase data. No HTML
description is interpreted as instructions or automatically extracted electrical limits.

The source-neutral SourcingRecord accepts different supplier IDs while retaining the
C-prefixed-ID requirement for LCSC/JLCPCB. Existing JLCSearch commands remain compatible.
All network reads are bounded, reject redirects and have explicit failure results.
Contract tests use a reduced response observed on 2026-09-13; live stock is never a CI
assertion. Neither provider requires credentials, substitutes parts, uploads designs or orders.


## KiCad 10.0.6 requalification

After updating the host from KiCad 10.0.0 to 10.0.6, the same pinned SWIG provider again
opened a disposable board, read state, added one trace, saved and produced a native file
containing exactly one segment. Independent CLI verification reported the deliberately
unassigned/dangling trace and ignored-check warnings; mutation success did not become
verification PASS. This requalification does not cover IPC or schematic editing.
