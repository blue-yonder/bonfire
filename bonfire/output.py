'''
Created on 11.03.15

@author = mharder
'''

from __future__ import division, print_function
import time
import arrow
from .graylog_api import SearchRange

def run_logprint(api, query, formatter, follow=False, interval=0, latency=2, output=None, header=None):
    if follow:
        assert query.limit is None

        close_output = False
        if output is not None and isinstance(output, basestring):
            output = open(output, "a")
            close_output = True

        try:
            while True:
                result = run_logprint(api, query, formatter, follow=False, output=output)
                new_range = SearchRange(from_time=result.range_to, to_time=arrow.now(api.host_tz).replace(seconds=-latency))
                query = query.copy_with_range(new_range)

                time.sleep(interval/1000.0)
        except KeyboardInterrupt:
            print("\nInterrupted follow mode. Exiting...")

        if close_output:
            output.close()

    else:
        result = api.search(query, fetch_all=True)
        formatted_msgs = map(formatter, result.messages)

        formatted_msgs.reverse()

        if output is None:
            for msg in formatted_msgs:
                print(msg)
        else:
            if isinstance(output, basestring):
                with open(output, "a") as f:
                    f.writelines(formatted_msgs)
            else:
                output.writelines(formatted_msgs)

        return result
