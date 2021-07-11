# -*- coding: utf-8 -*-

'''
Created on 16.04.15

@author = mharder
'''


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
    arrow_time = arrow.get()
    timestamp = arrow_time.to('local').format("YYYY-MM-DD HH:mm:ss.SS")

    message = {
        "message": "Hällo Wörld, Здравствулте мир, γειά σου κόσμος",
        "source": "a",
        "level": 2,
        "facility": "b",
        "line": 10,
        "module": "c",
        "timestamp": arrow_time
    }

    default_formatter = tail_format(["message"])
    default_expected_result = f"{timestamp} '{message['message']}'"
    assert default_formatter(Message({"message": message})) == default_expected_result

    source_formatter = tail_format(["message", "source"])
    source_expected_result = f"{timestamp} '{message['message']}' '{message['source']}'"
    assert source_formatter(Message({"message": message})) == source_expected_result

    varied_formatter = tail_format(["line", "source", "level"])
    varied_expected_result = f"{timestamp} '{message['line']}' '{message['source']}' '{message['level']}'"
    assert varied_formatter(Message({"message": message})) == varied_expected_result


    colorful_default_formatter = tail_format(["message"], True)
    colors = ["\x1b[41m\x1b[37m", "\x1b[31m", "\x1b[33m", "\x1b[32m", "\x1b[32m", "\x1b[34m"]

    def do_colorful_test(formatter, message, expected_result, level):
        message["level"] = level
        assert formatter(Message({"message": message})) == expected_result

    for level in range(2,8):
        expected_result = "{}{} '{}'\x1b[0m".format(colors[level-2], timestamp, message['message'])
        do_colorful_test(colorful_default_formatter, message, expected_result, level)
