from fastapi import Form, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic import TypeAdapter

from .schemas import GenData, TemplateData


def parse_json_str(t: type, json: str):
    try:
        ta = TypeAdapter(t)
        return ta.validate_json(json)
    except Exception as e:
        raise HTTPException(
            detail=jsonable_encoder(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


