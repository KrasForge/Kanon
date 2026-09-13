"""Audited, hashed local SPICE includes and named-library sections; no network resolution."""

import shlex
from pathlib import Path

from pydantic import Field

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import Digest, canonical_digest, file_digest


class ModelFile(StrictModel):
    path: str
    sha256: Digest
    sections: tuple[str, ...] = ()
    license: str = Field(min_length=1)
    approved_by: str = Field(min_length=1)
    evidence: DatasheetEvidence


def flatten(netlist: Path, models: tuple[ModelFile, ...]) -> tuple[str, str, dict[str, str]]:
    root = netlist.parent.resolve()
    declarations = {m.path: m for m in models}
    if len(declarations) != len(models):
        raise ValueError("Duplicate model paths")
    hashes = {str(netlist.resolve()): file_digest(netlist)}
    stack = []

    def expand(path, section=None, primary=False):
        path = path.resolve()
        if not path.is_relative_to(root):
            raise ValueError("Model escapes simulation root")
        relative = path.relative_to(root).as_posix()
        key = (relative, section)
        if key in stack or len(stack) >= 16:
            raise ValueError("Model include cycle/depth exceeded")
        if len(hashes) > 64:
            raise ValueError("Too many model files")
        if path.stat().st_size > 1024 * 1024:
            raise ValueError("Model exceeds 1 MiB")
        digest = file_digest(path)
        if not primary:
            model = declarations.get(relative)
            if not model or model.sha256 != digest:
                raise ValueError("Unapproved, missing or changed model")
            if section and section not in model.sections:
                raise ValueError("Unapproved library section")
        hashes[str(path)] = digest
        lines = path.read_text().splitlines()
        if section:
            selected = []
            active = False
            found = 0
            for line in lines:
                tokens = (
                    shlex.split(line, comments=False)
                    if line.strip() and not line.lstrip().startswith("*")
                    else []
                )
                if tokens and tokens[0].lower() == ".lib" and len(tokens) == 2:
                    if active:
                        raise ValueError("Nested library sections unsupported")
                    active = tokens[1].casefold() == section.casefold()
                    if active:
                        found += 1
                elif tokens and tokens[0].lower() == ".endl":
                    active = False
                elif active:
                    selected.append(line)
            if found != 1 or active:
                raise ValueError("Missing/ambiguous/unterminated library section")
            lines = selected
        output = []
        stack.append(key)
        for line in lines:
            stripped = line.strip()
            token = stripped.split(maxsplit=1)[0].lower() if stripped else ""
            if token in {".include", ".inc", ".lib"}:
                parts = shlex.split(stripped, comments=False)
                if token == ".lib" and len(parts) != 3 or token != ".lib" and len(parts) != 2:
                    raise ValueError("Unsupported model include/library syntax")
                output.append("* qualified include " + parts[1])
                output.extend(expand(path.parent / parts[1], parts[2] if token == ".lib" else None))
            else:
                output.append(line)
        stack.pop()
        return output

    content = "\n".join(expand(netlist, primary=True)) + "\n"
    digest = hashes[str(netlist.resolve())] if len(hashes) == 1 else canonical_digest(hashes)
    return content, digest, hashes
