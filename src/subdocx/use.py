from subdocx.errors import MissingFieldInData
from .template import Template
from .substitution import Substitute, SubFromTable
from io import BytesIO
import os
import requests
import pandas as pd

from pydantic import BaseModel


def substitute(template: Template, data: dict[str, str]):
    try:
        new = Substitute(template, data)
    except KeyError as e:
        raise MissingFieldInData(e.args[0])
    # docx
    buffer = BytesIO()
    new.save(buffer)
    buffer.seek(0)

    return buffer


############

class TemplateData(BaseModel):
    name: str
    filename: str
    numeric_on: str | None = None

def api_gen_bulk(templates: list[Template], data: pd.DataFrame, naming_schema: str):

    if "{temp.name}" in naming_schema:
        name_str = naming_schema
        naming_schema = lambda temp: name_str.replace('{temp.name}',temp.name)

    zipStream = SubFromTable(temp=templates,
                table=data,
                naming_schema=naming_schema,
                zip=True,
                )
    return zipStream
