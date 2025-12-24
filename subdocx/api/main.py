from os import stat
from typing import Annotated
from fastapi import FastAPI, status, File, UploadFile, Form, Body, Response, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from .. import Template, Substitute

from pydantic import BaseModel, ValidationError, validator, Field
from io import BytesIO
import json
import tempfile
import requests
import os

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
    pdf: bool = False,
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

    # docx
    buffer = BytesIO()
    new.save(buffer)
    buffer.seek(0)

    if pdf:
        # docx = tempfile.NamedTemporaryFile()
        # new.save(docx.file)

        SERVER = os.getenv("UNISERVER_URL")
        PORT = os.getenv("UNISERVER_PORT")
        pdf_r = requests.post(
            f"http://{SERVER}:{PORT}",
            files={"file": buffer},
            data={"convert-to": "pdf"},
        )
        content = pdf_r.content
        mime = "application/pdf"

    else:
        content = buffer.read()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return Response(content=content, media_type=mime)
