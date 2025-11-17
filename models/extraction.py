from typing import List
from pydantic import BaseModel, validator
from models.clause import Clause
from models.metadata import Metadata

class Extraction(BaseModel):
    clauses: List[Clause]
    metadata: Metadata

    @validator('clauses', pre=True)
    def _normalize_clauses(cls, v):
        if v is None:
            return []
        return v

    @validator('clauses')
    def _sort_clauses(cls, v):
        return sorted(v, key=lambda c: c.start)