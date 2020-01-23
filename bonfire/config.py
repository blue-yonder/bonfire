'''
Created on 05.03.15

@author = mharder
'''

import configparser

import os
import keyring
from string import Template
import arrow


def get_config():
    config = configparser.ConfigParser()
    config.read(['bonfire.cfg', os.path.expanduser('~/.bonfire.cfg')])

    return config


def get_templated_option(cfg, section, option, kwargs={}):
    template = Template(cfg.get(section, option))

    dt = arrow.now('local')

    mapping = {
        "today": dt.format("YYYY-MM-DD"),
        "time": dt.format("HH:mm:ss"),
        "now": dt.format("YYYY-MM-DD HH:mm:ss.SS")
    }

    return template.substitute(mapping, **kwargs)


def store_password_in_keyring(host, username, password):
    keyring.set_password('bonfire_' + host, username, password)


def get_password_from_keyring(host, username):
    return keyring.get_password('bonfire_' + host, username)
