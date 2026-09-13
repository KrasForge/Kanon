"""Engineering change intent and rollback evidence, not implicit mutation authority."""

from pydantic import Field

from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import Digest


class ChangePlan(StrictModel):
    id: str = Field(min_length=1)
    input_digest: Digest
    rationale: str = Field(min_length=1)
    affected_objects: tuple[str, ...] = Field(min_length=1)
    operations: tuple[str, ...] = Field(min_length=1)
    expected_effects: tuple[str, ...] = Field(min_length=1)
    risks: tuple[str, ...]
    verification_checks: tuple[str, ...] = Field(min_length=1)
    rollback_strategy: str = Field(min_length=1)
    rollback_artifacts: tuple[str, ...] = Field(min_length=1)
    substitutions: tuple[str, ...] = ()
    bank_voltage_changes: tuple[str, ...] = ()
    stackup_changes: tuple[str, ...] = ()
    explicit_user_intent: str | None = None

    def authorize(self, current_digest: Digest) -> None:
        if current_digest != self.input_digest:
            raise ValueError("Change plan is stale")
        if (
            self.substitutions or self.bank_voltage_changes or self.stackup_changes
        ) and not self.explicit_user_intent:
            raise PermissionError("Sensitive engineering change requires explicit user intent")
        # Intent must come from the trusted harness/user interaction, never model self-approval.
