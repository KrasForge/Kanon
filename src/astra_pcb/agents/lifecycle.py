"""Linear milestone transitions with content-bound gates and explicit change invalidation."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, model_validator

from astra_pcb.models import StrictModel, VerificationReport
from astra_pcb.models.provenance import Digest
from astra_pcb.release import GateConfig, ReleaseGate, evaluate
from astra_pcb.release.attestations import Attestation, TrustedSigner


class Stage(StrEnum):
    SPEC = "SPEC"
    ARCHITECTURE = "ARCHITECTURE"
    COMPONENT_SELECTION = "COMPONENT_SELECTION"
    SCHEMATIC = "SCHEMATIC"
    SCHEMATIC_REVIEW = "SCHEMATIC_REVIEW"
    FLOORPLAN = "FLOORPLAN"
    CRITICAL_ROUTING = "CRITICAL_ROUTING"
    GENERAL_ROUTING = "GENERAL_ROUTING"
    PCB_REVIEW = "PCB_REVIEW"
    DFM = "DFM"
    MECHANICAL = "MECHANICAL"
    RELEASE_REVIEW = "RELEASE_REVIEW"
    RELEASED = "RELEASED"


# Gate required to ENTER the destination stage. A trusted project policy can add gates;
# these minimum gates cannot be removed or changed into optional/waivable checks here.
GATES = {
    Stage.ARCHITECTURE: [("requirements.complete", "MANUAL")],
    Stage.COMPONENT_SELECTION: [("architecture.review", "MANUAL")],
    Stage.SCHEMATIC: [("components.review", "MANUAL")],
    Stage.SCHEMATIC_REVIEW: [("schematic.erc", "AUTOMATED")],
    Stage.FLOORPLAN: [("schematic.review", "MANUAL")],
    Stage.CRITICAL_ROUTING: [("floorplan.review", "MANUAL")],
    Stage.GENERAL_ROUTING: [("critical-nets.review", "MANUAL")],
    Stage.PCB_REVIEW: [("pcb.drc", "AUTOMATED")],
    Stage.DFM: [("power.review", "MANUAL"), ("review.independent", "MANUAL")],
    Stage.MECHANICAL: [("dfm.review", "MANUAL")],
    Stage.RELEASE_REVIEW: [("mechanical.review", "MANUAL")],
    Stage.RELEASED: [("release.transaction", "AUTOMATED")],
}


class Transition(StrictModel):
    previous: Stage
    target: Stage
    input_digest: Digest
    actor: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    kind: str = Field(pattern="^(advance|invalidate)$")
    evidence: tuple[str, ...] = Field(min_length=1)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Lifecycle(StrictModel):
    project: str = Field(min_length=1)
    design_author: str = Field(min_length=1)
    stage: Stage = Stage.SPEC
    input_digest: Digest
    history: tuple[Transition, ...] = ()

    @model_validator(mode="after")
    def chain(self):
        previous = Stage.SPEC
        for event in self.history:
            if event.previous != previous or event.at.tzinfo is None:
                raise ValueError("Broken lifecycle event chain")
            if (
                event.kind == "advance"
                and list(Stage).index(event.target) != list(Stage).index(previous) + 1
            ):
                raise ValueError("Illegal recorded forward transition")
            if event.kind == "invalidate" and event.target != Stage.SPEC:
                raise ValueError("Changed input must restart evidence at SPEC")
            previous = event.target
        if previous != self.stage:
            raise ValueError("State does not match event history")
        if self.history and self.history[-1].input_digest != self.input_digest:
            raise ValueError("State digest differs from latest event")
        return self

    def advance(
        self,
        target: Stage,
        report: VerificationReport,
        *,
        actor: str,
        attestations: tuple[Attestation, ...] = (),
        trusted: dict[str, TrustedSigner] | None = None,
    ) -> "Lifecycle":
        stages = list(Stage)
        if self.stage == Stage.RELEASED or stages.index(target) != stages.index(self.stage) + 1:
            raise ValueError("Illegal lifecycle transition")
        if report.design_author != self.design_author:
            raise ValueError("Report design author differs from lifecycle")
        gates = GateConfig(
            gates=tuple(ReleaseGate(check_id=key, mode=mode) for key, mode in GATES[target])
        )
        decision = evaluate(
            gates,
            report,
            expected_digest=self.input_digest,
            attestations=attestations,
            trusted=trusted,
        )
        if decision.exit_code != 0:
            raise ValueError(
                "Transition blocked by missing, failed or unauthenticated gate evidence"
            )
        event = Transition(
            previous=self.stage,
            target=target,
            input_digest=self.input_digest,
            actor=actor,
            reason="Required stage gates satisfied",
            kind="advance",
            evidence=(decision.model_dump_json(),),
        )
        return Lifecycle.model_validate(
            {**self.model_dump(), "stage": target, "history": (*self.history, event)}
        )

    def invalidate(self, new_digest: Digest, *, actor: str, reason: str) -> "Lifecycle":
        if new_digest == self.input_digest:
            raise ValueError("Invalidation requires changed content identity")
        event = Transition(
            previous=self.stage,
            target=Stage.SPEC,
            input_digest=new_digest,
            actor=actor,
            reason=reason,
            kind="invalidate",
            evidence=(self.input_digest,),
        )
        return Lifecycle.model_validate(
            {
                **self.model_dump(),
                "stage": Stage.SPEC,
                "input_digest": new_digest,
                "history": (*self.history, event),
            }
        )
