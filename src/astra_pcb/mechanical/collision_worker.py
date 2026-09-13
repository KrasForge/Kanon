"""Read-only OpenCascade STEP boolean/distance worker; never saves source CAD files."""

import json
import sys
from pathlib import Path


def main():
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_Reader

    config = json.loads(Path(sys.argv[1]).read_text())
    shapes = []
    # STEP reader converts source length units into millimetres; input models must share frame.
    for path in config["files"]:
        reader = STEPControl_Reader()
        if not Interface_Static.SetCVal_s("xstep.cascade.unit", "MM"):
            raise ValueError("Cannot establish millimetre transfer units")
        if reader.ReadFile(path) != IFSelect_RetDone or reader.TransferRoots() < 1:
            raise ValueError("STEP read/transfer failed")
        shape = reader.OneShape()
        if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
            raise ValueError("Invalid BREP")
        volume = GProp_GProps()
        BRepGProp.VolumeProperties_s(shape, volume)
        if volume.Mass() <= 0:
            raise ValueError("Solid volume required; open surface cannot prove collision freedom")
        shapes.append(shape)
    common = BRepAlgoAPI_Common(*shapes)
    common.Build()
    if not common.IsDone():
        raise ValueError("Boolean intersection failed")
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(common.Shape(), properties)
    distance = BRepExtrema_DistShapeShape(*shapes)
    distance.Perform()
    if not distance.IsDone():
        raise ValueError("Distance computation failed")
    Path(config["output"]).write_text(
        json.dumps({"overlap_mm3": properties.Mass(), "clearance_mm": distance.Value()})
    )


if __name__ == "__main__":
    main()
