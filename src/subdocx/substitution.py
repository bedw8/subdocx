from typing import Callable
from .utils import Document, iter_runs, Run
from .template import Template  # , NHandler
from .config import SubConfig, formatType
import pandas as pd
import re
from .format import functions

#### IDEA
# class Substitute
# 
# single file 
# __init__ -> Substitute()
# 
# bulk 
# @staticmethod from_table -> Substitute.from_table()


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


def Substitute(
    temp: Template,
    data: dict[str, str] | pd.Series,
    format: formatType = {},
    n: int = 0,
    **kwargs,
) -> Document:
    """substitute all variables in the document"""

    temp_id = Template._loaded_templates.index(temp)
    norm_temp = Template._normalized_templates[temp_id]
    new_document = norm_temp.copy()

    # TODO make a class SubstitutionConfig ?
    # it should not modify Temp attributes, since this options should be temporary
    #
    # method to get value of parameter from 'self' and 'other' class instances
    # use: substitution input parameter -> self
    #      template default values as fallback -> other
    # returns self.x unless self.x is None, when it returns other.x
    
    for r in iter_runs(new_document):
        if "{" in r.text:
            _substitute_run(
                run=r,
                data=data,
                n=n,
                format=format,
                kwargs_fallback=temp.config,
                **kwargs,
            )

    return new_document
