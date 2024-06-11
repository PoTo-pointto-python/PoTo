from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    name: test\n    plugin_type: inventory\n    short_description: test inventory source\n    extends_documentation_fragment:\n        - inventory_cache\n'
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable

class InventoryModule(BaseInventoryPlugin, Cacheable):
    NAME = 'test'

    def populate(self, hosts):
        for host in list(hosts.keys()):
            self.inventory.add_host(host, group='all')
            for (hostvar, hostval) in hosts[host].items():
                self.inventory.set_variable(host, hostvar, hostval)

    def get_hosts(self):
        return {'host1': {'one': 'two'}, 'host2': {'three': 'four'}}

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self.load_cache_plugin()
        cache_key = self.get_cache_key(path)
        cache_setting = self.get_option('cache')
        attempt_to_read_cache = cache_setting and cache
        cache_needs_update = cache_setting and (not cache)
        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        if cache_needs_update:
            results = self.get_hosts()
            self._cache[cache_key] = results
        self.populate(results)

def test_InventoryModule_populate():
    ret = InventoryModule().populate()

def test_InventoryModule_get_hosts():
    ret = InventoryModule().get_hosts()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()