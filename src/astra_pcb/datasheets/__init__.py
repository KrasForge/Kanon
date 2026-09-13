"""Evidence identity; extraction and authenticity verification are not implemented."""

from pydantic import Field, model_validator

from astra_pcb.models import StrictModel


class DatasheetEvidence(StrictModel):
    document: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    page: str | None = None
    section: str | None = None
    extracted_constraint: str = Field(min_length=1)
    source_location: str = Field(min_length=1)
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def locator(self):
        if not self.page and not self.section:
            raise ValueError("page or section required")
        return self
