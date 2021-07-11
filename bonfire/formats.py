'''
Created on 11.03.15

@author = mharder
'''

from termcolor import colored
import syslog

def get_log_color_and_background(level):
    log_color = 'green'
    log_background = None

    if level == syslog.LOG_CRIT:
        log_color = 'white'
        log_background = 'on_red'
    elif level == syslog.LOG_ERR:
        log_color = 'red'
    elif level == syslog.LOG_WARNING:
        log_color = 'yellow'
    elif level == syslog.LOG_NOTICE:
        log_color = 'green'
    elif level == syslog.LOG_INFO:
        log_color = 'green'
    elif level == syslog.LOG_DEBUG:
        log_color = 'blue'

    return log_color, log_background

def tail_format(fields, colorful=False):
    return formatter(fields, " ", colorful)

def dump_format(fields, colorful=False):
    return formatter(fields, ";", colorful)

def formatter(fields, seperator, colorful):
    def format(entry):
        timestamp = entry.timestamp.to('local').format("YYYY-MM-DD HH:mm:ss.SS")
        msg = timestamp + seperator + seperator.join(map(lambda f: u"'{val}'"\
                .format(val=entry.message_dict.get(f, "")), fields))
        if colorful:
            log_color, log_background = get_log_color_and_background(entry.level)
            return colored(msg, log_color, log_background)
        return msg
    return format
