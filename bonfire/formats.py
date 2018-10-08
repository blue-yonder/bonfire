'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
from termcolor import colored
import syslog
import six

def formatter(fields, seperator):
    def format(entry):
        timestamp = entry.timestamp.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
        return timestamp + seperator + seperator.join(map(lambda f: u"'{val}'"\
                .format(val=entry.message_dict.get(f, "")), fields))
    return format

def tail_format(fields):
    return formatter(fields, " ")

def dump_format(fields):
    return formatter(fields, ";")
