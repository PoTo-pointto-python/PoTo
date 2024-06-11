from __future__ import absolute_import, division, print_function
__metaclass__ = type
try:
    import passlib
    from passlib.handlers import pbkdf2
except ImportError:
    passlib = None
    pbkdf2 = None
import pytest
from units.mock.loader import DictDataLoader
from units.compat import unittest
from units.compat.mock import mock_open, patch
from ansible.errors import AnsibleError
from ansible.module_utils.six import text_type
from ansible.module_utils.six.moves import builtins
from ansible.module_utils._text import to_bytes
from ansible.plugins.loader import PluginLoader
from ansible.plugins.lookup import password
DEFAULT_CHARS = sorted([u'ascii_letters', u'digits', u'.,:-_'])
DEFAULT_CANDIDATE_CHARS = u'.,:-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
old_style_params_data = (dict(term=u'/path/to/file', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/embedded spaces and/file', filename=u'/path/with/embedded spaces and/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/equals/cn=com.ansible', filename=u'/path/with/equals/cn=com.ansible', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/unicode/くらとみ/file', filename=u'/path/with/unicode/くらとみ/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/utf 8 and spaces/くらとみ/file', filename=u'/path/with/utf 8 and spaces/くらとみ/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/encoding=unicode/くらとみ/file', filename=u'/path/with/encoding=unicode/くらとみ/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/with/encoding=unicode/くらとみ/and spaces file', filename=u'/path/with/encoding=unicode/くらとみ/and spaces file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/to/file length=42', filename=u'/path/to/file', params=dict(length=42, encrypt=None, chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/to/file encrypt=pbkdf2_sha256', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt='pbkdf2_sha256', chars=DEFAULT_CHARS), candidate_chars=DEFAULT_CANDIDATE_CHARS), dict(term=u'/path/to/file chars=abcdefghijklmnop', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'abcdefghijklmnop']), candidate_chars=u'abcdefghijklmnop'), dict(term=u'/path/to/file chars=digits,abc,def', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'digits', u'abc', u'def'])), candidate_chars=u'abcdef0123456789'), dict(term=u'/path/to/file chars=abcdefghijklmnop,,digits', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'abcdefghijklmnop', u',', u'digits'])), candidate_chars=u',abcdefghijklmnop0123456789'), dict(term=u'/path/to/file chars=,,', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u',']), candidate_chars=u','), dict(term=u'/path/to/file chars=digits,=,,', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'digits', u'=', u','])), candidate_chars=u',=0123456789'), dict(term=u'/path/to/file chars=digits,abc=def', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'digits', u'abc=def'])), candidate_chars=u'abc=def0123456789'), dict(term=u'/path/to/file chars=digits,くらとみ,,', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'digits', u'くらとみ', u','])), candidate_chars=u',0123456789くらとみ'), dict(term=u'/path/to/file chars=くらとみ', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'くらとみ'])), candidate_chars=u'くらとみ'), dict(term=u'/path/to/file_with:colon chars=ascii_letters,digits', filename=u'/path/to/file_with:colon', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=sorted([u'ascii_letters', u'digits'])), candidate_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), dict(term=u'/path/with/embedded spaces and/file chars=abc=def', filename=u'/path/with/embedded spaces and/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'abc=def']), candidate_chars=u'abc=def'), dict(term=u'/path/with/equals/cn=com.ansible chars=abc=def', filename=u'/path/with/equals/cn=com.ansible', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'abc=def']), candidate_chars=u'abc=def'), dict(term=u'/path/with/unicode/くらとみ/file chars=くらとみ', filename=u'/path/with/unicode/くらとみ/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'くらとみ']), candidate_chars=u'くらとみ'))

class TestParseParameters(unittest.TestCase):

    def test(self):
        for testcase in old_style_params_data:
            (filename, params) = password._parse_parameters(testcase['term'])
            params['chars'].sort()
            self.assertEqual(filename, testcase['filename'])
            self.assertEqual(params, testcase['params'])

    def test_unrecognized_value(self):
        testcase = dict(term=u'/path/to/file chars=くらとみi  sdfsdf', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'くらとみ']), candidate_chars=u'くらとみ')
        self.assertRaises(AnsibleError, password._parse_parameters, testcase['term'])

    def test_invalid_params(self):
        testcase = dict(term=u'/path/to/file chars=くらとみi  somethign_invalid=123', filename=u'/path/to/file', params=dict(length=password.DEFAULT_LENGTH, encrypt=None, chars=[u'くらとみ']), candidate_chars=u'くらとみ')
        self.assertRaises(AnsibleError, password._parse_parameters, testcase['term'])

