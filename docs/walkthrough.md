# Design a board with Astra: current entry point

1. Copy templates/design-spec.yaml and replace draft assumptions with measured requirements.
2. Validate structure with `astra-pcb validate examples/minimal-board/design-spec.yaml`.
3. Use electronics-architect to record interfaces, power tree, risks and decisions.
4. Populate component evidence, pin plan and review artifacts. These need engineering review.
5. Run `astra-pcb verify`; the example correctly blocks on missing board checks and approvals.

Schematic construction, placement, routing, independent runtime review and manufacturing
release are not yet wired together. No example KiCad board is supplied. Follow the M1–M4
backlog before extending this walkthrough to claim a complete closed loop.

Optional visual review should capture top/bottom views, readable schematic sheets and 3D
views with source hash, layer visibility, camera orientation and tool version. Inspect
connector orientation, polarity, silkscreen, collisions and routing anomalies. Record
uncertainty/occlusion. Images never replace connectivity, ERC/DRC, calculations or BOM checks.
