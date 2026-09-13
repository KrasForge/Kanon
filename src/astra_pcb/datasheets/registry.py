"""Local, content-addressed document registry and evidence-backed numeric limits."""

import json
from pathlib import Path

from pydantic import Field, model_validator

from astra_pcb.datasheets import DatasheetEvidence
from astra_pcb.models import CheckResult, CheckStatus, StrictModel
from astra_pcb.models.provenance import Digest, file_digest


class Document(StrictModel):
    id: str = Field(min_length=1)
    components: tuple[str, ...] = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    title: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    local_path: str = Field(min_length=1)
    sha256: Digest
    canonical_url: str | None = None
    redistribution: str = "not-assessed"


class Registry:
    def __init__(self, root: Path, documents: tuple[Document, ...] = ()):
        self.root = root.resolve()
        self.documents = {d.id: d for d in documents}
        if len(self.documents) != len(documents):
            raise ValueError("Duplicate document IDs")

    @classmethod
    def load(cls, root: Path, index: Path) -> "Registry":
        return cls(root, tuple(Document.model_validate(d) for d in json.loads(index.read_text())))

    def register(self, document: Document) -> None:
        if document.id in self.documents and self.documents[document.id] != document:
            raise ValueError("Document identity collision; register a new revision ID")
        self.validate(document)
        self.documents[document.id] = document

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [self.documents[k].model_dump(mode="json") for k in sorted(self.documents)]
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("x") as stream:
            stream.write(json.dumps(data, indent=2) + "\n")
        temporary.replace(path)

    def validate(self, document: Document) -> None:
        path = (self.root / document.local_path).resolve()
        if Path(document.local_path).is_absolute() or not path.is_relative_to(self.root):
            raise ValueError("Document path escapes registry")
        if not path.is_file() or file_digest(path) != document.sha256:
            raise ValueError("Document missing or content changed")

    def citation(
        self,
        document_id: str,
        *,
        constraint: str,
        page: str | None = None,
        section: str | None = None,
    ) -> DatasheetEvidence:
        document = self.documents[document_id]
        self.validate(document)
        return DatasheetEvidence(
            document=document.title,
            manufacturer=document.manufacturer,
            revision=document.revision,
            page=page,
            section=section,
            extracted_constraint=constraint,
            source_location=document.local_path,
            sha256=document.sha256,
        )


class SourcedLimit(StrictModel):
    id: str = Field(min_length=1)
    minimum: float | None = None
    maximum: float | None = None
    unit: str = Field(min_length=1)
    applicability: str = Field(min_length=1)
    evidence: DatasheetEvidence

    @model_validator(mode="after")
    def ordered(self):
        if self.minimum is None and self.maximum is None:
            raise ValueError("At least one limit bound is required")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("Inverted limit")
        if self.evidence.sha256 is None:
            raise ValueError("Constraint evidence requires document content identity")
        return self

    def check(self, value: float, unit: str, registry: Registry) -> CheckResult:
        import math

        try:
            matching = [
                d
                for d in registry.documents.values()
                if d.sha256 == self.evidence.sha256
                and d.revision == self.evidence.revision
                and d.manufacturer == self.evidence.manufacturer
                and d.local_path == self.evidence.source_location
            ]
            if not matching:
                raise ValueError("Constraint evidence is not registered")
            registry.validate(matching[0])
            if unit != self.unit or not math.isfinite(value):
                raise ValueError("Unit mismatch or nonfinite observation")
            passed = (self.minimum is None or value >= self.minimum) and (
                self.maximum is None or value <= self.maximum
            )
            return CheckResult(
                check_id=self.id,
                name=self.id,
                status=CheckStatus.PASS if passed else CheckStatus.FAIL,
                message=f"{value} {unit}; declared bounds [{self.minimum}, {self.maximum}]",
                evidence=(self.evidence.model_dump_json(),),
                source="sourced constraint",
            )
        except (ValueError, OSError) as exc:
            return CheckResult(
                check_id=self.id,
                name=self.id,
                status=CheckStatus.ERROR,
                message=str(exc),
                evidence=(self.evidence.model_dump_json(),),
            )
