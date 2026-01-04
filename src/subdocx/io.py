from pathlib import Path
import re


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
