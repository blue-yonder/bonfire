'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
from termcolor import colored
import syslog

def tail_format(fields=["source", "facility", "line", "module"], color=True):
    def format(entry):
        message_text = entry.message
        timestamp = entry.timestamp.to('local')
        level_string = entry.level

        log_color = 'green'
        log_background = None

        if entry.level == syslog.LOG_CRIT:
            log_color = 'white'
            log_background = 'on_red'
            level_string = "CRITICAL"
        elif entry.level == syslog.LOG_ERR:
            log_color = 'red'
            level_string = "ERROR   "
        elif entry.level == syslog.LOG_WARNING:
            log_color = 'yellow'
            level_string = "WARNING "
        elif entry.level == syslog.LOG_NOTICE:
            log_color = 'green'
            level_string = "NOTICE  "
        elif entry.level == syslog.LOG_INFO:
            log_color = 'green'
            level_string = "INFO    "
        elif entry.level == syslog.LOG_DEBUG:
            log_color = 'blue'
            level_string = "DEBUG   "

        if message_text:
            message_text = " " + message_text + " #"

        if "message" in fields:
            fields.remove("message")

        field_text = map(lambda f: "{}:{}".format(f, entry.message_dict.get(f, "")), fields)

        log = "{level_string}[{timestamp}]{message_text} {field_text}".format(
            timestamp=timestamp.format("YYYY-MM-DD HH:mm:ss.SS"),
            level_string=level_string,
            message_text=message_text,
            field_text="; ".join(field_text))
        if color:
            return colored(log, log_color, log_background)
        else:
            return log

    return format

def dump_format(fields=["message", "source", "facility", "line", "module"]):
    def format(entry):
        return ";".join(map(lambda f: "'{val}'".format(val=entry.message_dict.get(f,"")), fields))
    return format