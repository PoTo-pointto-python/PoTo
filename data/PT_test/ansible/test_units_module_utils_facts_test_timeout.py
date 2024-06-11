from __future__ import absolute_import, division, print_function
__metaclass__ = type
import sys
import time
import pytest
from ansible.module_utils.facts import timeout

@pytest.fixture
def set_gather_timeout_higher():
    default_timeout = timeout.GATHER_TIMEOUT
    timeout.GATHER_TIMEOUT = 5
    yield
    timeout.GATHER_TIMEOUT = default_timeout

@pytest.fixture
def set_gather_timeout_lower():
    default_timeout = timeout.GATHER_TIMEOUT
    timeout.GATHER_TIMEOUT = 2
    yield
    timeout.GATHER_TIMEOUT = default_timeout

@timeout.timeout
def sleep_amount_implicit(amount):
    time.sleep(amount)
    return 'Succeeded after {0} sec'.format(amount)

@timeout.timeout(timeout.DEFAULT_GATHER_TIMEOUT + 5)
def sleep_amount_explicit_higher(amount):
    time.sleep(amount)
    return 'Succeeded after {0} sec'.format(amount)

@timeout.timeout(2)
def sleep_amount_explicit_lower(amount):
    time.sleep(amount)
    return 'Succeeded after {0} sec'.format(amount)

def test_defaults_still_within_bounds():
    assert timeout.DEFAULT_GATHER_TIMEOUT >= 4

def test_implicit_file_default_succeeds():
    assert sleep_amount_implicit(1) == 'Succeeded after 1 sec'

def test_implicit_file_default_timesout(monkeypatch):
    monkeypatch.setattr(timeout, 'DEFAULT_GATHER_TIMEOUT', 1)
    sleep_time = timeout.DEFAULT_GATHER_TIMEOUT + 1
    with pytest.raises(timeout.TimeoutError):
        assert sleep_amount_implicit(sleep_time) == '(Not expected to succeed)'

def test_implicit_file_overridden_succeeds(set_gather_timeout_higher):
    set_gather_timeout_higher = set_gather_timeout_higher()
    sleep_time = 3
    assert sleep_amount_implicit(sleep_time) == 'Succeeded after {0} sec'.format(sleep_time)

def test_implicit_file_overridden_timesout(set_gather_timeout_lower):
    set_gather_timeout_lower = set_gather_timeout_lower()
    sleep_time = 3
    with pytest.raises(timeout.TimeoutError):
        assert sleep_amount_implicit(sleep_time) == '(Not expected to Succeed)'

def test_explicit_succeeds(monkeypatch):
    monkeypatch.setattr(timeout, 'DEFAULT_GATHER_TIMEOUT', 1)
    sleep_time = 2
    assert sleep_amount_explicit_higher(sleep_time) == 'Succeeded after {0} sec'.format(sleep_time)

def test_explicit_timeout():
    sleep_time = 3
    with pytest.raises(timeout.TimeoutError):
        assert sleep_amount_explicit_lower(sleep_time) == '(Not expected to succeed)'

@timeout.timeout(1)
def function_times_out():
    time.sleep(2)

@timeout.timeout(1)
def function_times_out_in_run_command(am):
    am.run_command([sys.executable, '-c', 'import time ; time.sleep(2)'])

@timeout.timeout(1)
def function_other_timeout():
    raise TimeoutError('Vanilla Timeout')

@timeout.timeout(1)
def function_raises():
    1 / 0

@timeout.timeout(1)
def function_catches_all_exceptions():
    try:
        time.sleep(10)
    except BaseException:
        raise RuntimeError('We should not have gotten here')

def test_timeout_raises_timeout():
    with pytest.raises(timeout.TimeoutError):
        assert function_times_out() == '(Not expected to succeed)'

@pytest.mark.parametrize('stdin', ({},), indirect=['stdin'])
def test_timeout_raises_timeout_integration_test(am):
    stdin = ({},)[0]
    with pytest.raises(timeout.TimeoutError):
        assert function_times_out_in_run_command(am) == '(Not expected to succeed)'

def test_timeout_raises_other_exception():
    with pytest.raises(ZeroDivisionError):
        assert function_raises() == '(Not expected to succeed)'

def test_exception_not_caught_by_called_code():
    with pytest.raises(timeout.TimeoutError):
        assert function_catches_all_exceptions() == '(Not expected to succeed)'