class TestReadPasswordFile(unittest.TestCase):

    def setUp(self):
        self.os_path_exists = password.os.path.exists

    def tearDown(self):
        password.os.path.exists = self.os_path_exists

    def test_no_password_file(self):
        password.os.path.exists = lambda x: False
        self.assertEqual(password._read_password_file(b'/nonexistent'), None)

    def test_with_password_file(self):
        password.os.path.exists = lambda x: True
        with patch.object(builtins, 'open', mock_open(read_data=b'Testing\n')) as m:
            self.assertEqual(password._read_password_file(b'/etc/motd'), u'Testing')

class TestGenCandidateChars(unittest.TestCase):

    def _assert_gen_candidate_chars(self, testcase):
        expected_candidate_chars = testcase['candidate_chars']
        params = testcase['params']
        chars_spec = params['chars']
        res = password._gen_candidate_chars(chars_spec)
        self.assertEqual(res, expected_candidate_chars)

    def test_gen_candidate_chars(self):
        for testcase in old_style_params_data:
            self._assert_gen_candidate_chars(testcase)

class TestRandomPassword(unittest.TestCase):

    def _assert_valid_chars(self, res, chars):
        for res_char in res:
            self.assertIn(res_char, chars)

    def test_default(self):
        res = password.random_password()
        self.assertEqual(len(res), password.DEFAULT_LENGTH)
        self.assertTrue(isinstance(res, text_type))
        self._assert_valid_chars(res, DEFAULT_CANDIDATE_CHARS)

    def test_zero_length(self):
        res = password.random_password(length=0)
        self.assertEqual(len(res), 0)
        self.assertTrue(isinstance(res, text_type))
        self._assert_valid_chars(res, u',')

    def test_just_a_common(self):
        res = password.random_password(length=1, chars=u',')
        self.assertEqual(len(res), 1)
        self.assertEqual(res, u',')

    def test_free_will(self):
        res = password.random_password(length=11, chars=u'a')
        self.assertEqual(len(res), 11)
        self.assertEqual(res, 'aaaaaaaaaaa')
        self._assert_valid_chars(res, u'a')

    def test_unicode(self):
        res = password.random_password(length=11, chars=u'くらとみ')
        self._assert_valid_chars(res, u'くらとみ')
        self.assertEqual(len(res), 11)

    def test_gen_password(self):
        for testcase in old_style_params_data:
            params = testcase['params']
            candidate_chars = testcase['candidate_chars']
            params_chars_spec = password._gen_candidate_chars(params['chars'])
            password_string = password.random_password(length=params['length'], chars=params_chars_spec)
            self.assertEqual(len(password_string), params['length'], msg='generated password=%s has length (%s) instead of expected length (%s)' % (password_string, len(password_string), params['length']))
            for char in password_string:
                self.assertIn(char, candidate_chars, msg='%s not found in %s from chars spect %s' % (char, candidate_chars, params['chars']))

class TestParseContent(unittest.TestCase):

    def test_empty_password_file(self):
        (plaintext_password, salt) = password._parse_content(u'')
        self.assertEqual(plaintext_password, u'')
        self.assertEqual(salt, None)

    def test(self):
        expected_content = u'12345678'
        file_content = expected_content
        (plaintext_password, salt) = password._parse_content(file_content)
        self.assertEqual(plaintext_password, expected_content)
        self.assertEqual(salt, None)

    def test_with_salt(self):
        expected_content = u'12345678 salt=87654321'
        file_content = expected_content
        (plaintext_password, salt) = password._parse_content(file_content)
        self.assertEqual(plaintext_password, u'12345678')
        self.assertEqual(salt, u'87654321')

