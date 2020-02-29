'''
Created on 11.03.15

@author = mharder
'''

import time
import arrow
import sys
from .graylog_api import SearchRange

def run_logprint(api, query, formatter, follow=False, interval=0, latency=2, header=None):
    if follow:
        try:
            while True:
                result = run_logprint(api, query, formatter, follow=False)
                new_range = SearchRange(from_time=result.range_to,
                        to_time="now")
                query = query.copy_with_range(new_range)
                query.limit = None

                time.sleep(interval / 1000.0)
        except KeyboardInterrupt:
            print("\nInterrupted follow mode. Exiting...")

    else:
        result = api.search(query, fetch_all=True)
        formatted_msgs = [formatter(m) for m in result.messages]
        formatted_msgs.reverse()

        for msg in formatted_msgs:
            print(msg)

        return result
