'''
Created on 05.03.15

@author = mharder
'''

import requests
import arrow
import syslog
from datetime import datetime

from .dateutils import datetime_converter


class Message(object):
    def __init__(self, message_dict={}):
        self.message_dict = dict(message_dict["message"])
        self.timestamp = arrow.get(self.message_dict.get("timestamp",
            datetime.utcnow()))
        self.level = self.message_dict.get("level", syslog.LOG_INFO)
        self.message = self.message_dict.get("message", "")

    def simple_formatted(self):
        return "[{}] {}: {}".format(self.timestamp, self.level, self.message)


class SearchResult(object):
    def __init__(self, result_dict={}):
        self.query = result_dict.get("query", None)
        self.query_object = None
        self.used_indices = result_dict.get("used_indices", None)
        self.queried_range = result_dict.get("queried_range", None)
        self.range_from = arrow.get(result_dict.get("from", datetime.utcnow()))
        self.range_to = arrow.get(result_dict.get("to", datetime.utcnow()))
        self.range_duration = result_dict.get("time", None)
        self.fields = result_dict.get("fields", [])
        self.total_results = result_dict.get("total_results", None)

        self.messages = list(map(Message, result_dict.get("messages", [])))

    def simple_formatted(self):
        return "\n".join(map(lambda m: m.simple_formatted(), self.messages))


class SearchRange(object):
    def __init__(self, from_time=None, to_time=None, relative=False):
        self.from_time = datetime_converter(from_time)
        self.to_time = datetime_converter(to_time)
        self.relative = relative

    def is_relative(self):
        return self.relative

    def range_in_seconds(self):
        if self.is_relative():
            range = int(arrow.now('local').datetime.timestamp()) - \
            (self.from_time.datetime.timestamp())
        else:
            range = (self.to_time - self.from_time).seconds

        if range < 1:
            return 1
        return range


class SearchQuery(object):
    def __init__(self, search_range, query="*", limit=None, offset=None, filter=None, fields=None, sort=None,
                 ascending=False):
        self.search_range = search_range
        self.query = query
        self.limit = limit
        self.offset = offset
        self.filter = filter
        self.fields = fields
        self.sort = sort
        self.ascending = ascending

    def copy_with_range(self, search_range):
        q = SearchQuery(search_range, self.query, self.limit, self.offset, self.filter, self.fields, self.sort,
                        self.ascending)
        return q


class GraylogAPI(object):
    def __init__(self, host, port, endpoint, username, password=None, host_tz='utc', default_stream=None, scheme='http',
                 proxies=None):
        endpoint = '/' + endpoint.strip('/')

        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.host_tz = host_tz
        self.default_stream = default_stream
        self.proxies = proxies

        self.get_header = {"Accept": "application/json"}
        self.base_url = "{scheme}://{host}:{port}{endpoint}".format(host=host, port=port, scheme=scheme,
                                                                    endpoint=endpoint)
        if self.base_url[-1] != '/':
            self.base_url += '/'

    def __str__(self):
        name = "{host}:{port}".format(host=self.host, port=self.port)
        if self.endpoint != '/':
            name += self.endpoint
        return name

    def get(self, url, **kwargs):
        params = {}

        for label, item in kwargs.items():
            if isinstance(item, list):
                params[label + "[]"] = item
            else:
                params[label] = item

        r = requests.get(self.base_url + url, params=params, headers=self.get_header,
                         auth=(self.username, self.password), proxies=self.proxies)

        if r.status_code == requests.codes.ok:
            return r.json()
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

            if result.total_results > 10000:
                raise RuntimeError("Query returns more than 10000 log entries. Use offsets to query in chunks.")

            result = self.search_raw(query.query, sr, result.total_results, query.offset,
                                     query.filter, query.fields, sort)

        else:
            result = self.search_raw(query.query, query.search_range, query.limit, query.offset,
                                     query.filter, query.fields, sort)

        result.query_object = query
        return result

    def node_info(self):
        url = "system/cluster/nodes"
        return self.get(url=url)

    def cluster_info(self):
        url = "cluster"
        return self.get(url=url)

    def user_info(self, username):
        url = "users/" + username
        return self.get(url=url)

    def host_timezone(self):
        # Need to retreive server timezoneinfo to be passed to SearchQuery
        # Will be using master node's timezone and assuming
        # that's used across the cluster

        # First getting all the nodes to determine master
        masternode = None
        for nodes in self.node_info()["nodes"]:
            if nodes["is_master"] == True:
                masternode = nodes["node_id"]
                # There can only be one
                break

        # timezone of master node
        return self.cluster_info()[masternode]["timezone"]

    def streams(self):
        url = "streams"
        return self.get(url=url)

    def search_raw(self, query, search_range, limit=None, offset=None, filter=None, fields=None, sort=None):
        url = "search/universal/"
        range_args = {}

        if filter is None and self.default_stream is not None:
            filter = "streams:{}".format(self.default_stream)

        if search_range.is_relative():
            url += "relative"
            range_args["range"] = search_range.range_in_seconds()
        else:
            url += "absolute"
            range_args["from"] = search_range.from_time.to(self.host_tz).format("YYYY-MM-DD HH:mm:ss.SSS")

            if search_range.to_time is None:
                to_time = arrow.now(self.host_tz)
            else:
                to_time = search_range.to_time.to(self.host_tz)

            range_args["to"] = to_time.format("YYYY-MM-DD HH:mm:ss.SSS")

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

        return SearchResult(result)
