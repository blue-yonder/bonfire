'''
Created on 16.04.15

@author = mharder
'''

from bonfire.dateutils import datetime_parser, datetime_converter
import arrow
import pytest


def test_datetime_parser():
    now = arrow.now()

    ts_tuples = [
        ("10 minutes ago", lambda x: x.shift(minutes=-10).\
                replace(microsecond=0, tzinfo='local')),
        ("1 day ago", lambda x: x.shift(days=-1)\
                .replace(microsecond=0, tzinfo='local')),
        ("yesterday midnight", lambda x: x.shift(days=-1).replace(hour=0,
            minute=0, second=0, microsecond=0, tzinfo='local')),
        ("1986-04-24 00:51:24+02:00",
            lambda x: arrow.get("1986-04-24 00:51:24+02:00")),
        ("2001-01-01 01:01:01",
            lambda x: arrow.get("2001-01-01 01:01:01").replace(tzinfo="local")),
        (now, lambda x: now)]

    for (s, ts) in ts_tuples:
        assert datetime_parser(s) == ts(now)

    with pytest.raises(ValueError):
        datetime_parser("fdjkldfhskl")


def test_datetime_converter():
    now = arrow.now()

    assert datetime_converter(None) is None
    assert datetime_converter(now) == now
    assert datetime_converter("1 day ago") == arrow.now().shift(days=-1)\
            .replace(microsecond=0, tzinfo='local')
