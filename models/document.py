from typing import List
from pydantic import BaseModel, field_validator

class DocumentBase(BaseModel):
    name: str
    text: str

    @field_validator('name', 'text', mode="before")
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator('name')
    def _non_empty_name(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v


class Document(DocumentBase):
    id: int