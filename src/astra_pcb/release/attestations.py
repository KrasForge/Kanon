"""Verify externally signed approvals. No signing key or signing tool is exposed here."""

import base64
import json
from datetime import datetime
from typing import Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import Field, model_validator

from astra_pcb.models import StrictModel
from astra_pcb.models.provenance import Digest


class TrustedSigner(StrictModel):
    public_key_base64: str
    roles: tuple[Literal["reviewer", "human"], ...] = Field(min_length=1)


class Attestation(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    issuer: str = Field(min_length=1)
    purpose: Literal["approval", "waiver"]
    check_id: str = Field(min_length=1)
    input_digest: Digest
    reason: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(min_length=1)
    issued_at: datetime
    expires_at: datetime
    signature_base64: str

    @model_validator(mode="after")
    def timestamp_order(self):
        if self.issued_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("Attestation timestamps must include timezone")
        if self.expires_at <= self.issued_at:
            raise ValueError("Attestation expiry must follow issuance")
        return self

    def payload(self) -> bytes:
        data = self.model_dump(mode="json", exclude={"signature_base64"})
        return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

    def verify(
        self,
        trusted: dict[str, TrustedSigner],
        *,
        now: datetime,
        digest: str,
        design_author: str | None,
    ) -> None:
        if self.input_digest != digest or not self.issued_at <= now < self.expires_at:
            raise ValueError("Stale, future or expired attestation")
        signer = trusted.get(self.issuer)
        if signer is None:
            raise ValueError("Unknown signer")
        if self.purpose == "waiver" and "human" not in signer.roles:
            raise ValueError("Only an explicitly trusted human may waive a gate")
        if self.purpose == "approval" and (
            "reviewer" not in signer.roles or not design_author or self.issuer == design_author
        ):
            raise ValueError("Approval requires a reviewer independent of the known design author")
        try:
            key = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(signer.public_key_base64, validate=True)
            )
            key.verify(base64.b64decode(self.signature_base64, validate=True), self.payload())
        except (ValueError, InvalidSignature) as exc:
            raise ValueError("Invalid attestation signature") from exc
