from pydantic import BaseModel, Field, field_validator

class ClauseBase(BaseModel):
    name: str
    text: str
    start: int
    end: int
    extraction_id: int

    @field_validator('name', 'text', mode="before")
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator('name')
    def _non_empty_name(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v

class Clause(ClauseBase):
    id: int