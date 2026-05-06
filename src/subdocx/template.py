import docx
from copy import deepcopy
from typing import Callable, Any
from dataclasses import dataclass
import pandas as pd

from .errors import InvalidRepetitionConfiguration, InvalidRepetitionData
from .utils import normalize as normalize_document
from .substitution_options import SubstitutionOptions, formatType

from docx.document import Document
import operator


@dataclass
class NHandler:
    """
    pattern: number of columns with that pattern and non-na values
    columns: number from column value
    function: number from function (lambda data: ...)
    """

    pattern: str | None = None
    column: str | None = None
    function: Callable[[Any], int] | None = None

    def getN(self, data) -> int:
        notnone = [(k, v) for k, v in self.__dict__.items() if v is not None]
        if len(notnone) == 0:
            raise InvalidRepetitionConfiguration(
                "NHandler requires one of: pattern, column, or function."
            ) from None
        key, val = notnone[0]

        match key:
            case "pattern":
                if not isinstance(data, pd.Series):
                    raise InvalidRepetitionData(
                        "NHandler pattern mode requires a pandas Series row."
                    )
                res = data.filter(regex=val).where(lambda x: x > 0).dropna().size
            case "column":
                res = int(data[val])
            case "function":
                res = val(data)

        return res

    #IDEA: turn N to rep. 
    # getN -> get_reps (list of values)

@dataclass
class ConditionHandler:
    """
    
    """

    column: str | None = None
    value: Any | None = None
    op: str = 'eq'

    _operations = {
        'eq':operator.eq,
        'ne':operator.ne,
        'le':operator.le,
        'ge':operator.ge,
        'gt':operator.gt,
        'lt':operator.lt,
        'in':operator.contains,
        }

    def _get_op(self):
        return self._operations[self.op]
 
    def valid(self, data_row) -> bool:
        op = self._get_op()

        if self.op == 'in':
            return op(self.value,data_row[self.column])

        return op(data_row[self.column],self.value)
        


class Template(Document):
    _loaded_templates: list["Template"] = []
    _normalized_templates: list["Template"] = []
    _custom_options = ["format", "vars_exclusion", "nvars_exclusion", "n_from"]

    def __init__(
        self,
        input,
        name: str = "",
        numeric: bool = False,
        n_from: NHandler | None = None,
        conditional: ConditionHandler | None = None,
        **kwargs,
    ):
        if isinstance(input, Document):
            pass
        else:
            input = docx.Document(input)

        self.__dict__ = input.__dict__
        self.name = name
        self.numeric = numeric
        self.n_from = n_from
        self.conditional = conditional

        self.config = SubstitutionOptions()
        self.config._load_kwargs(*kwargs)

        self._loaded_templates.append(self)
        self.format: formatType = {}

        self.normalize()

    @property
    def id(self):
        return Template._loaded_templates.index(self)

    @property
    def is_norm(self):
        return self in Template._normalized_templates

    def copy(self):
        return deepcopy(self)

    def normalize(self):
        to_normalize = self.copy()
        normalize_document(to_normalize)
        to_normalize._original = False
        self._normalized_templates.append(to_normalize)
        # TODO add normalization logs
