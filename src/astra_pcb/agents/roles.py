"""Typed capability policy. Reviewer never receives a live KiCad transport."""

from typing import Literal

from pydantic import Field, model_validator

from astra_pcb.kicad.mcp import DesignerTools, ReviewerTools
from astra_pcb.kicad.snapshot import Snapshot
from astra_pcb.models import StrictModel


class Role(StrictModel):
    name: Literal["architect", "designer", "reviewer", "release-gate"]
    model: str | None = None
    reasoning: Literal["high", "medium", "none"] = "high"
    tools: tuple[str, ...]
    shell: bool = False
    source_mount: Literal["none", "read-only", "read-write"] = "none"

    @model_validator(mode="after")
    def permissions(self):
        allowed = {
            "architect": {"snapshot.read", "snapshot.objects"},
            "reviewer": {"snapshot.read", "snapshot.objects"},
            "designer": {"board.open", "board.read", "board.route", "board.save", "backend.read"},
            "release-gate": {"checks.execute", "artifacts.write"},
        }
        if self.shell or not set(self.tools) <= allowed[self.name]:
            raise ValueError("Unsupported role capability or shell access")
        if self.name in {"architect", "reviewer"} and self.source_mount != "none":
            raise ValueError("Read roles consume frozen snapshots, not source mounts")
        if self.name == "release-gate" and (self.model is not None or self.reasoning != "none"):
            raise ValueError("Release authority is deterministic, not an LLM")
        if self.name != "release-gate" and not self.model:
            raise ValueError("Agent role requires an explicit model target")
        return self


class Roles(StrictModel):
    roles: tuple[Role, ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def complete(self):
        if {r.name for r in self.roles} != {"architect", "designer", "reviewer", "release-gate"}:
            raise ValueError("Exactly one definition of each engineering role is required")
        return self


class RoleTools:
    """Trusted harness dispatch surface; pass only selected tool JSON to a remote model.

    Python objects are not an OS sandbox. Do not execute model-generated Python in this
    harness process. Reviewer model calls must run without source mounts or shell tools.
    """

    def __init__(self, role: Role, snapshot: Snapshot, designer: DesignerTools | None = None):
        self.names = role.tools
        self._read = ReviewerTools(snapshot) if role.name in {"reviewer", "architect"} else None
        if role.name != "designer" and designer is not None:
            raise ValueError("Live designer transport cannot be attached to a read-only role")
        self._designer = designer

    def call(self, name: str, arguments: dict, *, allow_write: bool = False) -> dict:
        if name not in self.names:
            raise PermissionError("Role tool unavailable")
        if self._read is not None:
            return self._read.call(name, arguments)
        if self._designer is not None:
            return self._designer.call(name, arguments, allow_write=allow_write)
        raise PermissionError("Role operation requires the deterministic harness executor")
