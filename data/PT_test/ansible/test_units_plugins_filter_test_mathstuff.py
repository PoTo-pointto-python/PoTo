from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from jinja2 import Environment
import ansible.plugins.filter.mathstuff as ms
from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
UNIQUE_DATA = (([1, 3, 4, 2], sorted([1, 2, 3, 4])), ([1, 3, 2, 4, 2, 3], sorted([1, 2, 3, 4])), (['a', 'b', 'c', 'd'], sorted(['a', 'b', 'c', 'd'])), (['a', 'a', 'd', 'b', 'a', 'd', 'c', 'b'], sorted(['a', 'b', 'c', 'd'])))
TWO_SETS_DATA = (([1, 2], [3, 4], ([], sorted([1, 2]), sorted([1, 2, 3, 4]), sorted([1, 2, 3, 4]))), ([1, 2, 3], [5, 3, 4], ([3], sorted([1, 2]), sorted([1, 2, 5, 4]), sorted([1, 2, 3, 4, 5]))), (['a', 'b', 'c'], ['d', 'c', 'e'], (['c'], sorted(['a', 'b']), sorted(['a', 'b', 'd', 'e']), sorted(['a', 'b', 'c', 'e', 'd']))))
env = Environment()

@pytest.mark.parametrize('data, expected', UNIQUE_DATA)
class TestUnique:

    def test_unhashable(self, data, expected):
        assert sorted(ms.unique(env, list(data))) == expected

    def test_hashable(self, data, expected):
        assert sorted(ms.unique(env, tuple(data))) == expected

@pytest.mark.parametrize('dataset1, dataset2, expected', TWO_SETS_DATA)
class TestIntersect:

    def test_unhashable(self, dataset1, dataset2, expected):
        assert sorted(ms.intersect(env, list(dataset1), list(dataset2))) == expected[0]

    def test_hashable(self, dataset1, dataset2, expected):
        assert sorted(ms.intersect(env, tuple(dataset1), tuple(dataset2))) == expected[0]

@pytest.mark.parametrize('dataset1, dataset2, expected', TWO_SETS_DATA)
class TestDifference:

    def test_unhashable(self, dataset1, dataset2, expected):
        assert sorted(ms.difference(env, list(dataset1), list(dataset2))) == expected[1]

    def test_hashable(self, dataset1, dataset2, expected):
        assert sorted(ms.difference(env, tuple(dataset1), tuple(dataset2))) == expected[1]

@pytest.mark.parametrize('dataset1, dataset2, expected', TWO_SETS_DATA)
class TestSymmetricDifference:

    def test_unhashable(self, dataset1, dataset2, expected):
        assert sorted(ms.symmetric_difference(env, list(dataset1), list(dataset2))) == expected[2]

    def test_hashable(self, dataset1, dataset2, expected):
        assert sorted(ms.symmetric_difference(env, tuple(dataset1), tuple(dataset2))) == expected[2]

class TestMin:

    def test_min(self):
        assert ms.min((1, 2)) == 1
        assert ms.min((2, 1)) == 1
        assert ms.min(('p', 'a', 'w', 'b', 'p')) == 'a'

class TestMax:

    def test_max(self):
        assert ms.max((1, 2)) == 2
        assert ms.max((2, 1)) == 2
        assert ms.max(('p', 'a', 'w', 'b', 'p')) == 'w'

class TestLogarithm:

    def test_log_non_number(self):
        with pytest.raises(AnsibleFilterTypeError, match='log\\(\\) can only be used on numbers: (a float is required|must be real number, not str)'):
            ms.logarithm('a')
        with pytest.raises(AnsibleFilterTypeError, match='log\\(\\) can only be used on numbers: (a float is required|must be real number, not str)'):
            ms.logarithm(10, base='a')

    def test_log_ten(self):
        assert ms.logarithm(10, 10) == 1.0
        assert ms.logarithm(69, 10) * 1000 // 1 == 1838

    def test_log_natural(self):
        assert ms.logarithm(69) * 1000 // 1 == 4234

    def test_log_two(self):
        assert ms.logarithm(69, 2) * 1000 // 1 == 6108

class TestPower:

    def test_power_non_number(self):
        with pytest.raises(AnsibleFilterTypeError, match='pow\\(\\) can only be used on numbers: (a float is required|must be real number, not str)'):
            ms.power('a', 10)
        with pytest.raises(AnsibleFilterTypeError, match='pow\\(\\) can only be used on numbers: (a float is required|must be real number, not str)'):
            ms.power(10, 'a')

    def test_power_squared(self):
        assert ms.power(10, 2) == 100

    def test_power_cubed(self):
        assert ms.power(10, 3) == 1000

class TestInversePower:

    def test_root_non_number(self):
        with pytest.raises(AnsibleFilterTypeError, match="root\\(\\) can only be used on numbers: (invalid literal for float\\(\\): a|could not convert string to float: a|could not convert string to float: 'a')"):
            ms.inversepower(10, 'a')
        with pytest.raises(AnsibleFilterTypeError, match='root\\(\\) can only be used on numbers: (a float is required|must be real number, not str)'):
            ms.inversepower('a', 10)

    def test_square_root(self):
        assert ms.inversepower(100) == 10
        assert ms.inversepower(100, 2) == 10

    def test_cube_root(self):
        assert ms.inversepower(27, 3) == 3

