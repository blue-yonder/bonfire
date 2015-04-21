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
    formatter_wc = tail_format(["source", "facility", "line", "module"])
    formatter = tail_format(["source", "facility", "line", "module"], color=False)

    run_tail_test_with_formatter_wc(formatter_wc)
    run_tail_test_with_formatter(formatter)

    formatter_wc = tail_format(["source", "facility", "line", "module", "message"])
    formatter = tail_format(["source", "facility", "line", "module", "message"], color=False)
    run_tail_test_with_formatter_wc(formatter_wc)
    run_tail_test_with_formatter(formatter)


def run_tail_test_with_formatter_wc(formatter):
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

    result = "CRITICAL[{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )

    assert formatter(Message({"message": message})) == result

    message["level"] = 3
    result = "ERROR   [{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 4
    result = "WARNING [{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 5
    result = "NOTICE  [{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 6
    result = "INFO    [{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 7
    result = "DEBUG   [{}] Hallo World # source:a; facility:b; line:10; module:c".format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result