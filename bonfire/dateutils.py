'''
Created on 11.03.15

@author = mharder
'''

import parsedatetime.parsedatetime as pdt
import datetime
import arrow


def datetime_parser(s):
    """
    Parse timestamp s in local time. First the arrow parser is used, if it
    fails, the parsedatetime parser is used.

    :param s:
    :return:
    """
    try:
        ts = arrow.get(s)
        # Convert UTC to local, result of get is UTC unless it specifies
        # timezone, bonfire assumes all time to be machine local
        if ts.tzinfo == arrow.get().tzinfo:
            ts = ts.replace(tzinfo='local')
    except:
        c = pdt.Calendar()
        result, what = c.parse(s)

        ts = None
        if what in (1, 2, 3):
            ts = datetime.datetime(*result[:6])

            ts = arrow.get(ts)
            ts = ts.replace(tzinfo='local')
            return ts

    if ts is None:
        raise ValueError("Cannot parse timestamp '" + s + "'")

    return ts


def datetime_converter(dt):
    if dt is None:
        return None
    elif isinstance(dt, str):
        return datetime_parser(dt)
    else:
        return arrow.get(dt)
