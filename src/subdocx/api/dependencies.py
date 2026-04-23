from fastapi import Form, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic import TypeAdapter

from .schemas import GenData, TemplateData


def parse_data(t: type, data: str):
    try:
        ta = TypeAdapter(t)
        return ta.validate_json(data)
    except Exception as e:
        raise HTTPException(
            detail=jsonable_encoder(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def parse_gendata(data: str = Form(...)):
    return parse_data(GenData, data)


def parse_template_data(tdata: str = Form(...)):
    return parse_data(list[TemplateData], tdata)