class TestFormatContent(unittest.TestCase):

    def test_no_encrypt(self):
        self.assertEqual(password._format_content(password=u'hunter42', salt=u'87654321', encrypt=False), u'hunter42 salt=87654321')

    def test_no_encrypt_no_salt(self):
        self.assertEqual(password._format_content(password=u'hunter42', salt=None, encrypt=None), u'hunter42')

    def test_encrypt(self):
        self.assertEqual(password._format_content(password=u'hunter42', salt=u'87654321', encrypt='pbkdf2_sha256'), u'hunter42 salt=87654321')

    def test_encrypt_no_salt(self):
        self.assertRaises(AssertionError, password._format_content, u'hunter42', None, 'pbkdf2_sha256')

class TestWritePasswordFile(unittest.TestCase):

    def setUp(self):
        self.makedirs_safe = password.makedirs_safe
        self.os_chmod = password.os.chmod
        password.makedirs_safe = lambda path, mode: None
        password.os.chmod = lambda path, mode: None

    def tearDown(self):
        password.makedirs_safe = self.makedirs_safe
        password.os.chmod = self.os_chmod

    def test_content_written(self):
        with patch.object(builtins, 'open', mock_open()) as m:
            password._write_password_file(b'/this/is/a/test/caf\xc3\xa9', u'Testing Café')
            m.assert_called_once_with(b'/this/is/a/test/caf\xc3\xa9', 'wb')
            m().write.assert_called_once_with(u'Testing Café\n'.encode('utf-8'))

class BaseTestLookupModule(unittest.TestCase):

    def setUp(self):
        self.fake_loader = DictDataLoader({'/path/to/somewhere': 'sdfsdf'})
        self.password_lookup = password.LookupModule(loader=self.fake_loader)
        self.os_path_exists = password.os.path.exists
        self.os_open = password.os.open
        password.os.open = lambda path, flag: None
        self.os_close = password.os.close
        password.os.close = lambda fd: None
        self.os_remove = password.os.remove
        password.os.remove = lambda path: None
        self.makedirs_safe = password.makedirs_safe
        password.makedirs_safe = lambda path, mode: None

    def tearDown(self):
        password.os.path.exists = self.os_path_exists
        password.os.open = self.os_open
        password.os.close = self.os_close
        password.os.remove = self.os_remove
        password.makedirs_safe = self.makedirs_safe

class TestLookupModuleWithoutPasslib(BaseTestLookupModule):

    @patch.object(PluginLoader, '_get_paths')
    @patch('ansible.plugins.lookup.password._write_password_file')
    def test_no_encrypt(self, mock_get_paths, mock_write_file):
        mock_get_paths.return_value = ['/path/one', '/path/two', '/path/three']
        results = self.password_lookup.run([u'/path/to/somewhere'], None)
        for result in results:
            assert len(result) == password.DEFAULT_LENGTH
            assert isinstance(result, text_type)

    @patch.object(PluginLoader, '_get_paths')
    @patch('ansible.plugins.lookup.password._write_password_file')
    def test_password_already_created_no_encrypt(self, mock_get_paths, mock_write_file):
        mock_get_paths.return_value = ['/path/one', '/path/two', '/path/three']
        password.os.path.exists = lambda x: x == to_bytes('/path/to/somewhere')
        with patch.object(builtins, 'open', mock_open(read_data=b'hunter42 salt=87654321\n')) as m:
            results = self.password_lookup.run([u'/path/to/somewhere chars=anything'], None)
        for result in results:
            self.assertEqual(result, u'hunter42')

    @patch.object(PluginLoader, '_get_paths')
    @patch('ansible.plugins.lookup.password._write_password_file')
    def test_only_a(self, mock_get_paths, mock_write_file):
        mock_get_paths.return_value = ['/path/one', '/path/two', '/path/three']
        results = self.password_lookup.run([u'/path/to/somewhere chars=a'], None)
        for result in results:
            self.assertEqual(result, u'a' * password.DEFAULT_LENGTH)

    @patch('time.sleep')
    def test_lock_been_held(self, mock_sleep):
        password.os.path.exists = lambda x: True
        try:
            with patch.object(builtins, 'open', mock_open(read_data=b'hunter42 salt=87654321\n')) as m:
                results = self.password_lookup.run([u'/path/to/somewhere chars=anything'], None)
                self.fail("Lookup didn't timeout when lock already been held")
        except AnsibleError:
            pass

    def test_lock_not_been_held(self):
        password.os.path.exists = lambda x: x == to_bytes('/path/to/somewhere')
        try:
            with patch.object(builtins, 'open', mock_open(read_data=b'hunter42 salt=87654321\n')) as m:
                results = self.password_lookup.run([u'/path/to/somewhere chars=anything'], None)
        except AnsibleError:
            self.fail('Lookup timeouts when lock is free')
        for result in results:
            self.assertEqual(result, u'hunter42')

