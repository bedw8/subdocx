from typing import Annotated
from fastapi import FastAPI, status, File, UploadFile, Form, Response, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from subdocx.errors import MissingFieldInData
from subdocx.template import Template, NHandler
from subdocx.use import substitute, api_gen_bulk, TemplateData
from subdocx.io import to_pdf
import pandas as pd
from pydantic import BaseModel, TypeAdapter
from io import BytesIO
import json
import logging

app = FastAPI()

logger = logging.getLogger(__name__)


class GenData(BaseModel):
    data: dict[str, str]


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

@app.post(
    "/gen",
    response_class=Response,
)
async def generate_document(
    template: Annotated[UploadFile, File()],
    data: GenData = Depends(parse_gendata),
    pdf: Annotated[bool, Form()] = False,
):
    template = Template(BytesIO(await template.read()))

    try:
        docx_buffer = substitute(template, data)
    except MissingFieldInData as e:
        raise HTTPException(detail=str(e), status=status.HTTP_406_NOT_ACCEPTABLE)

    if pdf:
        mime = "application/pdf"
        content = to_pdf(docx_buffer)

    else:
        content = docx_buffer.read()
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return Response(content=content, media_type=mime)

def parse_template_data(tdata: str = Form(...)):
    return parse_data(list[TemplateData], tdata)

@app.post('/genbulk',response_class=Response)
async def genbulk(
        tdata: Annotated[list[TemplateData], Depends(parse_template_data)],
        templates: list[UploadFile],
        data: UploadFile,
        naming_schema: Annotated[str, Form(...)], 
        ):

    tnames = {}
    tnum = { }

    for td in tdata:
        tnames[td.filename] = td.name
        tnum[td.filename] = td.numeric_on

    temps = [
            Template(t.file, 
                     name=tnames[t.filename],
                     numeric=True if tnum[t.filename] else False,
                     n_from=NHandler(pattern=tnum[t.filename].replace('1','\\d')) if tnum[t.filename] else None)
            for t in templates    
            ]


    data = pd.read_excel(data.file)
    zipStream = api_gen_bulk(
            temps,
            data,
            naming_schema,
            )

    mime = "application/zip"
    return Response(content=zipStream.getvalue(), media_type=mime)
    

