from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import pandas as pd

from .errors import EmptyBatchTable, InvalidBatchTable, InvalidRepetitionCount
from .substitution_options import formatType
from .export import path_from_data, to_pdf, write, zip_dir
from .template import Template


class BatchSubstitution:
    def __init__(
        self,
        temp: Template | list[Template],
        table: pd.DataFrame,
        naming_schema: str | Callable,
        format: formatType = {},
        parent_directory: Path | None = None,
        pdf: bool = True,
        zip: bool = False,
        **kwargs,
    ):
        self.templates = temp if isinstance(temp, list) else [temp]
        self.table = table
        self.naming_schema = naming_schema
        self.format = format
        self.parent_directory = parent_directory
        self.pdf = pdf
        self.zip = zip
        self.kwargs = kwargs

    def _resolve_table(self) -> pd.DataFrame:
        table = self.table
        if isinstance(table, pd.DataFrame):
            table.columns = table.columns.str.strip()

        if not isinstance(table, pd.DataFrame):
            raise InvalidBatchTable(
                "Batch substitution requires `table` to be a pandas DataFrame."
            )
        if table.shape[0] <= 0:
            raise EmptyBatchTable()
        return table

    def _resolve_naming_schema(self, template: Template):
        match self.naming_schema:
            case x if isinstance(self.naming_schema, str):
                return x
            case x if callable(self.naming_schema):
                return x(template)

    def render(self):
        from .substitution import Substitution

        table = self._resolve_table()
        tableN = table.shape[0]

        if self.parent_directory is None:
            with TemporaryDirectory() as td:
                self.parent_directory = Path(td)

        output_directory =  self.parent_directory

        for i, row in table.iterrows():
            rowN = len(self.templates)
            row_i = 0
            for temp in self.templates:
                if temp.conditional is None:
                    pass
                elif temp.conditional.valid(row):
                    pass
                else:
                    continue

                if temp.numeric and temp.n_from:
                    N = temp.n_from.getN(row)  # pyright: ignore
                    if N is None or N <= 0:
                        raise InvalidRepetitionCount(N)
                else:
                    N = 1

                rowN += N - 1
                for n in range(N + 1):
                    if n == 0 and temp.numeric:
                        continue

                    print(f"{i}/{tableN} - {row_i}/{rowN}", end="\r")
                    substitution = Substitution(
                        temp,
                        row,
                        format=self.format,
                        n=n,
                        **self.kwargs,
                    )
                    new_doc = substitution.render()
                    extension = ".docx"

                    if self.pdf:
                        new_doc = to_pdf(new_doc)
                        extension = ".pdf"

                    out_path = path_from_data(
                        data=row,
                        fn_schema=self._resolve_naming_schema(temp),
                        parent_directory=output_directory,
                        extension=extension,
                    )

                    if temp.numeric:
                        out_path = out_path.with_stem(out_path.stem + f"_{n}")

                    write(new_doc, out_path)

                    row_i += 1
                    if not temp.numeric:
                        break
        if self.zip:
            return zip_dir(output_directory)
