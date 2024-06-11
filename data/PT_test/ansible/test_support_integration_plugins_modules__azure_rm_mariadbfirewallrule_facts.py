from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_mariadbfirewallrule_info\nversion_added: "2.9"\nshort_description: Get Azure MariaDB Firewall Rule facts\ndescription:\n    - Get facts of Azure MariaDB Firewall Rule.\n\noptions:\n    resource_group:\n        description:\n            - The name of the resource group.\n        required: True\n        type: str\n    server_name:\n        description:\n            - The name of the server.\n        required: True\n        type: str\n    name:\n        description:\n            - The name of the server firewall rule.\n        type: str\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n    - Matti Ranta (@techknowlogick)\n\n'
EXAMPLES = '\n  - name: Get instance of MariaDB Firewall Rule\n    azure_rm_mariadbfirewallrule_info:\n      resource_group: myResourceGroup\n      server_name: server_name\n      name: firewall_rule_name\n\n  - name: List instances of MariaDB Firewall Rule\n    azure_rm_mariadbfirewallrule_info:\n      resource_group: myResourceGroup\n      server_name: server_name\n'
RETURN = '\nrules:\n    description:\n        - A list of dictionaries containing facts for MariaDB Firewall Rule.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Resource ID.\n            returned: always\n            type: str\n            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/TestGroup/providers/Microsoft.DBforMariaDB/servers/testserver/fire\n                    wallRules/rule1"\n        server_name:\n            description:\n                - The name of the server.\n            returned: always\n            type: str\n            sample: testserver\n        name:\n            description:\n                - Resource name.\n            returned: always\n            type: str\n            sample: rule1\n        start_ip_address:\n            description:\n                - The start IP address of the MariaDB firewall rule.\n            returned: always\n            type: str\n            sample: 10.0.0.16\n        end_ip_address:\n            description:\n                - The end IP address of the MariaDB firewall rule.\n            returned: always\n            type: str\n            sample: 10.0.0.18\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.azure_operation import AzureOperationPoller
    from azure.mgmt.rdbms.mariadb import MariaDBManagementClient
    from msrest.serialization import Model
except ImportError:
    pass

class AzureRMMariaDbFirewallRuleInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True), server_name=dict(type='str', required=True), name=dict(type='str'))
        self.results = dict(changed=False)
        self.mgmt_client = None
        self.resource_group = None
        self.server_name = None
        self.name = None
        super(AzureRMMariaDbFirewallRuleInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_mariadbfirewallrule_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_mariadbfirewallrule_facts' module has been renamed to 'azure_rm_mariadbfirewallrule_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(MariaDBManagementClient, base_url=self._cloud_environment.endpoints.resource_manager)
        if self.name is not None:
            self.results['rules'] = self.get()
        else:
            self.results['rules'] = self.list_by_server()
        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.firewall_rules.get(resource_group_name=self.resource_group, server_name=self.server_name, firewall_rule_name=self.name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for FirewallRules.')
        if response is not None:
            results.append(self.format_item(response))
        return results

    def list_by_server(self):
        response = None
        results = []
        try:
            response = self.mgmt_client.firewall_rules.list_by_server(resource_group_name=self.resource_group, server_name=self.server_name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for FirewallRules.')
        if response is not None:
            for item in response:
                results.append(self.format_item(item))
        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {'resource_group': self.resource_group, 'id': d['id'], 'server_name': self.server_name, 'name': d['name'], 'start_ip_address': d['start_ip_address'], 'end_ip_address': d['end_ip_address']}
        return d

def main():
    AzureRMMariaDbFirewallRuleInfo()
if __name__ == '__main__':
    main()

def test_AzureRMMariaDbFirewallRuleInfo_exec_module():
    ret = AzureRMMariaDbFirewallRuleInfo().exec_module()

def test_AzureRMMariaDbFirewallRuleInfo_get():
    ret = AzureRMMariaDbFirewallRuleInfo().get()

def test_AzureRMMariaDbFirewallRuleInfo_list_by_server():
    ret = AzureRMMariaDbFirewallRuleInfo().list_by_server()

def test_AzureRMMariaDbFirewallRuleInfo_format_item():
    ret = AzureRMMariaDbFirewallRuleInfo().format_item()