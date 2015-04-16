'''
Created on 16.04.15

@author = mharder
'''

from __future__ import division, print_function

import arrow

from bonfire.config import get_config, get_templated_option, get_password_from_keyring, store_password_in_keyring

test_config_str = """
[node:default]
host=dummy
port=12345
username=tester

[query:test]
query=$other_arg template
from=$today $time
to=$now
"""


def test_config(monkeypatch, tmpdir):
    cfg_path = tmpdir.mkdir("config").join("bonfire.cfg")
    cfg_path.write(test_config_str)

    now = arrow.now()
    monkeypatch.setattr("os.path.expanduser", lambda x: str(cfg_path))
    monkeypatch.setattr("arrow.now", lambda x: now)

    cfg = get_config()

    assert get_templated_option(cfg, "query:test", "from") == now.format("YYYY-MM-DD") + " " + now.format("HH:mm:ss")
    assert get_templated_option(cfg, "query:test", "to") == now.format("YYYY-MM-DD HH:mm:ss.SS")
    assert get_templated_option(cfg, "query:test", "query", {"other_arg": "test"}) == "test template"

def test_keyring():
    store_password_in_keyring("dummy", "tester", "secret")
    assert get_password_from_keyring("dummy", "tester") == "secret"