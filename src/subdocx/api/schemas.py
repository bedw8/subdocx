from pydantic import BaseModel


class GenData(BaseModel):
    data: dict[str, str]


class Condition(BaseModel):
    column: str
    value: str
    op: str

class TemplateData(BaseModel):
    name: str
    filename: str
    numeric_on: str | None = None
    condition: Condition | None = None
