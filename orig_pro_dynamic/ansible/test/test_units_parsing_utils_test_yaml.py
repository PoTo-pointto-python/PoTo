from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.errors import AnsibleParserError
from ansible.parsing.utils.yaml import from_yaml

def test_from_yaml_simple():
    assert from_yaml(u'---\n- test: 1\n  test2: "2"\n- café: "café"') == [{u'test': 1, u'test2': u'2'}, {u'café': u'café'}]

def test_bad_yaml():
    with pytest.raises(AnsibleParserError):
        from_yaml(u'foo: bar: baz')