from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.module_utils.parsing.convert_bool import boolean

class TestBoolean:

    def test_bools(self):
        assert boolean(True) is True
        assert boolean(False) is False

    def test_none(self):
        with pytest.raises(TypeError):
            assert boolean(None, strict=True) is False
        assert boolean(None, strict=False) is False

    def test_numbers(self):
        assert boolean(1) is True
        assert boolean(0) is False
        assert boolean(0.0) is False

    def test_strings(self):
        assert boolean('true') is True
        assert boolean('TRUE') is True
        assert boolean('t') is True
        assert boolean('yes') is True
        assert boolean('y') is True
        assert boolean('on') is True

    def test_junk_values_nonstrict(self):
        assert boolean('flibbity', strict=False) is False
        assert boolean(42, strict=False) is False
        assert boolean(42.0, strict=False) is False
        assert boolean(object(), strict=False) is False

    def test_junk_values_strict(self):
        with pytest.raises(TypeError):
            assert boolean('flibbity', strict=True) is False
        with pytest.raises(TypeError):
            assert boolean(42, strict=True) is False
        with pytest.raises(TypeError):
            assert boolean(42.0, strict=True) is False
        with pytest.raises(TypeError):
            assert boolean(object(), strict=True) is False

def test_TestBoolean_test_bools():
    ret = TestBoolean().test_bools()

def test_TestBoolean_test_none():
    ret = TestBoolean().test_none()

def test_TestBoolean_test_numbers():
    ret = TestBoolean().test_numbers()

def test_TestBoolean_test_strings():
    ret = TestBoolean().test_strings()

def test_TestBoolean_test_junk_values_nonstrict():
    ret = TestBoolean().test_junk_values_nonstrict()

def test_TestBoolean_test_junk_values_strict():
    ret = TestBoolean().test_junk_values_strict()