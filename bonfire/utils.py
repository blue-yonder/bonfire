'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
import sys
import click
import getpass
from .graylog_api import GraylogAPI


def cli_error(msg):
    click.echo(click.style(msg, fg='red'))
    sys.exit(1)


def api_from_config(cfg, node_name="default"):
    section_name = "node:" + node_name

    host = cfg.get(section_name, "host")
    port = cfg.get(section_name, "port")
    end_point = cfg.get(section_name, "end_point")

    if cfg.has_option(section_name, "username"):
        username = cfg.get(section_name, "username")
    else:
        username = getpass.getuser()

    if cfg.has_option(section_name, "tls") and cfg.get(section_name, "tls"):
        scheme = "https"
    else:
        scheme = "http"

    if cfg.has_option(section_name, "proxy"):
        proxies = {scheme: cfg.get(section_name, "proxy")}
    else:
        proxies = None

    default_stream = None
    if cfg.has_option(section_name, "default_stream"):
        default_stream = cfg.get(section_name, "default_stream")

    return GraylogAPI(host=host, port=port, end_point=end_point, username=username, default_stream=default_stream,
                      scheme=scheme, proxies=proxies)


def api_from_host(host, port, end_point, username, scheme, proxies=None):
    return GraylogAPI(host=host, port=port, end_point=end_point, username=username,
                      scheme=scheme, proxies=proxies)
