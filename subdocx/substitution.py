
from typing import Callable, Any, TypeAlias
from .utils import iter_runs, Document, Run
from .template import Template, NHandler, formatType
from .io import path_from_data
from .config import SubConfig, formatType
import docx
import pandas as pd
import re
from pathlib import Path

def _substitute_run(run: Run,
                        data: dict | pd.Series,
                        n: int = 0,
                        format: formatType = {},
                        kwargs_fallback: SubConfig | None = None,
                        **kwargs
                        ) -> None:
    '''
    substitute the run's variable by the variable's value
    '''
    config = SubConfig()
    config._load_kwargs(**{'format':format,**kwargs})
    
    def _get(key):
        return config.get(key,kwargs_fallback)

    exclude = _get('exclude') 
    only = _get('only')

    if len(exclude) > 0 and len(only) > 0:
        raise Exception('can not use `vars_exclusion` and `vars_only` at the same time')

    text = run.text
    matches = re.finditer(r'{(([\w\s\d\(\)°\.]+);?(\w*))}',text)

    for m in matches:
        # ph: '{variable;format1}'
        ph = m.group()
        # variable keys syntax
        # 
        # full_key: 'variable;format1'
        # value_key: 'variable'
        # specific_key: 'format1'
        full_key,value_key,specific_key = m.groups()
        if value_key in exclude:
            continue
        if len(only) >1 and value_key not in only:
            continue
        
        # format
        #
        # not using specific_key at the moment. full_key is enough
        ffunc: Callable = format[full_key] if full_key in format else lambda x:x

        # value
        #
        # get value for n-th numeric variable
        if n > 0:
            value_key = re.sub('\\b1(?!°)\\b',str(n),value_key)

        # new value
        new_val = str(ffunc(data[value_key]))
        print(full_key,'--',new_val,full_key in format)

        text = text.replace(ph,new_val)

    # replacing value
    run.text = text


def Substitute(
        temp: Template,
        data: dict | pd.Series,
        format: formatType = {},
        n:int = 0,
        **kwargs
    ) -> None:
    '''substitute all variables in the document       
    '''
    
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
        if '{' in r.text:
            _substitute_run(
                run=r,
                data=data,
                n=n,
                format=format,
                kwargs_fallback=temp.config,
                **kwargs
            )

    return new_document

def SubFromTable(
    temp: Template | list[Template],
    table: list[dict] | pd.DataFrame,
    naming_schema: str | Callable,
    parent_directory=Path(),
    **kwargs,
    ) -> None:

    if isinstance(table,pd.DataFrame):
        tableN = table.shape

        # TODO put in check function
        table.columns = table.columns.str.strip()

        table = table.iterrows()
    elif isinstance(table,list):
        tableN = len(table) 
        table = enumerate(table)

    input_temp = temp
    if a:=not isinstance(temp,list):
        print(a)
        input_temp = [temp]
    
    for i,row in table:
        rowN = len(input_temp)
        row_i = 0
        for temp in input_temp:
            if temp.numeric:
                N = temp.n_from.getN(row)
            else:
                N=1

            rowN += N-1
            for n in range(N+1): 
                # skip to n=1 to numeric 
                if n == 0 and temp.numeric:
                    continue

                print(f'{i}/{tableN} - {row_i}/{rowN}',end='\r')
                new_doc = Substitute(temp=temp,data=row,n=n,**kwargs)
                
                # handle path creation
                match naming_schema:
                    case x if isinstance(naming_schema,str):
                        fn_schema = x
                    case x if callable(naming_schema):
                        fn_schema = x(temp) 

                out_path = path_from_data(
                    data=row,
                    fn_schema=fn_schema,
                    parent_directory=parent_directory)    


                if temp.numeric:
                    out_path = out_path.with_stem(out_path.stem + f'_{n}')
                    
                print(f'{i}/{tableN} - {row_i}/{rowN}',end='\r')

                new_doc.save(out_path)
                    
                row_i += 1
                # only n=0 for non-numeric
                if not temp.numeric:
                    break

