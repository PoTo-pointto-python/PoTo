from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.common.validation import check_type_raw

def test_check_type_raw():
    test_cases = ((1, 1), ('1', '1'), ('a', 'a'), ({'k1': 'v1'}, {'k1': 'v1'}), ([1, 2], [1, 2]), (b'42', b'42'), (u'42', u'42'))
    for case in test_cases:
        assert case[1] == check_type_raw(case[0])