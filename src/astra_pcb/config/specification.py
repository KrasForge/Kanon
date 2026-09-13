"""Semantic validation after structural JSON Schema validation; SI units are explicit."""

import math
from copy import deepcopy
from typing import Any


def migrate_spec(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Specification must be a mapping")
    migrated = deepcopy(data)
    if migrated.get("schema_version") == "0.1":
        migrated["schema_version"] = "1.0"
        # The only legacy rename is deliberately explicit; missing fields remain errors.
        if "requirements" in migrated:
            if "functional_requirements" in migrated:
                raise ValueError("Conflicting legacy requirements fields")
            migrated["functional_requirements"] = migrated.pop("requirements")
    if migrated.get("schema_version") != "1.0":
        raise ValueError("Unsupported design specification version")
    return migrated


def validate_spec(data: dict[str, Any]) -> None:
    errors = []
    identifiers = set()

    def walk(value, location="spec"):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{location}: non-finite numerical value")
        if isinstance(value, dict):
            identifier = value.get("id")
            if identifier:
                if identifier in identifiers:
                    errors.append(f"{location}: duplicate ID {identifier}")
                identifiers.add(identifier)
            for suffix in ["v", "c", "a", "hz"]:
                lower, upper = value.get(f"min_{suffix}"), value.get(f"max_{suffix}")
                if lower is not None and upper is not None:
                    if lower > upper:
                        errors.append(f"{location}: inverted {suffix} range")
                    nominal = value.get(f"nominal_{suffix}")
                    if nominal is not None and not lower <= nominal <= upper:
                        errors.append(f"{location}: nominal outside {suffix} range")
            for key, child in value.items():
                walk(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{location}[{index}]")

    walk(data)
    rails = {r["id"]: r for r in [*data["power_inputs"], *data["rails"]]}
    for rail in data["rails"]:
        for source in [rail["source"], *rail.get("dependencies", [])]:
            if source not in rails:
                errors.append(f"{rail['id']}: unknown rail/source {source}")
    for interface in data["interfaces"]:
        if interface["voltage_domain"] not in rails:
            errors.append(f"{interface['id']}: unknown voltage domain")
    for device in data["devices"]:
        if device.get("part") in data["forbidden_parts"]:
            errors.append(f"{device['id']}: forbidden part")
    environment = data["environmental_limits"]
    if environment.get("temperature_min_c", -273.15) > environment.get("temperature_max_c", 1e6):
        errors.append("Inverted environmental temperature range")
    if environment.get("temperature_min_c", 0) < -273.15:
        errors.append("Temperature below absolute zero")

    def visit(name, stack):
        if name in stack:
            errors.append(f"Power dependency cycle: {' -> '.join([*stack, name])}")
            return
        rail = rails.get(name)
        if rail and name not in {r["id"] for r in data["power_inputs"]}:
            for dependency in {rail["source"], *rail.get("dependencies", [])}:
                if dependency in rails:
                    visit(dependency, [*stack, name])

    for name in rails:
        visit(name, [])
    if errors:
        raise ValueError("; ".join(errors))
