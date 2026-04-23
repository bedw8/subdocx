from io import BytesIO

import pandas as pd

from .batch import SubFromTable
from .errors import MissingFieldInData
from .substitution import Substitute
from .template import Template


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


def generate_bulk_archive(
    templates: list[Template],
    data: pd.DataFrame,
    naming_schema: str,
):

    if "{temp.name}" in naming_schema:
        name_str = naming_schema
        naming_schema = lambda temp: name_str.replace("{temp.name}", temp.name)

    zipStream = SubFromTable(
        temp=templates,
        table=data,
        naming_schema=naming_schema,
        zip=True,
    )
    return zipStream
