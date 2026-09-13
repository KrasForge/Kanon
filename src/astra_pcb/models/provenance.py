"""Content identity used across reports, approvals and release artifacts."""

import hashlib
import json
from pathlib import Path
from typing import Annotated

from pydantic import Field

from astra_pcb.models import StrictModel

Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


def file_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


class InputIdentity(StrictModel):
    revision: str = Field(min_length=1)
    files: dict[str, Digest] = Field(min_length=1)

    @property
    def digest(self) -> str:
        return canonical_digest(self.model_dump())

    def verify(self, root: Path) -> None:
        for relative, expected in self.files.items():
            path = (root / relative).resolve()
            if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
                raise ValueError(f"Input escapes root: {relative}")
            if not path.is_file() or file_digest(path) != expected:
                raise ValueError(f"Missing or changed input: {relative}")
