'''
Created on 05.03.15

@author = mharder
'''

from __future__ import division, print_function
import requests
import arrow
import syslog

from .dateutils import datetime_converter


class Message(object):
    def __init__(self, message_dict={}):
        self.message_dict = dict(message_dict)
        self.timestamp = arrow.get(message_dict.get("timestamp", None))
        self.level = message_dict.get("level", syslog.LOG_INFO)
        self.message = message_dict.get("message", "")

    def simple_formatted(self):
        return "[{}] {}: {}".format(self.timestamp, self.level, self.message)


class SearchResult(object):
    def __init__(self, result_dict={}):
        self.query = result_dict.get("query", None)
        self.query_object = None
        self.used_indices = result_dict.get("used_indices", None)
        self.queried_range = result_dict.get("queried_range", None)
        self.range_from = arrow.get(result_dict.get("from", None))
        self.range_to = arrow.get(result_dict.get("to", None))
        self.range_duration = result_dict.get("time", None)
        self.fields = result_dict.get("fields", [])
        self.total_results = result_dict.get("total_results", None)

        self.messages = map(Message, result_dict.get("messages", []))

    def simple_formatted(self):
        return "\n".join(map(lambda m: m.simple_formatted(), self.messages))


class SearchRange(object):
    def __init__(self, from_time=None, to_time=None):
        self.from_time = datetime_converter(from_time)
        self.to_time = datetime_converter(to_time)

    def is_relative(self):
        return self.to_time is None

    def range_in_seconds(self):
        if self.is_relative():
            return (arrow.now('local') - self.from_time).seconds
        else:
            return (self.to_time - self.from_time).seconds


class SearchQuery(object):
    def __init__(self, search_range, query="*", limit=None, offset=None, filter=None, fields=None, sort=None, ascending=False):
        self.search_range = search_range
        self.query = query
        self.limit = limit
        self.offset = offset
        self.filter = filter
        self.fields = fields
        self.sort = sort
        self.ascending = ascending

    def copy_with_range(self, search_range):
        q = SearchQuery(search_range, self.query, self.limit, self.offset, self.filter, self.fields, self.sort, self.ascending)
        return q


class GraylogAPI(object):
    def __init__(self, host, port, username, password=None, host_tz='utc'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.host_tz = host_tz

        self.get_header = {"Accept": "application/json"}
        self.base_url = "http://{host}:{port}/".format(host=host, port=port)

    def get(self, url, **kwargs):
        params = {}

        for label, item in kwargs.iteritems():
            if isinstance(item, list):
                params[label + "[]"] = item
            else:
                params[label] = item

        r = requests.get(self.base_url + url, params=params, auth=(self.username, self.password))

        if r.status_code == requests.codes.ok:
            return SearchResult(r.json())
        else:
            r.raise_for_status()

    def search(self, query, fetch_all=False):
        sort = None
        if query.sort is not None:
            if query.ascending:
                sort = query.sort + ":asc"
            else:
                sort = query.sort + ":desc"

        if fetch_all and query.limit is None:
            result = self.search_raw(query.query, query.search_range, 1, query.offset,
                                     query.filter, query.fields, sort)

            sr = SearchRange(from_time=result.range_from, to_time=result.range_to)

            result = self.search_raw(query.query, sr, result.total_results, query.offset,
                                     query.filter, query.fields, sort)

        else:
            result = self.search_raw(query.query, query.search_range, query.limit, query.offset,
                                     query.filter, query.fields, sort)

        result.query_object = query
        return result

    def search_raw(self, query, search_range, limit=None, offset=None, filter=None, fields=None, sort=None):
        url = "search/universal/"
        range_args = {}

        if search_range.is_relative():
            url += "relative"
            range_args["range"] = search_range.range_in_seconds()
        else:
            url += "absolute"
            range_args["from"] = search_range.from_time.to(self.host_tz).format("YYYY-MM-DD HH:mm:ss")
            range_args["to"] = search_range.to_time.to(self.host_tz).format("YYYY-MM-DD HH:mm:ss")

        if fields is not None:
            fields = ",".join(fields)

        result = self.get(
            url=url,
            query=query,
            limit=limit,
            offset=offset,
            filter=filter,
            fields=fields,
            sort=sort,
            **range_args)

        return result