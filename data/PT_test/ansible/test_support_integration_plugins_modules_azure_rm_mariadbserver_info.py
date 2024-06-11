from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_mariadbserver_info\nversion_added: "2.9"\nshort_description: Get Azure MariaDB Server facts\ndescription:\n    - Get facts of MariaDB Server.\n\noptions:\n    resource_group:\n        description:\n            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.\n        required: True\n        type: str\n    name:\n        description:\n            - The name of the server.\n        type: str\n    tags:\n        description:\n            - Limit results by providing a list of tags. Format tags as \'key\' or \'key:value\'.\n        type: list\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n    - Matti Ranta (@techknowlogick)\n\n'
EXAMPLES = '\n  - name: Get instance of MariaDB Server\n    azure_rm_mariadbserver_info:\n      resource_group: myResourceGroup\n      name: server_name\n\n  - name: List instances of MariaDB Server\n    azure_rm_mariadbserver_info:\n      resource_group: myResourceGroup\n'
RETURN = '\nservers:\n    description:\n        - A list of dictionaries containing facts for MariaDB servers.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Resource ID.\n            returned: always\n            type: str\n            sample: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DBforMariaDB/servers/myabdud1223\n        resource_group:\n            description:\n                - Resource group name.\n            returned: always\n            type: str\n            sample: myResourceGroup\n        name:\n            description:\n                - Resource name.\n            returned: always\n            type: str\n            sample: myabdud1223\n        location:\n            description:\n                - The location the resource resides in.\n            returned: always\n            type: str\n            sample: eastus\n        sku:\n            description:\n                - The SKU of the server.\n            returned: always\n            type: complex\n            contains:\n                name:\n                    description:\n                        - The name of the SKU.\n                    returned: always\n                    type: str\n                    sample: GP_Gen4_2\n                tier:\n                    description:\n                        - The tier of the particular SKU.\n                    returned: always\n                    type: str\n                    sample: GeneralPurpose\n                capacity:\n                    description:\n                        - The scale capacity.\n                    returned: always\n                    type: int\n                    sample: 2\n        storage_mb:\n            description:\n                - The maximum storage allowed for a server.\n            returned: always\n            type: int\n            sample: 128000\n        enforce_ssl:\n            description:\n                - Enable SSL enforcement.\n            returned: always\n            type: bool\n            sample: False\n        admin_username:\n            description:\n                - The administrator\'s login name of a server.\n            returned: always\n            type: str\n            sample: serveradmin\n        version:\n            description:\n                - Server version.\n            returned: always\n            type: str\n            sample: "9.6"\n        user_visible_state:\n            description:\n                - A state of a server that is visible to user.\n            returned: always\n            type: str\n            sample: Ready\n        fully_qualified_domain_name:\n            description:\n                - The fully qualified domain name of a server.\n            returned: always\n            type: str\n            sample: myabdud1223.mys.database.azure.com\n        tags:\n            description:\n                - Tags assigned to the resource. Dictionary of string:string pairs.\n            type: dict\n            sample: { tag1: abc }\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.rdbms.mariadb import MariaDBManagementClient
    from msrest.serialization import Model
except ImportError:
    pass

class AzureRMMariaDbServerInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True), name=dict(type='str'), tags=dict(type='list'))
        self.results = dict(changed=False)
        self.resource_group = None
        self.name = None
        self.tags = None
        super(AzureRMMariaDbServerInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_mariadbserver_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_mariadbserver_facts' module has been renamed to 'azure_rm_mariadbserver_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        if self.resource_group is not None and self.name is not None:
            self.results['servers'] = self.get()
        elif self.resource_group is not None:
            self.results['servers'] = self.list_by_resource_group()
        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.mariadb_client.servers.get(resource_group_name=self.resource_group, server_name=self.name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for MariaDB Server.')
        if response and self.has_tags(response.tags, self.tags):
            results.append(self.format_item(response))
        return results

    def list_by_resource_group(self):
        response = None
        results = []
        try:
            response = self.mariadb_client.servers.list_by_resource_group(resource_group_name=self.resource_group)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for MariaDB Servers.')
        if response is not None:
            for item in response:
                if self.has_tags(item.tags, self.tags):
                    results.append(self.format_item(item))
        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {'id': d['id'], 'resource_group': self.resource_group, 'name': d['name'], 'sku': d['sku'], 'location': d['location'], 'storage_mb': d['storage_profile']['storage_mb'], 'version': d['version'], 'enforce_ssl': d['ssl_enforcement'] == 'Enabled', 'admin_username': d['administrator_login'], 'user_visible_state': d['user_visible_state'], 'fully_qualified_domain_name': d['fully_qualified_domain_name'], 'tags': d.get('tags')}
        return d

def main():
    AzureRMMariaDbServerInfo()
if __name__ == '__main__':
    main()

def test_AzureRMMariaDbServerInfo_exec_module():
    ret = AzureRMMariaDbServerInfo().exec_module()

def test_AzureRMMariaDbServerInfo_get():
    ret = AzureRMMariaDbServerInfo().get()

def test_AzureRMMariaDbServerInfo_list_by_resource_group():
    ret = AzureRMMariaDbServerInfo().list_by_resource_group()

def test_AzureRMMariaDbServerInfo_format_item():
    ret = AzureRMMariaDbServerInfo().format_item()