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

    def audit_changes(self, before, after):
        """Compare lossless native object diffs with declared operation/object scope.

        Operation vocabulary: add/remove/modify:<native-kind>, or modify:document for
        file metadata/non-native data. PCB footprints use references; other UUID-bearing
        objects use UUIDs. Unknown objects cannot be silently classified as routing.
        """
        from astra_pcb.kicad.snapshot import parse_sexpr
        from astra_pcb.models import CheckResult
        from astra_pcb.models.provenance import canonical_digest

        self.authorize(before.identity.digest)

        def index(snapshot):
            result = {}
            for path, text in snapshot.documents.items():
                if not path.endswith((".kicad_pcb", ".kicad_sch")):
                    result[("file:" + path, "document")] = text
                    continue
                tree = parse_sexpr(text)
                metadata = [tree[0]]
                for item in tree[1:]:
                    if not isinstance(item, list):
                        metadata.append(item)
                        continue
                    identifier = next(
                        (
                            n[1]
                            for n in item
                            if isinstance(n, list) and len(n) == 2 and n[0] == "uuid"
                        ),
                        None,
                    )
                    if identifier is None:
                        metadata.append(item)
                        continue
                    if item[0] == "footprint":
                        identifier = next(
                            (
                                n[2]
                                for n in item
                                if isinstance(n, list)
                                and len(n) >= 3
                                and n[:2] == ["property", "Reference"]
                            ),
                            identifier,
                        )
                    key = (path + "#" + identifier, item[0])
                    if key in result:
                        raise ValueError("Duplicate native object identity")
                    result[key] = item
                result[("file:" + path, "document")] = metadata
            return result

        old, new = index(before), index(after)
        changes = []
        for key in sorted(old.keys() | new.keys()):
            if old.get(key) == new.get(key):
                continue
            operation = "add" if key not in old else "remove" if key not in new else "modify"
            changes.append({"object": key[0], "operation": operation + ":" + key[1]})
        deviations = [
            c
            for c in changes
            if c["object"] not in self.affected_objects or c["operation"] not in self.operations
        ]
        return CheckResult(
            check_id="mutation.change-plan",
            name="Actual native changes versus plan",
            status="FAIL" if deviations else "PASS" if changes else "SKIP",
            message=f"Observed {len(changes)} changes; {len(deviations)} outside declared scope",
            evidence=(
                str(changes),
                canonical_digest(
                    {
                        "before": before.identity.digest,
                        "after": after.identity.digest,
                        "plan": self.model_dump(mode="json"),
                    }
                ),
            ),
            affected_objects=tuple(c["object"] for c in deviations),
            remediation="Independent review of deviations required before continuing"
            if deviations
            else None,
        )
