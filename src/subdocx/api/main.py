from typing import Annotated
from fastapi import FastAPI, status, File, UploadFile, Form, Response, Depends
from subdocx.errors import MissingFieldInData
from subdocx.export import to_pdf
from subdocx.services import render_batch_archive, render_docx_buffer
from subdocx.template import Template, NHandler, ConditionHandler
import pandas as pd
from fastapi.exceptions import HTTPException
from io import BytesIO
import logging

from .dependencies import parse_json_str
from .schemas import GenData, TemplateData

app = FastAPI()

logger = logging.getLogger(__name__)


def parse_gendata(data: str = Form(...)):
    return parse_json_str(GenData, data)


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
        docx_buffer = render_docx_buffer(template, data.data)
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
    return parse_json_str(list[TemplateData], tdata)

@app.post("/genbulk", response_class=Response)
async def genbulk(
    tdata: Annotated[list[TemplateData], Depends(parse_template_data)],
    templates: list[UploadFile],
    data: UploadFile,
    naming_schema: Annotated[str, Form(...)],
):

    # tnames = {}
    # tnum = {}
    # tcond = {}
    #
    # for td in tdata:
    #     tnames[td.filename] = td.name
    #     tnum[td.filename] = td.numeric_on
    #     tcond[td.filename] = td.condition

    data_dict = {}
    for td in tdata:
        data_dict[td.filename] = [td.name, td.numeric_on, td.condition]
    
    for t in templates:
        data_dict[t.filename].append(t.file)
        data_dict[t.filename].append(t.filename)
     
    temps = [
        Template(
            file,
            name=name,
            numeric=True if num else False,
            n_from=NHandler(pattern=num.replace("1", "\\d")) if num else None,
            conditional=None if cond is None else ConditionHandler(**cond.model_dump()),
        )
        for name, num, cond, file, fname in [p[1] for p in  data_dict.items()]
    ]

    data = pd.read_excel(data.file)
    zipStream = render_batch_archive(
        temps,
        data,
        naming_schema,
    )

    mime = "application/zip"
    return Response(content=zipStream.getvalue(), media_type=mime)
