from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.config.data import ConfigData
from ansible.config.manager import Setting
mykey = Setting('mykey', 'myvalue', 'test', 'string')
mykey2 = Setting('mykey2', 'myvalue2', ['test', 'test2'], 'list')
mykey3 = Setting('mykey3', 'myvalue3', 11111111111, 'integer')

class TestConfigData(unittest.TestCase):

    def setUp(self):
        self.cdata = ConfigData()

    def tearDown(self):
        self.cdata = None

    def test_update_setting(self):
        for setting in [mykey, mykey2, mykey3]:
            self.cdata.update_setting(setting)
            self.assertEqual(setting, self.cdata._global_settings.get(setting.name))

    def test_update_setting_with_plugin(self):
        pass

    def test_get_setting(self):
        self.cdata._global_settings = {'mykey': mykey}
        self.assertEqual(mykey, self.cdata.get_setting('mykey'))

    def test_get_settings(self):
        all_settings = {'mykey': mykey, 'mykey2': mykey2}
        self.cdata._global_settings = all_settings
        for setting in self.cdata.get_settings():
            self.assertEqual(all_settings[setting.name], setting)

def test_TestConfigData_setUp():
    ret = TestConfigData().setUp()

def test_TestConfigData_tearDown():
    ret = TestConfigData().tearDown()

def test_TestConfigData_test_update_setting():
    ret = TestConfigData().test_update_setting()

def test_TestConfigData_test_update_setting_with_plugin():
    ret = TestConfigData().test_update_setting_with_plugin()

def test_TestConfigData_test_get_setting():
    ret = TestConfigData().test_get_setting()

def test_TestConfigData_test_get_settings():
    ret = TestConfigData().test_get_settings()