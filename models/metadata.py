from typing import List, Optional
from pydantic import BaseModel, field_validator

class MetadataBase(BaseModel):
    parties: List[str] = []
    effective_date: Optional[str] = None
    termination: Optional[str] = None
    governing_law: Optional[str] = None
    jurisdiction: Optional[str] = None
    payment_terms: Optional[str] = None
    renewal: Optional[str] = None
    confidentiality: Optional[str] = None
    liability_limit: Optional[str] = None
    extraction_id: int

    @field_validator('parties', mode="before")
    def _normalize_parties(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        return []

    @field_validator('parties')
    def _strip_parties(cls, v):
        return [s.strip() for s in v if isinstance(s, str) and s.strip()]

    @field_validator('effective_date', 'termination', 'governing_law', 'jurisdiction', 'payment_terms', 'renewal', 'confidentiality', 'liability_limit', mode="before")
    def _strip_strings(cls, v):
        return v.strip() if isinstance(v, str) else v

class Metadata(MetadataBase):
    id: int