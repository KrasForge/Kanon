"""Strict, serializable verification contracts."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"
    ERROR = "ERROR"


class CheckSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


class CheckResult(StrictModel):
    check_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: CheckStatus
    severity: CheckSeverity = CheckSeverity.ERROR
    message: str
    evidence: tuple[str, ...] = ()
    affected_objects: tuple[str, ...] = ()
    remediation: str | None = None
    source: str | None = None


class VerificationReport(StrictModel):
    schema_version: Literal["1.0", "1.1"] = "1.1"
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    design_author: str | None = None
    input_digest: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    tool_versions: dict[str, str] = Field(default_factory=dict)
    results: tuple[CheckResult, ...]

    @model_validator(mode="after")
    def validate_identity(self):
        if self.created_at.tzinfo is None:
            raise ValueError("Report timestamp must include timezone")
        return self

    @property
    def exit_code(self) -> int:
        if not self.results or any(
            r.status in {CheckStatus.FAIL, CheckStatus.ERROR} for r in self.results
        ):
            return 1
        if any(r.status in {CheckStatus.SKIP, CheckStatus.WARN} for r in self.results):
            return 2
        return 0
