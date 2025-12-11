from os import stat
from typing import Annotated
from fastapi import FastAPI, status, File, UploadFile, Form, Body, Response, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from .. import Template, Substitute

from pydantic import BaseModel, ValidationError, validator, Field
from io import BytesIO
import json

app = FastAPI()


class GenData(BaseModel):
    data: dict[str, str]


def parse_data(data: str = Form(...)):
    try:
        # return GenData.model_validate_json(data)
        return json.loads(data)
    except Exception as e:
        raise HTTPException(
            detail=jsonable_encoder(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@app.post(
    "/gen",
    response_class=Response,
)
async def generate_document(
    template: Annotated[UploadFile, File()],
    data: GenData = Depends(parse_data),
    # data: dict[str, str] = Depends(checker),
    # filename: Annotated[str | None, Form()] = None,
):
    template = Template(BytesIO(await template.read()))
    try:
        new = Substitute(template, data)
    except KeyError as e:
        raise HTTPException(
            detail=f"La variable '{e.args[0]}' presente en el template no se encuentra en los datos.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    buffer = BytesIO()

    new.save(buffer)

    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    buffer.seek(0)
    return Response(content=buffer.read(), media_type=mime)
