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

    host = cfg.get(section_name, "host")
    port = cfg.get(section_name, "port")
    username = cfg.get(section_name, "username")

    default_stream = None
    if cfg.has_option(section_name, "default_stream"):
        default_stream = cfg.get(section_name, "default_stream")

    return GraylogAPI(host=host, port=port, username=username, default_stream=default_stream)


def api_from_host(host, port, username):
    return GraylogAPI(host=host, port=port, username=username)