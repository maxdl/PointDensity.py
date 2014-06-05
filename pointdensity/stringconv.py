def num_digits(n):
    """Return the number of digits used to represent a number
    """    
    nd = 1
    base = 10
    while 1:
        if n // base == 0:
            break
        else:
            base *= 10
            nd += 1
    return nd


def yes_or_no(i, justified=False):
    if i is None:
        return "N/A"
    elif i:
        return "yes"
    else:
        if justified:
            return " no"
        else:
            return "no"


def plurality(s, quantity):
    if quantity == 1:
        return s
    if s.lower() == "this":
        return s[0] + "hese"
    else:
        return s + "s"


def tostr(x, precision=2):
    """Convert a float/int x to a string, or a list/tuple of floats/ints to a
       tuple of strings; with exception handling"""
    try:
        li = tuple(x)
        resli = []
        for e in li:
            try:
                resli.append("%.*f" % (precision, e))
            except TypeError:
                resli.append("N/A")     
        return tuple(resli)                   
    except TypeError:
        try:
            return "%.*f" % (precision, x)
        except TypeError:
            return "N/A"


def tostr_zeropadded(x, precision=2):
    """Convert a float to a string; with exception handling.
       Padded with zeros to make number of decimals == precision
    """
    try:
        s = "%.*f" % (precision, x)
        while (len(s) - s.find('.')) < (precision + 1):
            s += "0"
        return s
    except TypeError:         # e g if x == None
        return "N/A"


def safediv(x, y):
    try:
        return x / y
    except (TypeError, ZeroDivisionError):
        return None


def safemul(x, y):
    try:
        return x * y
    except (TypeError, ZeroDivisionError):
        return None


def str_to_bool(s):
    if isinstance(s, bool):
        return s
    if not isinstance(s, str):
        raise ValueError
    if s.lower() in ('1', 'true', 'yes'):
        return True
    elif s.lower() in ('0', 'false', 'no'):
        return False
    else:
        raise ValueError


def str_to_int(s, lower=None, upper=None):
    s = int(s)
    if upper is not None and s > upper:
        raise ValueError
    if lower is not None and s < lower:
        raise ValueError
    return s