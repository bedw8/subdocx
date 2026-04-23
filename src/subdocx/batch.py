from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pandas as pd

from .config import formatType
from .export import path_from_data, to_pdf, write, zip_dir
from .substitution import Substitute
from .template import Template


def SubFromTable(
    temp: Template | list[Template],
    table: pd.DataFrame,
    naming_schema: str | Callable,
    format: formatType = {},
    parent_directory: Path | None = None,
    pdf: bool = True,
    zip: bool = False,
    **kwargs,
) -> None:
    if isinstance(table, pd.DataFrame):
        tableN = table.shape[0]

        # TODO put in check function
        table.columns = table.columns.str.strip()

    assert isinstance(table, pd.DataFrame)
    assert tableN > 0

    input_temp = temp
    if not isinstance(temp, list):
        input_temp = [temp]

    temp_directory = TemporaryDirectory() if parent_directory is None else None
    output_directory = Path(temp_directory.name) if temp_directory else parent_directory

    try:
        for i, row in table.iterrows():
            rowN = len(input_temp)
            row_i = 0
            for temp in input_temp:
                if temp.numeric and temp.n_from:
                    N = temp.n_from.getN(row)  # pyright: ignore
                    assert N is not None
                    assert N > 0
                else:
                    N = 1

                rowN += N - 1
                for n in range(N + 1):
                    if n == 0 and temp.numeric:
                        continue

                    print(f"{i}/{tableN} - {row_i}/{rowN}", end="\r")
                    new_doc = Substitute(temp=temp, data=row, n=n, format=format, **kwargs)
                    extension = ".docx"

                    if pdf:
                        new_doc = to_pdf(new_doc)
                        extension = ".pdf"

                    match naming_schema:
                        case x if isinstance(naming_schema, str):
                            fn_schema = x
                        case x if callable(naming_schema):
                            fn_schema = x(temp)

                    out_path = path_from_data(
                        data=row,
                        fn_schema=fn_schema,
                        parent_directory=output_directory,
                        extension=extension,
                    )

                    if temp.numeric:
                        out_path = out_path.with_stem(out_path.stem + f"_{n}")

                    write(new_doc, out_path)

                    row_i += 1
                    if not temp.numeric:
                        break
        if zip:
            return zip_dir(output_directory)
    finally:
        if temp_directory is not None:
            temp_directory.cleanup()
