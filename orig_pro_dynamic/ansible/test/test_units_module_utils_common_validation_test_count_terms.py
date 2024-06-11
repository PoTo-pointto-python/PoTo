from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.module_utils.common.validation import count_terms

@pytest.fixture
def params():
    return {'name': 'bob', 'dest': '/etc/hosts', 'state': 'present', 'value': 5}

def test_count_terms(params):
    params = params()
    check = set(('name', 'dest'))
    assert count_terms(check, params) == 2

def test_count_terms_str_input(params):
    params = params()
    check = 'name'
    assert count_terms(check, params) == 1

def test_count_terms_tuple_input(params):
    params = params()
    check = ('name', 'dest')
    assert count_terms(check, params) == 2

def test_count_terms_list_input(params):
    params = params()
    check = ['name', 'dest']
    assert count_terms(check, params) == 2