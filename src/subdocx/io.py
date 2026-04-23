from pathlib import Path
import re
from .template import Document
from io import BytesIO
import requests
import os
from docx.document import Document
import zipfile

## PDF Conversion
SERVER = os.getenv("UNISERVER_URL")
PORT = os.getenv("UNISERVER_PORT")


def path_from_data(data, fn_schema, extension=".docx", parent_directory=Path()):
    filename = fn_schema
    matches = re.finditer(r"{([\w\s\d\(\)°\.]+)}", fn_schema)
    for m in matches:
        placeholder = m.group()
        key = m.groups()[0]
        value = data[key]
        filename = filename.replace(placeholder, str(value))

    filename = re.sub("\\s+", "_", filename)

    f_path = parent_directory / Path(filename)
    if (f_path.parts) != 1:
        f_path.parent.mkdir(parents=True, exist_ok=True)

    return f_path.with_suffix(extension)


def to_pdf(docx: Document) -> bytes:
    docx_buffer = BytesIO()
    docx.save(docx_buffer)
    docx_buffer.seek(0)

    pdf_r = requests.post(
        f"http://{SERVER}:{PORT}/request",
        files={"file": docx_buffer},
        data={"convert-to": "pdf"},
    )
    content = pdf_r.content
    return content


def write(input: Document | bytes, path: Path):
    match input:
        case Document():
            input.save(path)
        case bytes():  # pdf bytes
            pdf_buffer = Path(path).open("wb")
            pdf_buffer.write(input)
            pdf_buffer.close()

def zip_dir(directory):
    if isinstance(directory, str):
        directory = Path(directory)

    zipstream = BytesIO()

    with zipfile.ZipFile(zipstream, mode="w") as archive:
        exts = ['pdf','docx']
        files = []
        for ext in exts:
            files += list(directory.rglob(f"*.{ext}"))

        for file_path in files:
            archive.write(file_path, arcname=file_path.relative_to(directory))

        archive.close()

        return zipstream
