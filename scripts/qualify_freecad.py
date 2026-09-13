"""Run with FreeCADCmd, writing only to a new KANON_FREECAD_SMOKE_ROOT directory."""

import json
import os
from pathlib import Path


def main():
    import FreeCAD
    import Part

    root = Path(os.environ["KANON_FREECAD_SMOKE_ROOT"])
    root.mkdir(parents=True, exist_ok=False)
    document = FreeCAD.newDocument("KanonQualification")
    feature = document.addObject("PartDesign::Feature", "BoardEnvelope")
    feature.Shape = Part.makeBox(10, 10, 1.6)
    document.recompute()
    document.saveAs(str(root / "envelope.FCStd"))
    Part.export([feature], str(root / "envelope.step"))
    imported = Part.read(str(root / "envelope.step"))
    if not imported.isValid() or abs(imported.Volume - 160) > 1e-6:
        raise ValueError("STEP export/import volume mismatch")
    FreeCAD.closeDocument(document.Name)
    document = FreeCAD.openDocument(str(root / "envelope.FCStd"))
    if abs(document.getObject("BoardEnvelope").Shape.Volume - 160) > 1e-6:
        raise ValueError("Native document round-trip failed")
    FreeCAD.closeDocument(document.Name)
    (root / "qualification.json").write_text(
        json.dumps(
            {
                "version": FreeCAD.Version(),
                "step_volume_mm3": imported.Volume,
                "native_roundtrip": True,
                "scope": "Synthetic solid only; no PCB or FreeCAD MCP qualification",
            },
            indent=2,
        )
        + "\n"
    )


# FreeCAD executes script files using its own module name rather than __main__.
main()
