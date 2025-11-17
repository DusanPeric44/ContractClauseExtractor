from typing import List
from pydantic import BaseModel, field_validator
from models.clause import Clause
from models.metadata import Metadata

class ExtractionBase(BaseModel):
    clauses: List[Clause]
    metadata: Metadata
    document_id: int

    @field_validator('clauses', mode="before")
    def _normalize_clauses(cls, v):
        if v is None:
            return []
        return v

    @field_validator('clauses')
    def _sort_clauses(cls, v):
        return sorted(v, key=lambda c: c.start)

class Extraction(ExtractionBase):
    id: int