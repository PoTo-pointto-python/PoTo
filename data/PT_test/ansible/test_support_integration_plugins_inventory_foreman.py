from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    name: foreman\n    plugin_type: inventory\n    short_description: foreman inventory source\n    version_added: "2.6"\n    requirements:\n        - requests >= 1.1\n    description:\n        - Get inventory hosts from the foreman service.\n        - "Uses a configuration file as an inventory source, it must end in ``.foreman.yml`` or ``.foreman.yaml`` and has a ``plugin: foreman`` entry."\n    extends_documentation_fragment:\n        - inventory_cache\n        - constructed\n    options:\n      plugin:\n        description: the name of this plugin, it should always be set to \'foreman\' for this plugin to recognize it as it\'s own.\n        required: True\n        choices: [\'foreman\']\n      url:\n        description: url to foreman\n        default: \'http://localhost:3000\'\n        env:\n            - name: FOREMAN_SERVER\n              version_added: "2.8"\n      user:\n        description: foreman authentication user\n        required: True\n        env:\n            - name: FOREMAN_USER\n              version_added: "2.8"\n      password:\n        description: foreman authentication password\n        required: True\n        env:\n            - name: FOREMAN_PASSWORD\n              version_added: "2.8"\n      validate_certs:\n        description: verify SSL certificate if using https\n        type: boolean\n        default: False\n      group_prefix:\n        description: prefix to apply to foreman groups\n        default: foreman_\n      vars_prefix:\n        description: prefix to apply to host variables, does not include facts nor params\n        default: foreman_\n      want_facts:\n        description: Toggle, if True the plugin will retrieve host facts from the server\n        type: boolean\n        default: False\n      want_params:\n        description: Toggle, if true the inventory will retrieve \'all_parameters\' information as host vars\n        type: boolean\n        default: False\n      want_hostcollections:\n        description: Toggle, if true the plugin will create Ansible groups for host collections\n        type: boolean\n        default: False\n        version_added: \'2.10\'\n      want_ansible_ssh_host:\n        description: Toggle, if true the plugin will populate the ansible_ssh_host variable to explicitly specify the connection target\n        type: boolean\n        default: False\n        version_added: \'2.10\'\n\n'
EXAMPLES = '\n# my.foreman.yml\nplugin: foreman\nurl: http://localhost:2222\nuser: ansible-tester\npassword: secure\nvalidate_certs: False\n'
from distutils.version import LooseVersion
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name, Constructable
try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion('1.1.0'):
        raise ImportError
except ImportError:
    raise AnsibleError('This script requires python-requests 1.1 as a minimum version')
from requests.auth import HTTPBasicAuth

