from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.plugins.cache import BaseCacheModule
DOCUMENTATION = '\n    cache: none\n    short_description: write-only cache (no cache)\n    description:\n        - No caching at all\n    version_added: historical\n    author: core team (@ansible-core)\n'

class CacheModule(BaseCacheModule):

    def __init__(self, *args, **kwargs):
        self.empty = {}

    def get(self, key):
        return self.empty.get(key)

    def set(self, key, value):
        return value

    def keys(self):
        return self.empty.keys()

    def contains(self, key):
        return key in self.empty

    def delete(self, key):
        del self.emtpy[key]

    def flush(self):
        self.empty = {}

    def copy(self):
        return self.empty.copy()

    def __getstate__(self):
        return self.copy()

    def __setstate__(self, data):
        self.empty = data

def test_CacheModule_get():
    ret = CacheModule().get()

def test_CacheModule_set():
    ret = CacheModule().set()

def test_CacheModule_keys():
    ret = CacheModule().keys()

def test_CacheModule_contains():
    ret = CacheModule().contains()

def test_CacheModule_delete():
    ret = CacheModule().delete()

def test_CacheModule_flush():
    ret = CacheModule().flush()

def test_CacheModule_copy():
    ret = CacheModule().copy()

def test_CacheModule___getstate__():
    ret = CacheModule().__getstate__()

def test_CacheModule___setstate__():
    ret = CacheModule().__setstate__()