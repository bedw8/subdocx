
import docx
from copy import deepcopy 
from typing import List, Dict, Callable, Any, TypeAlias
from dataclasses import dataclass
import pandas as pd

from .utils import normalize as normalize_document
from .config import SubConfig, formatType

Document = docx.document.Document

@dataclass
class NHandler:
    '''
    patter: number of columns with that patter and non-na values
    columns: number from column value
    function: number from function (lambda data: ...)
    '''
    pattern: str | None = None
    column: str | None = None
    function: Callable | None = None
    
    def getN(self,data):

        notnone = [(k,v) for k,v in self.__dict__.items() if v is not None]
        if len(notnone) == 0:
            raise Exception('no method specified') from None
        key,val = notnone[0]

        match key:
            case 'pattern':
                assert isinstance(data, pd.Series)
                return data.filter(regex=val).where(lambda x: x > 0).dropna().size
            case 'column':
                return int(data[val])
            case 'function':
                return val(data)


class Template(Document):
    _loaded_templates: list['Template']  = []
    _normalized_templates: list['Template']  = []
    _custom_options = [
        'format',
        'vars_exclusion',
        'nvars_exclusion',
        'n_from'
    ]
    
    def __init__(
            self, 
            input,
            name: str = "",
            numeric: bool = False,
            n_from: NHandler | None = None,
            **kwargs
        ):
        if isinstance(input, Document):
            pass
        else:
            input = docx.Document(input)

        self.__dict__ = input.__dict__
        self.name = name
        self.numeric = numeric
        self.n_from = n_from

        self.config = SubConfig()
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
        #TODO add normalization logs

        
