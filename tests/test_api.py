'''
Created on 20.04.15

@author = mharder
'''

from __future__ import division, print_function

import bonfire.graylog_api as api
import arrow
import pytest
import httpretty


def test_message():
    ts = arrow.now()
    m = api.Message({"message": {"message": "Test", "timestamp": ts, "level": 1}})
    expected = "[{}] 1: Test".format(ts)
    assert m.simple_formatted() == expected

def test_search_result():
    ts = arrow.now()
    messages = [{"message": {"message": "Test", "timestamp": ts, "level": 1}}]*3
    expected = "[{}] 1: Test".format(ts)
    sr = api.SearchResult({"messages": messages})
    assert sr.simple_formatted() == "\n".join([expected]*3)

def test_search_range():
    sr = api.SearchRange("10 minutes ago", arrow.now())
    assert sr.range_in_seconds() == 10*60

    sr = api.SearchRange("10 minutes ago", relative=True)
    assert sr.range_in_seconds() == 10*60

    sr = api.SearchRange("10 minutes ago")
    with pytest.raises(Exception):
        sr.range_in_seconds()

    sr = api.SearchRange("10 minutes ago", "10 minutes ago")
    assert sr.range_in_seconds() == 1

def generate_search_result(total_results=1000):
    result = """{{
  "query": "*",
  "built_query": "{{\\"from\\":0,\\"size\\":150,\\"query\\":{{\\"match_all\\":{{}},\\"post_filter\\":{{\\"range\\":{{\\"timestamp\\":{{\\"from\\":\\"2015-04-20 10:33:01.000\\",\\"to\\":\\"2015-04-20 10:43:01.795\\",\\"include_lower\\":true,\\"include_upper\\":true}}}},\\"sort\\":[{{\\"timestamp\\":{{\\"order\\":\\"desc\\"}}]}}",
  "used_indices": [
    {{
      "index": "graylog2_20",
      "calculation_took_ms": 3,
      "calculated_at": "2015-04-18T20:00:10.000Z",
      "starts": "2015-04-18T20:00:10.000Z"
    }}
  ],
  "messages": [
    {{
      "message": {{
        "level": 7,
        "module": "Database",
        "streams": [
          "1111111"
        ],
        "source": "host1",
        "message": "Some message",
        "gl2_source_input": "1111111",
        "version": "1.1",
        "full_message": "Some extended message",
        "gl2_source_node": "c03b2ce1-8246-408b-9ca6-32309640d252",
        "_id": "0bc08503-e74a-11e4-a01b-52540021a4c5",
        "timestamp": "2015-04-20T10:43:01.793Z"
      }},
      "index": "graylog2_20"
    }}
  ],
  "fields": [
    "line",
    "source",
    "file",
    "text",
    "tag",
    "level",
    "module",
    "message",
    "version",
    "name",
    "facility"
  ],
  "time": 1,
  "total_results": {total_results},
  "from": "2015-04-20T10:33:01.000Z",
  "to": "2015-04-20T10:43:01.795Z"
}}
"""
    return result.format(total_results=total_results)


@httpretty.activate
def test_graylog_api_search():
    httpretty.register_uri(httpretty.GET, "http://dummyhost:80/search/universal/absolute",
                           body=generate_search_result(),
                           content_type="application/json")

    # More of some dummy tests now
    g = api.GraylogAPI("dummyhost", 80, "dummy", password="dummy")
    sr = api.SearchRange("10 minutes ago", arrow.now())
    q = api.SearchQuery(sr)
    result = g.search(q)
    assert len(result.messages) == 1
    assert result.query == "*"

    q = api.SearchQuery(sr, fields=["level", "module", "message", "timestamp"], sort="level", ascending=True)
    qq = q.copy_with_range(sr)
    result = g.search(qq)
    assert len(result.messages) == 1
    assert result.query == "*"

    q = api.SearchQuery(sr, fields=["level", "module", "message", "timestamp"], sort="level", ascending=False)
    result = g.search(q)
    assert len(result.messages) == 1
    assert result.query == "*"

    result = g.search(q, fetch_all=True)
    assert len(result.messages) == 1
    assert result.query == "*"


@httpretty.activate
def test_to_many_results():
    httpretty.register_uri(httpretty.GET, "http://dummyhost:80/search/universal/absolute",
                           body=generate_search_result(1000000),
                           content_type="application/json")

    # More of some dummy tests now
    g = api.GraylogAPI("dummyhost", 80, "dummy", password="dummy")
    sr = api.SearchRange("10 minutes ago", arrow.now())
    q = api.SearchQuery(sr)

    with pytest.raises(RuntimeError):
        result = g.search(q, fetch_all=True)


@httpretty.activate
def test_userinfo():
    httpretty.register_uri(httpretty.GET, "http://dummyhost:80/users/testuser",
                           body='{"someuser" : "info" }',
                           content_type="application/json")

    # More of some dummy tests now
    g = api.GraylogAPI("dummyhost", 80, "dummy", password="dummy")

    result = g.user_info("testuser")
    expected = {"someuser" : "info" }
    assert result == expected


@httpretty.activate
def test_streams():
    httpretty.register_uri(httpretty.GET, "http://dummyhost:80/streams",
                           body='[{"somestream" : "a" }]',
                           content_type="application/json")

    # More of some dummy tests now
    g = api.GraylogAPI("dummyhost", 80, "dummy", password="dummy")

    result = g.streams()
    expected = [{"somestream" : "a" }]
    assert result == expected