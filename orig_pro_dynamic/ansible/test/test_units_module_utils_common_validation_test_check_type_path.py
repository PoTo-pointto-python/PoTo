from __future__ import absolute_import, division, print_function
__metaclass__ = type
import re
import os
from ansible.module_utils.common.validation import check_type_path

def mock_expand(value):
    return re.sub('~|\\$HOME', '/home/testuser', value)

def test_check_type_path(monkeypatch):
    monkeypatch.setattr(os.path, 'expandvars', mock_expand)
    monkeypatch.setattr(os.path, 'expanduser', mock_expand)
    test_cases = (('~/foo', '/home/testuser/foo'), ('$HOME/foo', '/home/testuser/foo'), ('/home/jane', '/home/jane'), (u'/home/jané', u'/home/jané'))
    for case in test_cases:
        assert case[1] == check_type_path(case[0])