class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):
    """ Host inventory parser for ansible using foreman as source. """
    NAME = 'foreman'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.foreman_url = None
        self.session = None
        self.cache_key = None
        self.use_cache = None

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('foreman.yaml', 'foreman.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "foreman.yaml" nor "foreman.yml"')
        return valid

    def _get_session(self):
        if not self.session:
            self.session = requests.session()
            self.session.auth = HTTPBasicAuth(self.get_option('user'), to_bytes(self.get_option('password')))
            self.session.verify = self.get_option('validate_certs')
        return self.session

    def _get_json(self, url, ignore_errors=None):
        if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
            if self.cache_key not in self._cache:
                self._cache[self.cache_key] = {url: ''}
            results = []
            s = self._get_session()
            params = {'page': 1, 'per_page': 250}
            while True:
                ret = s.get(url, params=params)
                if ignore_errors and ret.status_code in ignore_errors:
                    break
                ret.raise_for_status()
                json = ret.json()
                if 'results' not in json:
                    results = json
                    break
                elif isinstance(json['results'], MutableMapping):
                    results = json['results']
                    break
                else:
                    results = results + json['results']
                    if len(results) >= json['subtotal']:
                        break
                    if len(json['results']) == 0:
                        self.display.warning('Did not make any progress during loop. expected %d got %d' % (json['subtotal'], len(results)))
                        break
                    params['page'] += 1
            self._cache[self.cache_key][url] = results
        return self._cache[self.cache_key][url]

    def _get_hosts(self):
        return self._get_json('%s/api/v2/hosts' % self.foreman_url)

    def _get_all_params_by_id(self, hid):
        url = '%s/api/v2/hosts/%s' % (self.foreman_url, hid)
        ret = self._get_json(url, [404])
        if not ret or not isinstance(ret, MutableMapping) or (not ret.get('all_parameters', False)):
            return {}
        return ret.get('all_parameters')

    def _get_facts_by_id(self, hid):
        url = '%s/api/v2/hosts/%s/facts' % (self.foreman_url, hid)
        return self._get_json(url)

    def _get_host_data_by_id(self, hid):
        url = '%s/api/v2/hosts/%s' % (self.foreman_url, hid)
        return self._get_json(url)

    def _get_facts(self, host):
        """Fetch all host facts of the host"""
        ret = self._get_facts_by_id(host['id'])
        if len(ret.values()) == 0:
            facts = {}
        elif len(ret.values()) == 1:
            facts = list(ret.values())[0]
        else:
            raise ValueError("More than one set of facts returned for '%s'" % host)
        return facts

    def _populate(self):
        for host in self._get_hosts():
            if host.get('name'):
                host_name = self.inventory.add_host(host['name'])
                group_name = host.get('hostgroup_title', host.get('hostgroup_name'))
                if group_name:
                    group_name = to_safe_group_name('%s%s' % (self.get_option('group_prefix'), group_name.lower().replace(' ', '')))
                    group_name = self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, host_name)
                try:
                    for (k, v) in host.items():
                        if k not in ('name', 'hostgroup_title', 'hostgroup_name'):
                            try:
                                self.inventory.set_variable(host_name, self.get_option('vars_prefix') + k, v)
                            except ValueError as e:
                                self.display.warning('Could not set host info hostvar for %s, skipping %s: %s' % (host, k, to_text(e)))
                except ValueError as e:
                    self.display.warning('Could not get host info for %s, skipping: %s' % (host_name, to_text(e)))
                if self.get_option('want_params'):
                    for p in self._get_all_params_by_id(host['id']):
                        try:
                            self.inventory.set_variable(host_name, p['name'], p['value'])
                        except ValueError as e:
                            self.display.warning("Could not set hostvar %s to '%s' for the '%s' host, skipping:  %s" % (p['name'], to_native(p['value']), host, to_native(e)))
                if self.get_option('want_facts'):
                    self.inventory.set_variable(host_name, 'foreman_facts', self._get_facts(host))
                if self.get_option('want_hostcollections'):
                    host_data = self._get_host_data_by_id(host['id'])
                    hostcollections = host_data.get('host_collections')
                    if hostcollections:
                        for hostcollection in hostcollections:
                            try:
                                hostcollection_group = to_safe_group_name('%shostcollection_%s' % (self.get_option('group_prefix'), hostcollection['name'].lower().replace(' ', '')))
                                hostcollection_group = self.inventory.add_group(hostcollection_group)
                                self.inventory.add_child(hostcollection_group, host_name)
                            except ValueError as e:
                                self.display.warning('Could not create groups for host collections for %s, skipping: %s' % (host_name, to_text(e)))
                if self.get_option('want_ansible_ssh_host'):
                    for key in ('ip', 'ipv4', 'ipv6'):
                        if host.get(key):
                            try:
                                self.inventory.set_variable(host_name, 'ansible_ssh_host', host[key])
                                break
                            except ValueError as e:
                                self.display.warning("Could not set hostvar ansible_ssh_host to '%s' for the '%s' host, skipping: %s" % (host[key], host_name, to_text(e)))
                strict = self.get_option('strict')
                hostvars = self.inventory.get_host(host_name).get_vars()
                self._set_composite_vars(self.get_option('compose'), hostvars, host_name, strict)
                self._add_host_to_composed_groups(self.get_option('groups'), hostvars, host_name, strict)
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'), hostvars, host_name, strict)

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        self.foreman_url = self.get_option('url')
        self.cache_key = self.get_cache_key(path)
        self.use_cache = cache and self.get_option('cache')
        self._populate()

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule__get_session():
    ret = InventoryModule()._get_session()

def test_InventoryModule__get_json():
    ret = InventoryModule()._get_json()

def test_InventoryModule__get_hosts():
    ret = InventoryModule()._get_hosts()

def test_InventoryModule__get_all_params_by_id():
    ret = InventoryModule()._get_all_params_by_id()

def test_InventoryModule__get_facts_by_id():
    ret = InventoryModule()._get_facts_by_id()

def test_InventoryModule__get_host_data_by_id():
    ret = InventoryModule()._get_host_data_by_id()

def test_InventoryModule__get_facts():
    ret = InventoryModule()._get_facts()

def test_InventoryModule__populate():
    ret = InventoryModule()._populate()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()