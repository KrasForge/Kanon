"""Optional FreeCAD MCP operations through an audited tool mapping.

This facade is Designer-only; Reviewer receives immutable STEP/snapshots instead.
"""

import json

from astra_pcb.kicad.mcp import DesignerTools


class FreeCADTools:
    def __init__(self, tools: DesignerTools):
        self.tools = tools

    def read_object(self, document: str, name: str) -> dict:
        response = self.tools.call(
            "mechanical.object.read",
            {"doc_name": document, "obj_name": name, "include_screenshot": False},
        )
        values = [
            json.loads(c["text"]) for c in response.get("content", []) if c.get("type") == "text"
        ]
        if len(values) != 1 or not isinstance(values[0], dict) or values[0].get("Name") != name:
            raise ValueError("Missing, malformed or mismatched FreeCAD object")
        return values[0]

    def create_box(
        self,
        document: str,
        name: str,
        *,
        length_mm: float,
        width_mm: float,
        height_mm: float,
        allow_write: bool = False,
    ) -> dict:
        import math

        if not all(math.isfinite(v) and v > 0 for v in (length_mm, width_mm, height_mm)):
            raise ValueError("Positive finite dimensions required")
        self.tools.call(
            "mechanical.object.create",
            {
                "doc_name": document,
                "obj_name": name,
                "obj_type": "Part::Box",
                "obj_properties": {"Length": length_mm, "Width": width_mm, "Height": height_mm},
                "include_screenshot": False,
            },
            allow_write=allow_write,
        )
        result = self.read_object(document, name)
        properties = result.get("Properties", {})
        for key, expected in (("Length", length_mm), ("Width", width_mm), ("Height", height_mm)):
            value = properties.get(key)
            if (
                not isinstance(value, str)
                or not value.endswith(" mm")
                or abs(float(value[:-3]) - expected) > 1e-8
            ):
                raise ValueError("FreeCAD readback does not match requested dimensions")
        return result
