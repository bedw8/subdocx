from io import BytesIO

import pandas as pd

from .batch import BatchSubstitution
from .errors import MissingFieldInData
from .substitution import Substitution
from .template import Template


def substitute(template: Template, data: dict[str, str]):
    try:
        new = Substitution(template, data).render()
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

    zipStream = BatchSubstitution(
        temp=templates,
        table=data,
        naming_schema=naming_schema,
        zip=True,
    ).render()
    return zipStream
