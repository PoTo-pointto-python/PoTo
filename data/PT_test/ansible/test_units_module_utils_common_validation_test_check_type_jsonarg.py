from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.module_utils._text import to_native
from ansible.module_utils.common.validation import check_type_jsonarg

def test_check_type_jsonarg():
    test_cases = (('a', 'a'), ('a  ', 'a'), (b'99', b'99'), (b'99  ', b'99'), ({'k1': 'v1'}, '{"k1": "v1"}'), ([1, 'a'], '[1, "a"]'), ((1, 2, 'three'), '[1, 2, "three"]'))
    for case in test_cases:
        assert case[1] == check_type_jsonarg(case[0])

def test_check_type_jsonarg_fail():
    test_cases = (1.5, 910313498012384012341982374109384098)
    for case in test_cases:
        with pytest.raises(TypeError) as e:
            check_type_jsonarg(case)
        assert 'cannot be converted to a json string' in to_native(e.value)