@pytest.mark.skipif(passlib is None, reason='passlib must be installed to run these tests')
class TestLookupModuleWithPasslib(BaseTestLookupModule):

    def setUp(self):
        super(TestLookupModuleWithPasslib, self).setUp()
        self.sha256 = passlib.registry.get_crypt_handler('pbkdf2_sha256')
        sha256_for_tests = pbkdf2.create_pbkdf2_hash('sha256', 32, 20000)
        passlib.registry.register_crypt_handler(sha256_for_tests, force=True)

    def tearDown(self):
        super(TestLookupModuleWithPasslib, self).tearDown()
        passlib.registry.register_crypt_handler(self.sha256, force=True)

    @patch.object(PluginLoader, '_get_paths')
    @patch('ansible.plugins.lookup.password._write_password_file')
    def test_encrypt(self, mock_get_paths, mock_write_file):
        mock_get_paths.return_value = ['/path/one', '/path/two', '/path/three']
        results = self.password_lookup.run([u'/path/to/somewhere encrypt=pbkdf2_sha256'], None)
        expected_password_length = 76
        for result in results:
            self.assertEqual(len(result), expected_password_length)
            str_parts = result.split('$', 5)
            crypt_parts = passlib.hash.pbkdf2_sha256.parsehash(result)
            self.assertEqual(str_parts[1], 'pbkdf2-sha256')
            self.assertEqual(len(str_parts), 5)
            self.assertEqual(int(str_parts[2]), crypt_parts['rounds'])
            self.assertIsInstance(result, text_type)

    @patch.object(PluginLoader, '_get_paths')
    @patch('ansible.plugins.lookup.password._write_password_file')
    def test_password_already_created_encrypt(self, mock_get_paths, mock_write_file):
        mock_get_paths.return_value = ['/path/one', '/path/two', '/path/three']
        password.os.path.exists = lambda x: x == to_bytes('/path/to/somewhere')
        with patch.object(builtins, 'open', mock_open(read_data=b'hunter42 salt=87654321\n')) as m:
            results = self.password_lookup.run([u'/path/to/somewhere chars=anything encrypt=pbkdf2_sha256'], None)
        for result in results:
            self.assertEqual(result, u'$pbkdf2-sha256$20000$ODc2NTQzMjE$Uikde0cv0BKaRaAXMrUQB.zvG4GmnjClwjghwIRf2gU')

def test_TestParseParameters_test():
    ret = TestParseParameters().test()

def test_TestParseParameters_test_unrecognized_value():
    ret = TestParseParameters().test_unrecognized_value()

def test_TestParseParameters_test_invalid_params():
    ret = TestParseParameters().test_invalid_params()

