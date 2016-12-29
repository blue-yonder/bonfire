# -*- coding: utf-8 -*-

'''
Created on 16.04.15

@author = mharder
'''

from __future__ import division, print_function

import six

from bonfire.formats import tail_format, dump_format
from bonfire.graylog_api import Message
import arrow


def test_dump_format():
    ts = arrow.get()
    ts_str = ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    formatter = dump_format(["a", "b", "c"])

    assert formatter(Message({"timestamp": ts, "message": {}})) == "{};'';'';''".format(ts_str)
    assert formatter(Message({"timestamp": ts, "message": {"a": "d"}})) == "{};'d';'';''".format(ts_str)
    assert formatter(Message({"timestamp": ts, "message": {"a": "d", "b": "e", "c": "f"}})) == "{};'d';'e';'f'".format(ts_str)
    assert formatter(Message({"timestamp": ts, "message": {"a": "d", "b": "e", "c": "f", "g": "h"}})) == "{};'d';'e';'f'".format(ts_str)


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
        "message": "Hällo Wörld, Здравствулте мир, γειά σου κόσμος",
        "source": "a",
        "level": 2,
        "facility": "b",
        "line": 10,
        "module": "c",
        "timestamp": ts
    }

    result = six.u("\x1b[41m\x1b[37mCRITICAL[{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )

    assert formatter(Message({"message": message})) == result

    message["level"] = 3
    result = six.u("\x1b[31mERROR   [{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 4
    result = six.u("\x1b[33mWARNING [{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 5
    result = six.u("\x1b[32mNOTICE  [{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 6
    result = six.u("\x1b[32mINFO    [{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
        ts.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
    )
    assert formatter(Message({"message": message})) == result

    message["level"] = 7
    result = six.u("\x1b[34mDEBUG   [{}] Hällo Wörld, Здравствулте мир, γειά σου κόσμος # source:a; facility:b; line:10; module:c\x1b[0m").format(
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
