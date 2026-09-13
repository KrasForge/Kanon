"""Lossless persisted-source snapshots, S-expression inspection and content diffs."""

import hashlib
import json
import re
from pathlib import Path

from pydantic import Field, model_validator

from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import InputIdentity, file_digest


def parse_sexpr(text: str) -> list:
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    roots = []
    stack = [roots]
    for token in tokens:
        if token == "(":
            node = []
            stack[-1].append(node)
            stack.append(node)
        elif token == ")":
            if len(stack) == 1:
                raise ValueError("Unexpected closing parenthesis")
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if len(stack) != 1 or len(roots) != 1 or not isinstance(roots[0], list):
        raise ValueError("Unbalanced or multiple S-expression roots")
    return roots[0]


def nodes(tree: list, kind: str):
    if tree and tree[0] == kind:
        yield tree
    for item in tree:
        if isinstance(item, list):
            yield from nodes(item, kind)


class Snapshot(StrictModel):
    identity: InputIdentity
    documents: dict[str, str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_documents(self):
        if self.documents.keys() != self.identity.files.keys():
            raise ValueError("Snapshot document set differs from identity")
        for name, text in self.documents.items():
            if hashlib.sha256(text.encode()).hexdigest() != self.identity.files[name]:
                raise ValueError("Snapshot document differs from content identity")
        return self

    def objects(self, kind: str) -> list[list]:
        return [
            node
            for name, text in self.documents.items()
            if name.endswith((".kicad_pcb", ".kicad_sch", ".kicad_sym", ".kicad_mod"))
            for node in nodes(parse_sexpr(text), kind)
        ]

    def diff(self, other: "Snapshot") -> dict[str, tuple[str, ...]]:
        before, after = self.identity.files, other.identity.files
        return {
            "added": tuple(sorted(after.keys() - before.keys())),
            "removed": tuple(sorted(before.keys() - after.keys())),
            "changed": tuple(
                sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
            ),
        }


def capture(root: Path, paths: tuple[Path, ...], revision: str) -> Snapshot:
    files, documents = {}, {}
    for supplied in paths:
        path = (root / supplied).resolve()
        if not path.is_relative_to(root.resolve()) or path.is_symlink():
            raise ValueError("Snapshot source outside project root")
        relative = str(path.relative_to(root.resolve()))
        if relative in files:
            raise ValueError("Duplicate snapshot source")
        if path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError("Snapshot source exceeds 32 MiB per-file limit")
        before = file_digest(path)
        documents[relative] = path.read_bytes().decode("utf-8")
        if path.suffix in {".kicad_pcb", ".kicad_sch"}:
            parse_sexpr(documents[relative])
        if file_digest(path) != before:
            raise ValueError("Source changed while snapshotting")
        files[relative] = before
    return Snapshot(identity=InputIdentity(revision=revision, files=files), documents=documents)
