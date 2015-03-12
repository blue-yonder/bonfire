'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
import parsedatetime.parsedatetime as pdt
import datetime
import arrow

def datetime_parser(s):
    """
    Parse timestamp in local time
    :param s:
    :return:
    """
    try:
        dt = arrow.get(s)
        dt = dt.replace(tzinfo='local')
    except:
        c = pdt.Calendar()
        result, what = c.parse(s)

        dt = None
        if what in (1, 2):
            dt = datetime.datetime(*result[:6])
        elif what == 3:
            dt = result

        if dt is None:
            # Failed to parse
            raise ValueError("Don't understand date '"+s+"'")

        dt = arrow.get(dt)
        dt = dt.replace(tzinfo='local')
    return dt


def datetime_converter(dt):
    if dt is None:
        return None
    elif isinstance(dt, basestring):
        return datetime_parser(dt)
    else:
        return arrow.get(dt)