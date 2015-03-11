'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
import sys
import click
from .graylog_api import GraylogAPI


def cli_error(msg):
    click.echo(click.style(msg, fg='red'))
    sys.exit(1)


def api_from_config(cfg, node_name="default"):
    section_name = "node:" + node_name
    return GraylogAPI(host="host", port="port", username="username")


def api_from_host(host, port, username):
    return GraylogAPI(host=host, port=port, username=username)