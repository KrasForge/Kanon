# Final local validation, 2026-09-13

M5 working tree on Fedora 44, KiCad CLI 10.0.0, ngspice 47, Gerbonara 1.6.3 and
cadquery-ocp 8.0.1.0.0. Python environments include dev, visual and geometry extras.

| Check | Result |
|---|---|
| Python 3.13.14 `pytest -ra` | 107 passed, 0 skipped, 19.13 seconds |
| Python 3.12.13 `pytest -ra`, isolated rerun | 107 passed, 0 skipped, 18.98 seconds |
| `ruff check .` | All checks passed |
| JSON Schema draft meta-validation | Every schema valid |
| Changed pcb-red-team Skill validator | Skill valid |
| Minimal-board spec validation | 1 PASS, exit 0 |
| Environment diagnostics | 4 PASS, 5 SKIP, exit 2 |
| Verify with no evidence | 18 mandatory gates FAIL, exit 1 |
| Incomplete example BOM through bounded CLI | 1 FAIL, exit 1 |
| Release with no explicit project | ERROR, exit 1 |

The first Python 3.12 run overlapped the 3.13 suite and encountered one external KiCad
DRC timeout: 106 passed, 1 failed. The isolated full rerun above passed. The timeout was
not treated as a successful check. Avoid overlapping native KiCad qualification suites
on the same desktop/configuration environment.

Environment SKIPs are optional FreeCAD and four unconfigured/unprobed example MCP
endpoints. The separately qualified local stdio KiCad server is documented in
[integrations.md](../integrations.md); discovery does not automatically activate it.
Core CI intentionally skips missing native tools/extras. The Fedora integration job
installs KiCad/ngspice and visual/geometry extras and retains actual tool artifacts.

The tests use synthetic engineering limits and parser/export controls. They are not
proof of a populated PCB's electrical, mechanical or manufacturing correctness.