def test_TestReadPasswordFile_setUp():
    ret = TestReadPasswordFile().setUp()

def test_TestReadPasswordFile_tearDown():
    ret = TestReadPasswordFile().tearDown()

def test_TestReadPasswordFile_test_no_password_file():
    ret = TestReadPasswordFile().test_no_password_file()

def test_TestReadPasswordFile_test_with_password_file():
    ret = TestReadPasswordFile().test_with_password_file()

def test_TestGenCandidateChars__assert_gen_candidate_chars():
    ret = TestGenCandidateChars()._assert_gen_candidate_chars()

def test_TestGenCandidateChars_test_gen_candidate_chars():
    ret = TestGenCandidateChars().test_gen_candidate_chars()

def test_TestRandomPassword__assert_valid_chars():
    ret = TestRandomPassword()._assert_valid_chars()

def test_TestRandomPassword_test_default():
    ret = TestRandomPassword().test_default()

def test_TestRandomPassword_test_zero_length():
    ret = TestRandomPassword().test_zero_length()

def test_TestRandomPassword_test_just_a_common():
    ret = TestRandomPassword().test_just_a_common()

def test_TestRandomPassword_test_free_will():
    ret = TestRandomPassword().test_free_will()

def test_TestRandomPassword_test_unicode():
    ret = TestRandomPassword().test_unicode()

def test_TestRandomPassword_test_gen_password():
    ret = TestRandomPassword().test_gen_password()

def test_TestParseContent_test_empty_password_file():
    ret = TestParseContent().test_empty_password_file()

def test_TestParseContent_test():
    ret = TestParseContent().test()

def test_TestParseContent_test_with_salt():
    ret = TestParseContent().test_with_salt()

def test_TestFormatContent_test_no_encrypt():
    ret = TestFormatContent().test_no_encrypt()

def test_TestFormatContent_test_no_encrypt_no_salt():
    ret = TestFormatContent().test_no_encrypt_no_salt()

def test_TestFormatContent_test_encrypt():
    ret = TestFormatContent().test_encrypt()

def test_TestFormatContent_test_encrypt_no_salt():
    ret = TestFormatContent().test_encrypt_no_salt()

def test_TestWritePasswordFile_setUp():
    ret = TestWritePasswordFile().setUp()

def test_TestWritePasswordFile_tearDown():
    ret = TestWritePasswordFile().tearDown()

def test_TestWritePasswordFile_test_content_written():
    ret = TestWritePasswordFile().test_content_written()

def test_BaseTestLookupModule_setUp():
    ret = BaseTestLookupModule().setUp()

def test_BaseTestLookupModule_tearDown():
    ret = BaseTestLookupModule().tearDown()

def test_TestLookupModuleWithoutPasslib_test_no_encrypt():
    ret = TestLookupModuleWithoutPasslib().test_no_encrypt()

def test_TestLookupModuleWithoutPasslib_test_password_already_created_no_encrypt():
    ret = TestLookupModuleWithoutPasslib().test_password_already_created_no_encrypt()

def test_TestLookupModuleWithoutPasslib_test_only_a():
    ret = TestLookupModuleWithoutPasslib().test_only_a()

def test_TestLookupModuleWithoutPasslib_test_lock_been_held():
    ret = TestLookupModuleWithoutPasslib().test_lock_been_held()

def test_TestLookupModuleWithoutPasslib_test_lock_not_been_held():
    ret = TestLookupModuleWithoutPasslib().test_lock_not_been_held()

def test_TestLookupModuleWithPasslib_setUp():
    ret = TestLookupModuleWithPasslib().setUp()

def test_TestLookupModuleWithPasslib_tearDown():
    ret = TestLookupModuleWithPasslib().tearDown()

def test_TestLookupModuleWithPasslib_test_encrypt():
    ret = TestLookupModuleWithPasslib().test_encrypt()

def test_TestLookupModuleWithPasslib_test_password_already_created_encrypt():
    ret = TestLookupModuleWithPasslib().test_password_already_created_encrypt()