'''
Created on 05.03.15

@author = mharder
'''

from __future__ import division, print_function

import ConfigParser
import os
import keyring


def get_config():
    config = ConfigParser.ConfigParser()
    config.read(['bonfire.cfg', os.path.expanduser('~/.bonfire.cfg')])

    return config


def store_password_in_keyring(host, username, password):
    keyring.set_password('bonfire_' + host, username, password)


def get_password_from_keyring(host, username):
    return keyring.get_password('bonfire_' + host, username)