from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest, mock
from ansible.errors import AnsibleError
from ansible.plugins.cache import FactCache, CachePluginAdjudicator
from ansible.plugins.cache.base import BaseCacheModule
from ansible.plugins.cache.memory import CacheModule as MemoryCache
from ansible.plugins.loader import cache_loader
import pytest

class TestCachePluginAdjudicator:
    cache = CachePluginAdjudicator()
    cache['cache_key'] = {'key1': 'value1', 'key2': 'value2'}
    cache['cache_key_2'] = {'key': 'value'}

    def test___setitem__(self):
        self.cache['new_cache_key'] = {'new_key1': ['new_value1', 'new_value2']}
        assert self.cache['new_cache_key'] == {'new_key1': ['new_value1', 'new_value2']}

    def test_inner___setitem__(self):
        self.cache['new_cache_key'] = {'new_key1': ['new_value1', 'new_value2']}
        self.cache['new_cache_key']['new_key1'][0] = 'updated_value1'
        assert self.cache['new_cache_key'] == {'new_key1': ['updated_value1', 'new_value2']}

    def test___contains__(self):
        assert 'cache_key' in self.cache
        assert 'not_cache_key' not in self.cache

    def test_get(self):
        assert self.cache.get('cache_key') == {'key1': 'value1', 'key2': 'value2'}

    def test_get_with_default(self):
        assert self.cache.get('foo', 'bar') == 'bar'

    def test_get_without_default(self):
        assert self.cache.get('foo') is None

    def test___getitem__(self):
        with pytest.raises(KeyError) as err:
            self.cache['foo']

    def test_pop_with_default(self):
        assert self.cache.pop('foo', 'bar') == 'bar'

    def test_pop_without_default(self):
        with pytest.raises(KeyError) as err:
            assert self.cache.pop('foo')

    def test_pop(self):
        v = self.cache.pop('cache_key_2')
        assert v == {'key': 'value'}
        assert 'cache_key_2' not in self.cache

    def test_update(self):
        self.cache.update({'cache_key': {'key2': 'updatedvalue'}})
        assert self.cache['cache_key']['key2'] == 'updatedvalue'

class TestFactCache(unittest.TestCase):

    def setUp(self):
        with mock.patch('ansible.constants.CACHE_PLUGIN', 'memory'):
            self.cache = FactCache()

    def test_copy(self):
        self.cache['avocado'] = 'fruit'
        self.cache['daisy'] = 'flower'
        a_copy = self.cache.copy()
        self.assertEqual(type(a_copy), dict)
        self.assertEqual(a_copy, dict(avocado='fruit', daisy='flower'))

    def test_plugin_load_failure(self):
        with mock.patch('ansible.constants.CACHE_PLUGIN', 'json'):
            self.assertRaisesRegexp(AnsibleError, 'Unable to load the facts cache plugin.*json.*', FactCache)

    def test_update(self):
        self.cache.update({'cache_key': {'key2': 'updatedvalue'}})
        assert self.cache['cache_key']['key2'] == 'updatedvalue'

    def test_update_legacy(self):
        self.cache.update('cache_key', {'key2': 'updatedvalue'})
        assert self.cache['cache_key']['key2'] == 'updatedvalue'

    def test_update_legacy_key_exists(self):
        self.cache['cache_key'] = {'key': 'value', 'key2': 'value2'}
        self.cache.update('cache_key', {'key': 'updatedvalue'})
        assert self.cache['cache_key']['key'] == 'updatedvalue'
        assert self.cache['cache_key']['key2'] == 'value2'

class TestAbstractClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_subclass_error(self):

        class CacheModule1(BaseCacheModule):
            pass
        with self.assertRaises(TypeError):
            CacheModule1()

        class CacheModule2(BaseCacheModule):

            def get(self, key):
                super(CacheModule2, self).get(key)
        with self.assertRaises(TypeError):
            CacheModule2()

    def test_subclass_success(self):

        class CacheModule3(BaseCacheModule):

            def get(self, key):
                super(CacheModule3, self).get(key)

            def set(self, key, value):
                super(CacheModule3, self).set(key, value)

            def keys(self):
                super(CacheModule3, self).keys()

            def contains(self, key):
                super(CacheModule3, self).contains(key)

            def delete(self, key):
                super(CacheModule3, self).delete(key)

            def flush(self):
                super(CacheModule3, self).flush()

            def copy(self):
                super(CacheModule3, self).copy()
        self.assertIsInstance(CacheModule3(), CacheModule3)

    def test_memory_cachemodule(self):
        self.assertIsInstance(MemoryCache(), MemoryCache)

    def test_memory_cachemodule_with_loader(self):
        self.assertIsInstance(cache_loader.get('memory'), MemoryCache)

def test_TestCachePluginAdjudicator_test___setitem__():
    ret = TestCachePluginAdjudicator().test___setitem__()

def test_TestCachePluginAdjudicator_test_inner___setitem__():
    ret = TestCachePluginAdjudicator().test_inner___setitem__()

def test_TestCachePluginAdjudicator_test___contains__():
    ret = TestCachePluginAdjudicator().test___contains__()

def test_TestCachePluginAdjudicator_test_get():
    ret = TestCachePluginAdjudicator().test_get()

def test_TestCachePluginAdjudicator_test_get_with_default():
    ret = TestCachePluginAdjudicator().test_get_with_default()

def test_TestCachePluginAdjudicator_test_get_without_default():
    ret = TestCachePluginAdjudicator().test_get_without_default()

def test_TestCachePluginAdjudicator_test___getitem__():
    ret = TestCachePluginAdjudicator().test___getitem__()

def test_TestCachePluginAdjudicator_test_pop_with_default():
    ret = TestCachePluginAdjudicator().test_pop_with_default()

def test_TestCachePluginAdjudicator_test_pop_without_default():
    ret = TestCachePluginAdjudicator().test_pop_without_default()

def test_TestCachePluginAdjudicator_test_pop():
    ret = TestCachePluginAdjudicator().test_pop()

def test_TestCachePluginAdjudicator_test_update():
    ret = TestCachePluginAdjudicator().test_update()

def test_TestFactCache_setUp():
    ret = TestFactCache().setUp()

def test_TestFactCache_test_copy():
    ret = TestFactCache().test_copy()

def test_TestFactCache_test_plugin_load_failure():
    ret = TestFactCache().test_plugin_load_failure()

def test_TestFactCache_test_update():
    ret = TestFactCache().test_update()

def test_TestFactCache_test_update_legacy():
    ret = TestFactCache().test_update_legacy()

def test_TestFactCache_test_update_legacy_key_exists():
    ret = TestFactCache().test_update_legacy_key_exists()

def test_TestAbstractClass_setUp():
    ret = TestAbstractClass().setUp()

def test_TestAbstractClass_tearDown():
    ret = TestAbstractClass().tearDown()

def test_TestAbstractClass_test_subclass_error():
    ret = TestAbstractClass().test_subclass_error()

def test_TestAbstractClass_test_subclass_success():
    ret = TestAbstractClass().test_subclass_success()

def test_TestAbstractClass_test_memory_cachemodule():
    ret = TestAbstractClass().test_memory_cachemodule()

def test_TestAbstractClass_test_memory_cachemodule_with_loader():
    ret = TestAbstractClass().test_memory_cachemodule_with_loader()

def test_CacheModule2_get():
    ret = CacheModule2().get()

def test_CacheModule3_get():
    ret = CacheModule3().get()

def test_CacheModule3_set():
    ret = CacheModule3().set()

def test_CacheModule3_keys():
    ret = CacheModule3().keys()

def test_CacheModule3_contains():
    ret = CacheModule3().contains()

def test_CacheModule3_delete():
    ret = CacheModule3().delete()

def test_CacheModule3_flush():
    ret = CacheModule3().flush()

def test_CacheModule3_copy():
    ret = CacheModule3().copy()