from pydantic import BaseModel


class GenData(BaseModel):
    data: dict[str, str]


class TemplateData(BaseModel):
    name: str
    filename: str
    numeric_on: str | None = None
