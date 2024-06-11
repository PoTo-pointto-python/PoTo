from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.mock.procenv import ModuleTestCase
from ansible.module_utils.six.moves import builtins
realimport = builtins.__import__

class TestTextifyContainers(ModuleTestCase):

    def test_module_utils_basic_json_dict_converters(self):
        from ansible.module_utils.basic import json_dict_unicode_to_bytes, json_dict_bytes_to_unicode
        test_data = dict(item1=u'Fóo', item2=[u'Bár', u'Bam'], item3=dict(sub1=u'Súb'), item4=(u'föo', u'bär', u'©'), item5=42)
        res = json_dict_unicode_to_bytes(test_data)
        res2 = json_dict_bytes_to_unicode(res)
        self.assertEqual(test_data, res2)

def test_TestTextifyContainers_test_module_utils_basic_json_dict_converters():
    ret = TestTextifyContainers().test_module_utils_basic_json_dict_converters()