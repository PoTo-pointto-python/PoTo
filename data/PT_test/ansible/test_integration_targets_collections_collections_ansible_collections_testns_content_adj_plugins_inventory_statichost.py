from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    inventory: statichost\n    short_description: Add a single host\n    description: Add a single host\n    extends_documentation_fragment:\n      - inventory_cache\n    options:\n      plugin:\n        description: plugin name (must be statichost)\n        required: true\n      hostname:\n        description: Toggle display of stderr even when script was successful\n        required: True\n'
from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable

class InventoryModule(BaseInventoryPlugin, Cacheable):
    NAME = 'testns.content_adj.statichost'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self._hosts = set()

    def verify_file(self, path):
        """ Verify if file is usable by this plugin, base does minimal accessibility check """
        if not path.endswith('.statichost.yml') and (not path.endswith('.statichost.yaml')):
            return False
        return super(InventoryModule, self).verify_file(path)

    def parse(self, inventory, loader, path, cache=None):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        cache_key = self.get_cache_key(path)
        attempt_to_read_cache = self.get_option('cache') and cache
        cache_needs_update = self.get_option('cache') and (not cache)
        if attempt_to_read_cache:
            try:
                host_to_add = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        if not attempt_to_read_cache or cache_needs_update:
            host_to_add = self.get_option('hostname')
        self.inventory.add_host(host_to_add, 'all')
        self._cache[cache_key] = host_to_add

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()