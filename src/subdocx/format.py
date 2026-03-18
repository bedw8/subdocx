from babel.dates import format_date


# format
def thd_number_sep(n):
    n = round(n)
    n = f"{n:,}"
    n = n.replace(",", ".")
    return n


def date2words(date):
    return format_date(date, "d 'de' MMMM 'de' y", locale="es_CL")


def date_MMMMy(x):
    return (format_date(x, "MMMM, y", locale="es_CL"),)


def date_MMMM(x):
    return (format_date(x, "MMMM", locale="es_CL"),)


def toInt(x):
    return int(x)


_functions = [
    thd_number_sep,
    date2words,
    date_MMMM,
    date_MMMMy,
]

functions = {f.__name__: f for f in _functions}
