from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils import distro
from ansible.module_utils.six import string_types

class TestDistro:

    def test_info(self):
        info = distro.info()
        assert isinstance(info, dict), 'distro.info() returned %s (%s) which is not a dist' % (info, type(info))

    def test_linux_distribution(self):
        linux_dist = distro.linux_distribution()
        assert isinstance(linux_dist, tuple), 'linux_distrution() returned %s (%s) which is not a tuple' % (linux_dist, type(linux_dist))

    def test_id(self):
        id = distro.id()
        assert isinstance(id, string_types), 'distro.id() returned %s (%s) which is not a string' % (id, type(id))

def test_TestDistro_test_info():
    ret = TestDistro().test_info()

def test_TestDistro_test_linux_distribution():
    ret = TestDistro().test_linux_distribution()

def test_TestDistro_test_id():
    ret = TestDistro().test_id()