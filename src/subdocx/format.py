from babel.dates import format_date
from babel.numbers import format_decimal
from pandas import to_datetime
from datetime import datetime
import re


def _to_number(nm_str):
    if re.search(r"[,\.]", nm_str):
        return float(nm_str)
    return int(nm_str)


# format
def thd_number_sep(n):
    if isinstance(n, str):
        n = _to_number(n)

    return format_decimal(n, locale="es_CL")


def date2words(date):
    if not isinstance(date, datetime):
        date = to_datetime(date)
    return format_date(date, "d 'de' MMMM 'de' y", locale="es_CL")


def date_MMMMy(x):
    if not isinstance(x, datetime):
        x = to_datetime(x)
    return format_date(x, "MMMM, y", locale="es_CL")


def date_MMMM(x):
    if not isinstance(x, datetime):
        x = to_datetime()
    return format_date(x, "MMMM", locale="es_CL")


def toInt(x):
    return int(x)


_functions = [
    thd_number_sep,
    date2words,
    date_MMMM,
    date_MMMMy,
    toInt
]

functions = {f.__name__: f for f in _functions}
