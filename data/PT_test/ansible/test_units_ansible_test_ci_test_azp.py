from __future__ import absolute_import, division, print_function
__metaclass__ = type
from .util import common_auth_test

def test_auth():
    from ansible_test._internal.ci.azp import AzurePipelinesAuthHelper

    class TestAzurePipelinesAuthHelper(AzurePipelinesAuthHelper):

        def __init__(self):
            self.public_key_pem = None
            self.private_key_pem = None

        def publish_public_key(self, public_key_pem):
            self.public_key_pem = public_key_pem

        def initialize_private_key(self):
            if not self.private_key_pem:
                self.private_key_pem = self.generate_private_key()
            return self.private_key_pem
    auth = TestAzurePipelinesAuthHelper()
    common_auth_test(auth)

def test_TestAzurePipelinesAuthHelper_publish_public_key():
    ret = TestAzurePipelinesAuthHelper().publish_public_key()

def test_TestAzurePipelinesAuthHelper_initialize_private_key():
    ret = TestAzurePipelinesAuthHelper().initialize_private_key()