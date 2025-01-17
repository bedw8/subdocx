
import docx
from typing import TypeAlias

# Run = NewType('Run',docx.oxml.text.run.CT_R)
Run = docx.oxml.text.run.CT_R
Document: TypeAlias = docx.document.Document

def get_next(r: Run) -> Run | None: 
    '''returns the next run, skipping elements in between'''
    next = r.getnext()
    if next is None:
        return None
    
    while not isinstance(next,Run):
        next = next.getnext()

    return next

def get_prev(r: Run) -> Run | None:    
    next = r.getprevious()
    if next is None:
        return None
    
    while not isinstance(next,Run):
        next = next.getprevious()

    return next

def iter_runs(doc: Document):
    '''generator that goes through every run in the document'''
    for r in doc.element.xpath('.//w:r'):
        yield r

def normalize_run(r: Run,
                  open: int,
                  close: int
                  ) -> tuple:
    '''join the text of key spanning multiple runs, in a single run

    example: ['{var','iable}'] -> ['{variable}']
    '''
    text = r.text
    open += text.count('{')
    close += text.count('}')

     #if open:
    if open > close:
        #print(r,f'O:{open} - C:{close}',r.text)
        next_r = get_next(r) # falta caso next_r es None
        next_r.text = text+next_r.text 
        r.text = ''
        open -= 1
    
    return open, close

def normalize(doc: Document) -> None:
    '''normalize every run in the document'''
    open,close = 0,0
    for r in iter_runs(doc):
        open, close = normalize_run(r,open,close)
    

