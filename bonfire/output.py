'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
import time
import arrow
import sys
from kitchen.text.converters import getwriter
from .graylog_api import SearchRange


def run_logprint(api, query, formatter, follow=False, interval=0, latency=2, output=None, header=None):
    if output is None:
        output = getwriter('utf8')(sys.stdout)

    if follow:
        assert query.limit is None

        try:
            while True:
                result = run_logprint(api, query, formatter, follow=False, output=output)
                new_range = SearchRange(from_time=result.range_to,
                                        to_time=arrow.now(api.host_tz).replace(seconds=-latency))
                query = query.copy_with_range(new_range)

                time.sleep(interval / 1000.0)
        except KeyboardInterrupt:
            print("\nInterrupted follow mode. Exiting...")

    else:
        result = api.search(query, fetch_all=True)
        formatted_msgs = [formatter(m) for m in result.messages]
        formatted_msgs.reverse()

        for msg in formatted_msgs:
            print(msg, file=output)

        return result
