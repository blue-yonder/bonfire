=======
bonfire
=======

Bonfire is a command line interface to query Graylog searches via the REST API. It tries to emulate the feeling of using tail on a local file.

Usage
=====

Examples::

    > bonfire --node localhost -u jdoe -@ "10 minutes ago" *
    ...

    > bonfire --node localhost -u jdoe -f "source:localhost AND level:2"
    ...

Bonfire usage::

    Usage: bonfire [OPTIONS] [QUERY]

      Bonfire - An interactive graylog cli client

    Options:
      --node TEXT                     Label of a preconfigured graylog node
      -h, --host TEXT                 Your graylog node's host
      --port INTEGER                  Your graylog port (default: 12900)
      -u, --username TEXT             Your graylog username
      -p, --password TEXT             Your graylog password (default: prompt)
      -k, --keyring / -nk, --no-keyring
                                      Use keyring to store/retrieve password
      -@, --search-from TEXT          Query range from
      -#, --search-to TEXT            Query range to (default: now)
      -t, --tail                      Show the last n lines for the query
                                      (default)
      -d, --dump                      Print the query result as a csv
      -o, --output TEXT               Output logs to file (only tail/dump mode)
      -f, --follow                    Poll the logging server for new logs
                                      matching the query (sets search from to now,
                                      limit to None)
      -l, --interval INTEGER          Polling interval in ms (default: 1000)
      -n, --limit INTEGER             Limit the number of results (default: 10)
      -a, --latency INTEGER           Latency of polling queries (default: 2)
      -r, --stream TEXT               Stream ID of the stream to query (default:
                                      no stream filter)
      -e, --field TEXT                Fields to include in the query result
      -x, --template-option TEXT      Template options for the stored query
      -s, --sort TEXT                 Field used for sorting (default: timestamp)
      --asc / --desc                  Sort ascending / descending
      --help                          Show this message and exit.

Configuration
=============

Bonfire can be configured. It will look for a ``~/.bonfire.cfg`` or a ``bonfire.cfg`` (in the current directory). The
configuration file can specify API nodes. If no host is specified a node with the name ``default`` will be used. You can
also configure queries which can be referenced by starting your query with a colon::

    [node:default]
    host=1.2.3.4
    port=12900
    username=jdoe

    [node:dev]
    host=4.3.2.1
    port=12900
    username=jdoe

    [query:example]
    query=facility:*foo* source:*bar*
    from=2015-03-01 15:00:00
    limit=100
    fields=message,name,facility,source

Now you can run queries via such as::

    > bonfire --node=dev :example
    ... runs the example query on the node dev

    > bonfire :example
    ... runs the example query on the default node

Query Templates
---------------

Options
=======

Queries
=======

Known Bugs
==========

* bonfire expects graylog's timezone to be UTC.

Release Notes
=============

* v0.0.5: Clean up
    * Removed terminal UI ideas
    * Added first tests
    * Fixed date and time handling with timezones
    * Added python3 compatibility
* v0.0.4: Extended documentation & stream access
    * Use the first stream the user has access to if no stream is specified and the user has no global search rights
* v0.0.3: Small fixes
    * Use accept header in GET requests.
    * Fix bug when querying specific fields
* v0.0.1: Initial release, limited feature set.