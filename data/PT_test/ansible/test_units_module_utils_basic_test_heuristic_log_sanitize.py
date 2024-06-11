from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.module_utils.basic import heuristic_log_sanitize

class TestHeuristicLogSanitize(unittest.TestCase):

    def setUp(self):
        self.URL_SECRET = 'http://username:pas:word@foo.com/data'
        self.SSH_SECRET = 'username:pas:word@foo.com/data'
        self.clean_data = repr(self._gen_data(3, True, True, 'no_secret_here'))
        self.url_data = repr(self._gen_data(3, True, True, self.URL_SECRET))
        self.ssh_data = repr(self._gen_data(3, True, True, self.SSH_SECRET))

    def _gen_data(self, records, per_rec, top_level, secret_text):
        hostvars = {'hostvars': {}}
        for i in range(1, records, 1):
            host_facts = {'host%s' % i: {'pstack': {'running': '875.1', 'symlinked': '880.0', 'tars': [], 'versions': ['885.0']}}}
            if per_rec:
                host_facts['host%s' % i]['secret'] = secret_text
            hostvars['hostvars'].update(host_facts)
        if top_level:
            hostvars['secret'] = secret_text
        return hostvars

    def test_did_not_hide_too_much(self):
        self.assertEqual(heuristic_log_sanitize(self.clean_data), self.clean_data)

    def test_hides_url_secrets(self):
        url_output = heuristic_log_sanitize(self.url_data)
        self.assertNotIn('pas:word', url_output)
        self.assertNotIn('pas', url_output)
        self.assertEqual(len(url_output), len(self.url_data))

    def test_hides_ssh_secrets(self):
        ssh_output = heuristic_log_sanitize(self.ssh_data)
        self.assertNotIn('pas:word', ssh_output)
        self.assertNotIn('pas', ssh_output)
        self.assertTrue(ssh_output.startswith("{'"))
        self.assertTrue(ssh_output.endswith('}'))
        self.assertIn(":********@foo.com/data'", ssh_output)

    def test_hides_parameter_secrets(self):
        output = heuristic_log_sanitize('token="secret", user="person", token_entry="test=secret"', frozenset(['secret']))
        self.assertNotIn('secret', output)

def test_TestHeuristicLogSanitize_setUp():
    ret = TestHeuristicLogSanitize().setUp()

def test_TestHeuristicLogSanitize__gen_data():
    ret = TestHeuristicLogSanitize()._gen_data()

def test_TestHeuristicLogSanitize_test_did_not_hide_too_much():
    ret = TestHeuristicLogSanitize().test_did_not_hide_too_much()

def test_TestHeuristicLogSanitize_test_hides_url_secrets():
    ret = TestHeuristicLogSanitize().test_hides_url_secrets()

def test_TestHeuristicLogSanitize_test_hides_ssh_secrets():
    ret = TestHeuristicLogSanitize().test_hides_ssh_secrets()

def test_TestHeuristicLogSanitize_test_hides_parameter_secrets():
    ret = TestHeuristicLogSanitize().test_hides_parameter_secrets()