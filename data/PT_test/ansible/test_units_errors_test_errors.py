from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.builtins import BUILTINS
from units.compat.mock import mock_open, patch
from ansible.errors import AnsibleError
from ansible.parsing.yaml.objects import AnsibleBaseYAMLObject

class TestErrors(unittest.TestCase):

    def setUp(self):
        self.message = 'This is the error message'
        self.unicode_message = 'This is an error with ð\x9f\x98¨ in it'
        self.obj = AnsibleBaseYAMLObject()

    def test_basic_error(self):
        e = AnsibleError(self.message)
        self.assertEqual(e.message, self.message)
        self.assertEqual(e.__repr__(), self.message)

    def test_basic_unicode_error(self):
        e = AnsibleError(self.unicode_message)
        self.assertEqual(e.message, self.unicode_message)
        self.assertEqual(e.__repr__(), self.unicode_message)

    @patch.object(AnsibleError, '_get_error_lines_from_file')
    def test_error_with_kv(self, mock_method):
        """ This tests a task with both YAML and k=v syntax

        - lineinfile: line=foo path=bar
            line: foo

        An accurate error message and position indicator are expected.

        _get_error_lines_from_file() returns (target_line, prev_line)
        """
        self.obj.ansible_pos = ('foo.yml', 2, 1)
        mock_method.return_value = ['    line: foo\n', '- lineinfile: line=foo path=bar\n']
        e = AnsibleError(self.message, self.obj)
        self.assertEqual(e.message, "This is the error message\n\nThe error appears to be in 'foo.yml': line 1, column 19, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n- lineinfile: line=foo path=bar\n                  ^ here\n\nThere appears to be both 'k=v' shorthand syntax and YAML in this task. Only one syntax may be used.\n")

    @patch.object(AnsibleError, '_get_error_lines_from_file')
    def test_error_with_object(self, mock_method):
        self.obj.ansible_pos = ('foo.yml', 1, 1)
        mock_method.return_value = ('this is line 1\n', '')
        e = AnsibleError(self.message, self.obj)
        self.assertEqual(e.message, "This is the error message\n\nThe error appears to be in 'foo.yml': line 1, column 1, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\nthis is line 1\n^ here\n")

    def test_get_error_lines_from_file(self):
        m = mock_open()
        m.return_value.readlines.return_value = ['this is line 1\n']
        with patch('{0}.open'.format(BUILTINS), m):
            self.obj.ansible_pos = ('foo.yml', 1, 1)
            e = AnsibleError(self.message, self.obj)
            self.assertEqual(e.message, "This is the error message\n\nThe error appears to be in 'foo.yml': line 1, column 1, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\nthis is line 1\n^ here\n")
            self.obj.ansible_pos = ('foo.yml', 2, 1)
            e = AnsibleError(self.message, self.obj)
            self.assertEqual(e.message, "This is the error message\n\nThe error appears to be in 'foo.yml': line 2, column 1, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\n(specified line no longer in file, maybe it changed?)")
        m = mock_open()
        m.return_value.readlines.return_value = ['this line has unicode ð\x9f\x98¨ in it!\n']
        with patch('{0}.open'.format(BUILTINS), m):
            self.obj.ansible_pos = ('foo.yml', 1, 1)
            e = AnsibleError(self.unicode_message, self.obj)
            self.assertEqual(e.message, "This is an error with ð\x9f\x98¨ in it\n\nThe error appears to be in 'foo.yml': line 1, column 1, but may\nbe elsewhere in the file depending on the exact syntax problem.\n\nThe offending line appears to be:\n\n\nthis line has unicode ð\x9f\x98¨ in it!\n^ here\n")

def test_TestErrors_setUp():
    ret = TestErrors().setUp()

def test_TestErrors_test_basic_error():
    ret = TestErrors().test_basic_error()

def test_TestErrors_test_basic_unicode_error():
    ret = TestErrors().test_basic_unicode_error()

def test_TestErrors_test_error_with_kv():
    ret = TestErrors().test_error_with_kv()

def test_TestErrors_test_error_with_object():
    ret = TestErrors().test_error_with_object()

def test_TestErrors_test_get_error_lines_from_file():
    ret = TestErrors().test_get_error_lines_from_file()