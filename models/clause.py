from pydantic import BaseModel, Field, validator

class Clause(BaseModel):
    name: str
    text: str = Field(max_length=400)
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @validator('name', 'text', pre=True)
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator('name')
    def _non_empty_name(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v

    @validator('end')
    def _end_ge_start(cls, v, values):
        s = values.get('start')
        if s is not None and v < s:
            raise ValueError('end must be greater than or equal to start')
        return v