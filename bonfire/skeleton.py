#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following line in the
console_scripts section in setup.cfg:

    hello_world = bonfire.skeleton:run

Then run `python setup.py install` which will install the command `hello_world`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!

TODO for release v0.1:

"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging

from bonfire import __version__

__author__ = "Malte Harder"
__copyright__ = "Malte Harder"
__license__ = "none"

_logger = logging.getLogger(__name__)

import click
import getpass
import arrow

from .config import get_config, get_password_from_keyring, store_password_in_keyring
from .graylog_api import SearchRange, SearchQuery
from .utils import cli_error, api_from_config, api_from_host
from .output import run_logprint
from .formats import tail_format, dump_format

@click.command()
@click.option("--node", default=None,  help="Label of a preconfigured graylog node")
@click.option("-h", "--host", default=None, help="Your graylog node's host")
@click.option("--port", default=12900, help="Your graylog port")
@click.option("-u", "--username", default=None, help="Your graylog username")
@click.option("-p", "--password", default=None, help="Your graylog password")
@click.option("-k/-nk", "--keyring/--no-keyring", default=False, help="Use keyring to store/retrieve password")
@click.option("-@", "--search-from", default="5 minutes ago", help="Query range from")
@click.option("-#", "--search-to", default=None, help="Query range to (default: now)")
@click.option('-t', '--tail', 'mode', flag_value='tail', default=True, help="Show the last n lines for the query")
@click.option('-d', '--dump', 'mode', flag_value='dump', help="Print the last n lines for the query as a csv")
@click.option('-i', '--interactive', 'mode', flag_value='interactive', help="Start an interactive terminal UI")
@click.option('-o', '--output', default=None, help="Output logs to file (only tail/dump mode)")
@click.option("-f", "--follow", default=False, is_flag=True, help="Poll the logging server for new logs matching the query (sets search from to now, limit to None)")
@click.option("-l", "--interval", default=1000, help="Polling interval in ms (default: 1000)")
@click.option("-n", "--limit", default=10, help="Limit the number of results (default: 10)")
@click.option("-a", "--latency", default=2, help="Latency of polling queries (default: 2)")
@click.option('--field', '-e', multiple=True)
@click.option('--sort', '-s', default=None)
@click.option("--asc/--desc", default=False, help="Sort ascecnding / descending")
@click.argument('query', default="*")
def run(host,
        node,
        port,
        username,
        password,
        keyring,
        search_from,
        search_to,
        mode,
        output,
        follow,
        interval,
        limit,
        latency,
        field,
        sort,
        asc,
        query):
    """
    Bonfire - An interactive graylog cli client
    """

    cfg = get_config()

    # Configure the graylog API object
    if node is not None:
        # The user specified a preconfigured node, take the config from there
        gl_api = api_from_config(cfg, node_name=node)
    else:
        if host is not None:
            # A manual host configuration is used
            if username is None:
                username = click.prompt("Enter username for {host}:{port}".format(host=host, port=port),
                                        default=getpass.getuser())
            gl_api = api_from_host(host=host, port=port, username=username)
        else:
            if cfg.has_section("node:default"):
                gl_api = api_from_config(cfg)
            else:
                cli_error("Error: No host or node configuration specified and no default found.")

    if keyring and password is None:
        password = get_password_from_keyring(gl_api.host, gl_api.username)

    if password is None:
        password = click.prompt("Enter password for {username}@{host}:{port}".format(
            username=gl_api.username, host=gl_api.host, port=gl_api.port), hide_input=True)

    gl_api.password = password

    if keyring:
        store_password_in_keyring(gl_api.host, gl_api.username, password)

    # Check if the query should be retrieved from the configuration

    # Configure the base query
    sr = SearchRange(from_time=search_from, to_time=search_to)

    # Pass none if the list of fields is empty
    fields = None
    if field:
        fields = field

    if limit <= 0:
        limit = None

    # Set limit to None, sort to none and start time to now if follow is active
    if follow:
        limit = None
        sort = None
        sr.from_time = arrow.now('local').replace(seconds=-latency-1)
        sr.to_time = arrow.now('local').replace(seconds=-latency)

    # Create the initial query object
    q = SearchQuery(search_range=sr, query=query, limit=limit, fields=fields, sort=sort, ascending=asc)

    # Check the mode in which the program should run (dump, tail or interactive mode)
    if mode == "tail":
        if fields:
            formatter = tail_format(fields)
        else:
            formatter = tail_format()
    elif mode == "dump":
        formatter = dump_format()

    if mode == "tail" or mode == "dump":
        run_logprint(gl_api, q, formatter, follow, interval, latency, output)
    elif mode == "interactive":
        if output:
            raise RuntimeError("Output file option not allowed in interactive mode")

    # print(url)
    # r = requests.get(url, headers=header, auth=(name, password))
    # print(r)
    # print(r.json())
    #
    # import urwid
    #
    # def show_or_exit(key):
    #     if key in ('q', 'Q'):
    #         raise urwid.ExitMainLoop()
    #     txt.set_text(repr(key))
    #
    # txt = urwid.Text(u"Hello World")
    # fill = urwid.Filler(txt, 'top')
    # loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
    # loop.run()

if __name__ == "__main__":
    run()
