from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    name: test_inventory\n    plugin_type: inventory\n    authors:\n      - Pierre-Louis Bonicoli (@pilou-)\n    short_description: test inventory\n    description:\n        - test inventory (fetch parameters using config API)\n    options:\n        departments:\n            description: test parameter\n            type: list\n            default:\n                - seine-et-marne\n                - haute-garonne\n            required: False\n'
EXAMPLES = '\n# Example command line: ansible-inventory --list -i test_inventory.yml\n\nplugin: test_inventory\ndepartments:\n  - paris\n'
from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):
    NAME = 'test_inventory'

    def verify_file(self, path):
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path=path)
        departments = self.get_option('departments')
        group = 'test_group'
        host = 'test_host'
        self.inventory.add_group(group)
        self.inventory.add_host(group=group, host=host)
        self.inventory.set_variable(host, 'departments', departments)

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()