class TestRekeyOnMember:
    VALID_ENTRIES = (([{'proto': 'eigrp', 'state': 'enabled'}, {'proto': 'ospf', 'state': 'enabled'}], 'proto', {'eigrp': {'state': 'enabled', 'proto': 'eigrp'}, 'ospf': {'state': 'enabled', 'proto': 'ospf'}}), ({'eigrp': {'proto': 'eigrp', 'state': 'enabled'}, 'ospf': {'proto': 'ospf', 'state': 'enabled'}}, 'proto', {'eigrp': {'state': 'enabled', 'proto': 'eigrp'}, 'ospf': {'state': 'enabled', 'proto': 'ospf'}}))
    INVALID_ENTRIES = ((AnsibleFilterError, [{'proto': 'eigrp', 'state': 'enabled'}], 'invalid_key', 'Key invalid_key was not found'), (AnsibleFilterError, {'eigrp': {'proto': 'eigrp', 'state': 'enabled'}}, 'invalid_key', 'Key invalid_key was not found'), (AnsibleFilterError, [{'proto': 'eigrp'}, {'proto': 'ospf'}, {'proto': 'ospf'}], 'proto', 'Key ospf is not unique, cannot correctly turn into dict'), (AnsibleFilterTypeError, ['string'], 'proto', 'List item is not a valid dict'), (AnsibleFilterTypeError, [123], 'proto', 'List item is not a valid dict'), (AnsibleFilterTypeError, [[{'proto': 1}]], 'proto', 'List item is not a valid dict'), (AnsibleFilterTypeError, 'string', 'proto', 'Type is not a valid list, set, or dict'), (AnsibleFilterTypeError, 123, 'proto', 'Type is not a valid list, set, or dict'))

    @pytest.mark.parametrize('list_original, key, expected', VALID_ENTRIES)
    def test_rekey_on_member_success(self, list_original, key, expected):
        (list_original,  key,  expected) = VALID_ENTRIES[0]
        assert ms.rekey_on_member(list_original, key) == expected

    @pytest.mark.parametrize('expected_exception_type, list_original, key, expected', INVALID_ENTRIES)
    def test_fail_rekey_on_member(self, expected_exception_type, list_original, key, expected):
        (expected_exception_type,  list_original,  key,  expected) = INVALID_ENTRIES[0]
        with pytest.raises(expected_exception_type) as err:
            ms.rekey_on_member(list_original, key)
        assert err.value.message == expected

    def test_duplicate_strategy_overwrite(self):
        list_original = ({'proto': 'eigrp', 'id': 1}, {'proto': 'ospf', 'id': 2}, {'proto': 'eigrp', 'id': 3})
        expected = {'eigrp': {'proto': 'eigrp', 'id': 3}, 'ospf': {'proto': 'ospf', 'id': 2}}
        assert ms.rekey_on_member(list_original, 'proto', duplicates='overwrite') == expected

def test_TestUnique_test_unhashable():
    ret = TestUnique().test_unhashable()

def test_TestUnique_test_hashable():
    ret = TestUnique().test_hashable()

def test_TestIntersect_test_unhashable():
    ret = TestIntersect().test_unhashable()

def test_TestIntersect_test_hashable():
    ret = TestIntersect().test_hashable()

def test_TestDifference_test_unhashable():
    ret = TestDifference().test_unhashable()

def test_TestDifference_test_hashable():
    ret = TestDifference().test_hashable()

def test_TestSymmetricDifference_test_unhashable():
    ret = TestSymmetricDifference().test_unhashable()

def test_TestSymmetricDifference_test_hashable():
    ret = TestSymmetricDifference().test_hashable()

def test_TestMin_test_min():
    ret = TestMin().test_min()

def test_TestMax_test_max():
    ret = TestMax().test_max()

def test_TestLogarithm_test_log_non_number():
    ret = TestLogarithm().test_log_non_number()

def test_TestLogarithm_test_log_ten():
    ret = TestLogarithm().test_log_ten()

def test_TestLogarithm_test_log_natural():
    ret = TestLogarithm().test_log_natural()

def test_TestLogarithm_test_log_two():
    ret = TestLogarithm().test_log_two()

def test_TestPower_test_power_non_number():
    ret = TestPower().test_power_non_number()

def test_TestPower_test_power_squared():
    ret = TestPower().test_power_squared()

def test_TestPower_test_power_cubed():
    ret = TestPower().test_power_cubed()

def test_TestInversePower_test_root_non_number():
    ret = TestInversePower().test_root_non_number()

def test_TestInversePower_test_square_root():
    ret = TestInversePower().test_square_root()

def test_TestInversePower_test_cube_root():
    ret = TestInversePower().test_cube_root()

def test_TestRekeyOnMember_test_rekey_on_member_success():
    ret = TestRekeyOnMember().test_rekey_on_member_success()

def test_TestRekeyOnMember_test_fail_rekey_on_member():
    ret = TestRekeyOnMember().test_fail_rekey_on_member()

def test_TestRekeyOnMember_test_duplicate_strategy_overwrite():
    ret = TestRekeyOnMember().test_duplicate_strategy_overwrite()