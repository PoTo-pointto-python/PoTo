from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_mariadbconfiguration_info\nversion_added: "2.9"\nshort_description: Get Azure MariaDB Configuration facts\ndescription:\n    - Get facts of Azure MariaDB Configuration.\n\noptions:\n    resource_group:\n        description:\n            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.\n        required: True\n        type: str\n    server_name:\n        description:\n            - The name of the server.\n        required: True\n        type: str\n    name:\n        description:\n            - Setting name.\n        type: str\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n    - Matti Ranta (@techknowlogick)\n\n'
EXAMPLES = '\n  - name: Get specific setting of MariaDB Server\n    azure_rm_mariadbconfiguration_info:\n      resource_group: myResourceGroup\n      server_name: testserver\n      name: deadlock_timeout\n\n  - name: Get all settings of MariaDB Server\n    azure_rm_mariadbconfiguration_info:\n      resource_group: myResourceGroup\n      server_name: server_name\n'
RETURN = '\nsettings:\n    description:\n        - A list of dictionaries containing MariaDB Server settings.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Setting resource ID.\n            returned: always\n            type: str\n            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DBforMariaDB/servers/testserver\n                     /configurations/deadlock_timeout"\n        name:\n            description:\n                - Setting name.\n            returned: always\n            type: str\n            sample: deadlock_timeout\n        value:\n            description:\n                - Setting value.\n            returned: always\n            type: raw\n            sample: 1000\n        description:\n            description:\n                - Description of the configuration.\n            returned: always\n            type: str\n            sample: Deadlock timeout.\n        source:\n            description:\n                - Source of the configuration.\n            returned: always\n            type: str\n            sample: system-default\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.azure_operation import AzureOperationPoller
    from azure.mgmt.rdbms.mariadb import MariaDBManagementClient
    from msrest.serialization import Model
except ImportError:
    pass

class AzureRMMariaDbConfigurationInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True), server_name=dict(type='str', required=True), name=dict(type='str'))
        self.results = dict(changed=False)
        self.mgmt_client = None
        self.resource_group = None
        self.server_name = None
        self.name = None
        super(AzureRMMariaDbConfigurationInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_mariadbconfiguration_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_mariadbconfiguration_facts' module has been renamed to 'azure_rm_mariadbconfiguration_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(MariaDBManagementClient, base_url=self._cloud_environment.endpoints.resource_manager)
        if self.name is not None:
            self.results['settings'] = self.get()
        else:
            self.results['settings'] = self.list_by_server()
        return self.results

    def get(self):
        """
        Gets facts of the specified MariaDB Configuration.

        :return: deserialized MariaDB Configurationinstance state dictionary
        """
        response = None
        results = []
        try:
            response = self.mgmt_client.configurations.get(resource_group_name=self.resource_group, server_name=self.server_name, configuration_name=self.name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for Configurations.')
        if response is not None:
            results.append(self.format_item(response))
        return results

    def list_by_server(self):
        """
        Gets facts of the specified MariaDB Configuration.

        :return: deserialized MariaDB Configurationinstance state dictionary
        """
        response = None
        results = []
        try:
            response = self.mgmt_client.configurations.list_by_server(resource_group_name=self.resource_group, server_name=self.server_name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for Configurations.')
        if response is not None:
            for item in response:
                results.append(self.format_item(item))
        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {'resource_group': self.resource_group, 'server_name': self.server_name, 'id': d['id'], 'name': d['name'], 'value': d['value'], 'description': d['description'], 'source': d['source']}
        return d

def main():
    AzureRMMariaDbConfigurationInfo()
if __name__ == '__main__':
    main()

def test_AzureRMMariaDbConfigurationInfo_exec_module():
    ret = AzureRMMariaDbConfigurationInfo().exec_module()

def test_AzureRMMariaDbConfigurationInfo_get():
    ret = AzureRMMariaDbConfigurationInfo().get()

def test_AzureRMMariaDbConfigurationInfo_list_by_server():
    ret = AzureRMMariaDbConfigurationInfo().list_by_server()

def test_AzureRMMariaDbConfigurationInfo_format_item():
    ret = AzureRMMariaDbConfigurationInfo().format_item()