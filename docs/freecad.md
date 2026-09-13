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

Application/STEP qualification does not qualify a FreeCAD MCP server. The optional
`neka-nat/freecad-mcp` profile remains disabled and unqualified; provider addon installation,
transport/capability auditing and review isolation remain tracked in #48. Reviewer access
must never include a mutation-capable CAD server. The independent OpenCascade collision
adapter remains available without FreeCAD.

Follow-up validation: Python 3.13.14 and 3.12.13 each passed all **123 tests with zero
skips** (20.48 s and 19.22 s respectively); Ruff passed. Public sourcing contract tests
cover mismatch, offline, malformed inventory and availability-text cases. Live Adafruit
and JLCSearch requests both returned WARN as intended because missing sourcing metadata
is unresolved. Environment diagnostics report five installed tools PASS and four
unconfigured optional MCP endpoints SKIP.
