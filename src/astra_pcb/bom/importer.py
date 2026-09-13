"""Explicit canonical/KiCad CSV column mapping, reference expansion and normalization."""

import csv
import json
import re
from pathlib import Path

from astra_pcb.bom import BOMItem

COLUMNS = {
    "Reference": "reference",
    "References": "reference",
    "Qty": "quantity",
    "Quantity": "quantity",
    "Value": "value",
    "Footprint": "package",
    "Manufacturer": "manufacturer",
    "MPN": "mpn",
    "LCSC": "supplier_part_number",
}


def import_bom(path: Path, columns: dict[str, str] | None = None) -> list[BOMItem]:
    if path.suffix.lower() == ".json":
        rows = json.loads(path.read_text())
        if not isinstance(rows, list):
            raise ValueError("Canonical BOM JSON must be an array")
    else:
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("Missing or duplicate CSV columns")
            mapping = {name: (columns or COLUMNS).get(name, name) for name in reader.fieldnames}
            if len(set(mapping.values())) != len(mapping):
                raise ValueError("Ambiguous column mapping")
            rows = []
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("CSV row has wrong number of fields")
                rows.append({mapping[k]: v for k, v in row.items()})
    result = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"BOM row {index} is not an object")
        clean = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
        if not isinstance(clean.get("reference"), str):
            raise ValueError("BOM reference must be text")
        references = re.split(r"[,\s]+", clean.get("reference", "").strip())
        if not all(references):
            raise ValueError(f"BOM row {index} lacks references")
        raw_quantity = clean.get("quantity")
        if raw_quantity not in (None, "") and not re.fullmatch(r"[1-9]\d*", str(raw_quantity)):
            raise ValueError("BOM quantity must be a positive integer")
        quantity = int(raw_quantity) if raw_quantity not in (None, "") else len(references)
        if len(references) > 1 and quantity != len(references):
            raise ValueError(f"BOM row {index}: quantity does not match expanded references")
        for reference in references:
            item = {
                **clean,
                "reference": reference,
                "quantity": 1 if len(references) > 1 else quantity,
            }
            for name in [
                "mpn",
                "manufacturer",
                "supplier",
                "supplier_part_number",
                "stock",
                "unit_cost",
                "assembly_classification",
                "lifecycle",
                "currency",
            ]:
                if item.get(name) == "":
                    item[name] = None
            result.append(BOMItem.model_validate(item))
    return result
