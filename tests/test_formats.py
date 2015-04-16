'''
Created on 16.04.15

@author = mharder
'''

from __future__ import division, print_function
from bonfire.formats import tail_format, dump_format
from bonfire.graylog_api import Message

def test_dump_format():
    formatter = dump_format(["a", "b", "c"])

    assert formatter(Message({"message": {}})) == "'';'';''"
    assert formatter(Message({"message": {"a": "d"}})) == "'d';'';''"
    assert formatter(Message({"message": {"a": "d", "b": "e", "c": "f"}})) == "'d';'e';'f'"
    assert formatter(Message({"message": {"a": "d", "b": "e", "c": "f", "g": "h"}})) == "'d';'e';'f'"