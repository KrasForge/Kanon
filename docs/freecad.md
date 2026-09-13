# FreeCAD installation and qualification

The official [FreeCAD 1.1.3 Linux x86_64 AppImage](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3)
was installed on this Fedora 44 host on 2026-09-13. The native Fedora package was unavailable,
so installation uses the upstream binary distribution documented on the
[FreeCAD download page](https://www.freecad.org/downloads.php).

Installed location: `/home/ik/.local/share/kanon/integrations/freecad-1.1.3/`.
The AppImage is extracted into `squashfs-root` to avoid a FUSE runtime dependency. Its
SHA-256 was checked against GitHub's official release asset digest before execution:
`3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef`.
The installation has a local provenance receipt; binaries are outside the Git repository.

Launch `FreeCAD` (or `freecad`) for the GUI; `FreeCADCmd` (or `freecadcmd`) for the console.
User-local launchers in `~/.local/bin` invoke the upstream AppRun script with the correct
bundled runtime. A user-local desktop entry named **FreeCAD 1.1.3** is installed. No existing
launcher or project was overwritten. Put `~/.local/bin` on PATH if a new shell omits it.

## Reproduce and verify

Download the x86_64 asset from the release above, verify its SHA-256, mark it executable
and run `./FreeCAD.AppImage --appimage-extract` in a new installation directory. GUI entry
point: `squashfs-root/AppRun freecad`. Console entry point:
`squashfs-root/AppRun freecadcmd`. Keep the extracted directory intact.

`FreeCADCmd --version` reports **1.1.3, revision 20260725**. The GUI opened and exited normally
in an isolated Xvfb display with separate configuration files. It printed host-font parsing
warnings; those did not prevent startup. The user's desktop/session was not used.

`uv run pytest tests/test_freecad.py -ra` exercises the actual installed executable. It
creates a disposable 10 × 10 × 1.6 mm solid, saves/reopens an FCStd document, exports/imports
STEP and confirms validity and 160 mm³ volume. The test requires its success receipt
because FreeCAD can print a Python exception while still exiting zero. It uses safe mode
and isolated configuration files; no design source is mutated. Hosts without FreeCAD
explicitly skip this optional integration test.

## Optional MCP qualification

The [neka-nat provider](https://github.com/neka-nat/freecad-mcp) is now installed separately
at `~/.local/share/kanon/integrations/freecad-mcp`, pinned to
`5dbfe2c80b53c3102bff0723951676e16edf2d84` (0.1.23). Its checked-in upstream `uv.lock`
was used with `uv sync --locked --no-dev --python 3.13`. No unpinned `uvx` launch is used.
The profile pins all 17 advertised tool schemas, but exposes only create document/object
and read object/object-list operations to Designer. `execute_code`, headless scripts,
FEM and library insertion remain outside that exposed subset. Arbitrary code was used
only by the deployment-owned qualification probe to save and independently inspect a
synthetic solid. No provider prompt is imported as project policy.

Reproduce with the audited checkout and installed FreeCAD/Xvfb:

```sh
uv run python scripts/qualify_freecad_mcp.py "$KANON_FREECAD_MCP_ROOT" /tmp/new-freecad-probe
```

This script refuses an occupied RPC port, uses a fresh GUI/configuration, binds only
127.0.0.1:9875, performs MCP create/readback, saves FCStd and STEP, and checks native
shape validity and 160 mm³ volume. The initial qualification found a startup modal blocked
GUI dispatch; the probe dismisses startup UI only in its own empty disposable session.
It also checks the provider's `null` response for a nonexistent object. The adapter treats
that response as an error, checks returned identity/dimensions and never trusts text success.
The installed server and addon shut down after the probe. Missing/offline endpoints time
out rather than producing successful check evidence.

`config/integrations/freecad.example.json` records the inventory hash, read/write mapping
and optional launch configuration. Environment substitution is performed by the deployment
launcher, not by passing a literal `${...}` argument to subprocess. RPC is unauthenticated:
use a private local session; do not enable remote connections or expose it on a shared host.
This is application/configuration isolation, not a sandbox for arbitrary CAD Python. Reviewer
receives **no FreeCAD transport** and inspects immutable STEP/snapshots through the required
read-only boundary. Review and manufacturing approval remain separate.

The qualification receipt is in `config/integrations/freecad-mcp-qualification.json`;
artifact hashes identify the local disposable run, not distributable fabrication outputs.
The independent OpenCascade collision adapter remains available without FreeCAD.
