from __future__ import absolute_import, division, print_function
__metaclass__ = type
from os.path import isdir, isfile, isabs, exists, lexists, islink, samefile, ismount
from ansible import errors

class TestModule(object):
    """ Ansible file jinja2 tests """

    def tests(self):
        return {'is_dir': isdir, 'directory': isdir, 'is_file': isfile, 'file': isfile, 'is_link': islink, 'link': islink, 'exists': exists, 'link_exists': lexists, 'is_abs': isabs, 'abs': isabs, 'is_same_file': samefile, 'same_file': samefile, 'is_mount': ismount, 'mount': ismount}

def test_TestModule_tests():
    ret = TestModule().tests()