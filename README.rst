=======
bonfire
=======

Bonfire is a command line interface to query Graylog searches via the REST API. It tries to emulate the feeling of using tail on a local file.

Usage
=====

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
      -t, --tail                      Show the last n lines for the query (default)
      -d, --dump                      Print the query result as a csv
      -i, --interactive               Start an interactive terminal UI
      -o, --output TEXT               Output logs to file (only tail/dump mode)
      -f, --follow                    Poll the logging server for new logs
                                      matching the query (sets search from to now,
                                      limit to None)
      -l, --interval INTEGER          Polling interval in ms (default: 1000)
      -n, --limit INTEGER             Limit the number of results (default: 10)
      -a, --latency INTEGER           Latency of polling queries (default: 2)
      -e, --field TEXT                Fields to include in the query result
      -x, --template-option TEXT      Template options for the stored query
      -s, --sort TEXT                 Field used for sorting (default: timestamp)
      --asc / --desc                  Sort ascecnding / descending
      --help                          Show this message and exit.



Connections
===========

Options
=======

Queries
=======

Configuration
=============
