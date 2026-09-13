"""YAML input loading and explicit JSON Schema validation."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from astra_pcb.config.specification import migrate_spec, validate_spec


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def validate_document(document: Path, schema: Path) -> None:
    definition = json.loads(schema.read_text())
    Draft202012Validator.check_schema(definition)
    data = load_yaml(document)
    if definition.get("title") == "design-spec":
        data = migrate_spec(data)
    Draft202012Validator(definition).validate(data)
    if definition.get("title") == "design-spec":
        validate_spec(data)
