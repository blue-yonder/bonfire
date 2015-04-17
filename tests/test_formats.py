'''
Created on 16.04.15

@author = mharder
'''

from __future__ import division, print_function
from bonfire.formats import tail_format, dump_format
from bonfire.graylog_api import Message
import arrow


def test_dump_format():
    formatter = dump_format(["a", "b", "c"])

    assert formatter(Message({"message": {}})) == "'';'';''"
    assert formatter(Message({"message": {"a": "d"}})) == "'d';'';''"
    assert formatter(Message({"message": {"a": "d", "b": "e", "c": "f"}})) == "'d';'e';'f'"
    assert formatter(Message({"message": {"a": "d", "b": "e", "c": "f", "g": "h"}})) == "'d';'e';'f'"


def test_tail_format():
    formatter = tail_format(["source", "facility", "line", "module"])
    run_tail_test_with_formatter(formatter)

    formatter = tail_format(["source", "facility", "line", "module", "message"])
    run_tail_test_with_formatter(formatter)



def run_tail_test_with_formatter(formatter):
    ts = arrow.get()

    message = {
        "message": "Hallo World",
        "source": "a",
        "level": 2,
        "facility": "b",
        "line": 10,
        "module": "c",
        "timestamp": ts
    }

    result = "\x1b[41m\x1b[37mCRITICAL[{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )

    assert formatter(Message({"message": message})) == result

    message["level"] = 3
    result = "\x1b[31mERROR   [{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 4
    result = "\x1b[33mWARNING [{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 5
    result = "\x1b[32mNOTICE  [{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 6
    result = "\x1b[32mINFO    [{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 7
    result = "\x1b[34mDEBUG   [{}] Hallo World # source:a; facility:b; line:10; module:c\x1b[0m".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result