from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.api import rate_limit, retry
import pytest

class TestRateLimit:

    def test_ratelimit(self):

        @rate_limit(rate=1, rate_limit=1)
        def login_database():
            return 'success'
        r = login_database()
        assert r == 'success'

class TestRetry:

    def test_no_retry_required(self):
        self.counter = 0

        @retry(retries=4, retry_pause=2)
        def login_database():
            self.counter += 1
            return 'success'
        r = login_database()
        assert r == 'success'
        assert self.counter == 1

    def test_catch_exception(self):

        @retry(retries=1)
        def login_database():
            return 'success'
        with pytest.raises(Exception):
            login_database()

def test_TestRateLimit_login_database():
    ret = TestRateLimit().login_database()

def test_TestRateLimit_test_ratelimit():
    ret = TestRateLimit().test_ratelimit()

def test_TestRetry_login_database():
    ret = TestRetry().login_database()

def test_TestRetry_test_no_retry_required():
    ret = TestRetry().test_no_retry_required()

def test_TestRetry_login_database():
    ret = TestRetry().login_database()

def test_TestRetry_test_catch_exception():
    ret = TestRetry().test_catch_exception()