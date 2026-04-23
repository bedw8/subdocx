from typing import TYPE_CHECKING, Callable
import re

import pandas as pd

from .config import SubConfig, formatType
from .format import functions
from .template import Template
from .utils import Document, Run, iter_runs

if TYPE_CHECKING:
    from .batch import BatchSubstitution


class Substitution:
    def __init__(
        self,
        template: Template,
        data: dict[str, str] | pd.Series,
        format: formatType = {},
        n: int = 0,
        **kwargs,
    ):
        self.template = template
        self.data = data
        self.format = format
        self.n = n
        self.kwargs = kwargs

    @staticmethod
    def _substitute_run(
        run: Run,
        data: dict | pd.Series,
        n: int = 0,
        format: formatType = {},
        kwargs_fallback: SubConfig | None = None,
        **kwargs,
    ) -> None:
        """
        substitute the run's variable by the variable's value
        """
        config = SubConfig()
        config._load_kwargs(**{"format": format, **kwargs})

        if isinstance(data, pd.Series):
            data = data.to_dict()

        def _get(key):
            return config.get(key, kwargs_fallback)

        exclude = _get("exclude")
        only = _get("only")

        if len(exclude) > 0 and len(only) > 0:
            raise Exception("can not use `vars_exclusion` and `vars_only` at the same time")

        text = run.text
        matches = re.finditer(r"{(([\w\s\d\(\)°\.]+);?(\w*))}", text)

        for m in matches:
            # ph: '{variable;format1}'
            ph = m.group()
            # variable keys syntax
            #
            # full_key: 'variable;format1'
            # value_key: 'variable'
            # specific_key: 'format1'
            full_key, value_key, specific_key = m.groups()
            if value_key in exclude:
                continue
            if value_key not in data:
                continue
            if len(only) > 1 and value_key not in only:
                continue

            # format
            #
            # not using specific_key at the moment. full_key is enough
            ffunc: Callable
            if full_key in format:
                ffunc = format[full_key]
            elif specific_key in functions:
                ffunc = functions[specific_key]
            else:
                ffunc = lambda x: x

            # value
            #
            # get value for n-th numeric variable
            if n > 0:
                value_key = re.sub("\\b1(?!°)\\b", str(n), value_key)

            # new value
            new_val = str(ffunc(data[value_key]))

            text = text.replace(ph, new_val)

        # replacing value
        run.text = text

    def render(self) -> Document:
        """substitute all variables in the document"""

        temp_id = Template._loaded_templates.index(self.template)
        norm_temp = Template._normalized_templates[temp_id]
        new_document = norm_temp.copy()

        for run in iter_runs(new_document):
            if "{" in run.text:
                self._substitute_run(
                    run=run,
                    data=self.data,
                    n=self.n,
                    format=self.format,
                    kwargs_fallback=self.template.config,
                    **self.kwargs,
                )

        return new_document

    @staticmethod
    def from_table(
        temp: Template | list[Template],
        table: pd.DataFrame,
        naming_schema: str | Callable,
        format: formatType = {},
        parent_directory=None,
        pdf: bool = True,
        zip: bool = False,
        **kwargs,
    ) -> "BatchSubstitution":
        from .batch import BatchSubstitution

        return BatchSubstitution(
            temp=temp,
            table=table,
            naming_schema=naming_schema,
            format=format,
            parent_directory=parent_directory,
            pdf=pdf,
            zip=zip,
            **kwargs,
        )
