from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    inventory: statichost\n    short_description: Add a single host\n    description: Add a single host\n    extends_documentation_fragment:\n      - inventory_cache\n    options:\n      plugin:\n        description: plugin name (must be statichost)\n        required: true\n      hostname:\n        description: Toggle display of stderr even when script was successful\n        required: True\n'
from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable

class InventoryModule(BaseInventoryPlugin, Cacheable):
    NAME = 'testns.content_adj.statichost'

    def verify_file(self, path):
        pass

    def parse(self, inventory, loader, path, cache=None):
        pass

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()