#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

# Todo:

import logging
from bonfire import __version__

__author__ = "Malte Harder"
__copyright__ = "Blue Yonder"
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)

import click
import getpass
import arrow


from .config import get_config, get_password_from_keyring, store_password_in_keyring, get_templated_option
from .graylog_api import SearchRange, SearchQuery
from .utils import cli_error, api_from_config, api_from_host
from .output import run_logprint
from .formats import tail_format, dump_format

@click.command()
@click.option("--node", default=None,  help="Label of a preconfigured graylog node")
@click.option("-h", "--host", default=None, help="Your graylog node's host")
@click.option("--port", default=12900, help="Your graylog port (default: 12900)")
@click.option("-u", "--username", default=None, help="Your graylog username")
@click.option("-p", "--password", default=None, help="Your graylog password (default: prompt)")
@click.option("-k/-nk", "--keyring/--no-keyring", default=False, help="Use keyring to store/retrieve password")
@click.option("-@", "--search-from", default="5 minutes ago", help="Query range from")
@click.option("-#", "--search-to", default=None, help="Query range to (default: now)")
@click.option('-t', '--tail', 'mode', flag_value='tail', default=True, help="Show the last n lines for the query (default)")
@click.option('-d', '--dump', 'mode', flag_value='dump', help="Print the query result as a csv")
@click.option('-o', '--output', default=None, help="Output logs to file (only tail/dump mode)")
@click.option("-f", "--follow", default=False, is_flag=True, help="Poll the logging server for new logs matching the query (sets search from to now, limit to None)")
@click.option("-l", "--interval", default=1000, help="Polling interval in ms (default: 1000)")
@click.option("-n", "--limit", default=10, help="Limit the number of results (default: 10)")
@click.option("-a", "--latency", default=2, help="Latency of polling queries (default: 2)")
@click.option("-r", "--stream", default=None, help="Stream ID of the stream to query (default: no stream filter)")
@click.option('--field', '-e', multiple=True, help="Fields to include in the query result")
@click.option('--template-option', '-x', multiple=True, help="Template options for the stored query")
@click.option('--sort', '-s', default=None, help="Field used for sorting (default: timestamp)")
@click.option("--asc/--desc", default=False, help="Sort ascending / descending")
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
        stream,
        field,
        template_option,
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

    username = gl_api.username

    # Check if the query should be retrieved from the configuration
    if query[0] == ":":
        section_name = "query" + query
        template_options = dict(map(lambda t: tuple(str(t).split("=", 1)), template_option))
        query = get_templated_option(cfg, section_name, "query", template_options)

        if cfg.has_option(section_name, "limit"):
            limit = get_templated_option(cfg, section_name, "limit", template_options)

        if cfg.has_option(section_name, "from"):
            search_from = get_templated_option(cfg, section_name, "from", template_options)

        if cfg.has_option(section_name, "to"):
            search_to = get_templated_option(cfg, section_name, "to", template_options)

        if cfg.has_option(section_name, "sort"):
            sort = get_templated_option(cfg, section_name, "sort", template_options)

        if cfg.has_option(section_name, "asc"):
            asc = get_templated_option(cfg, section_name, "asc", template_options)

        if cfg.has_option(section_name, "fields"):
            field = get_templated_option(cfg, section_name, "fields", template_options).split(",")

        if cfg.has_option(section_name, "stream"):
            stream = get_templated_option(cfg, section_name, "stream", template_options)

    # Configure the base query
    sr = SearchRange(from_time=search_from, to_time=search_to)

    # Pass none if the list of fields is empty
    fields = None
    if field:
        fields = list(field)

    if limit <= 0:
        limit = None

    # Set limit to None, sort to none and start time to now, if follow is active
    if follow:
        limit = None
        sort = None
        sr.from_time = arrow.now('local').replace(seconds=-latency-1)
        sr.to_time = arrow.now('local').replace(seconds=-latency)

    # Get the user permissions
    userinfo = gl_api.user_info(username)

    # If the permissions are not set or a stream is specified
    stream_filter = None
    if stream or (userinfo["permissions"] != ["*"] and gl_api.default_stream is None):
        if not stream:
            streams = gl_api.streams()["streams"]
            click.echo("Please select a stream to query:")
            for i, stream in enumerate(streams):
                click.echo("{}: Stream '{}' (id: {})".format(i, stream["title"], stream["id"]))
            i = click.prompt("Enter stream number:", type=int, default=0)
            stream = streams[i]["id"]
        stream_filter = "streams:{}".format(stream)

    # Create the initial query object
    q = SearchQuery(search_range=sr, query=query, limit=limit, filter=stream_filter, fields=fields, sort=sort, ascending=asc)

    # Check the mode in which the program should run (dump, tail or interactive mode)
    if mode == "tail":
        if fields:
            formatter = tail_format(fields)
        else:
            formatter = tail_format()
    elif mode == "dump":
        formatter = dump_format()

    run_logprint(gl_api, q, formatter, follow, interval, latency, output)

if __name__ == "__main__":
    run()
