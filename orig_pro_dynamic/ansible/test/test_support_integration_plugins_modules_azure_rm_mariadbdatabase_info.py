from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_mariadbdatabase_info\nversion_added: "2.9"\nshort_description: Get Azure MariaDB Database facts\ndescription:\n    - Get facts of MariaDB Database.\n\noptions:\n    resource_group:\n        description:\n            - The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.\n        required: True\n        type: str\n    server_name:\n        description:\n            - The name of the server.\n        required: True\n        type: str\n    name:\n        description:\n            - The name of the database.\n        type: str\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n    - Matti Ranta (@techknowlogick)\n\n'
EXAMPLES = '\n  - name: Get instance of MariaDB Database\n    azure_rm_mariadbdatabase_info:\n      resource_group: myResourceGroup\n      server_name: server_name\n      name: database_name\n\n  - name: List instances of MariaDB Database\n    azure_rm_mariadbdatabase_info:\n      resource_group: myResourceGroup\n      server_name: server_name\n'
RETURN = '\ndatabases:\n    description:\n        - A list of dictionaries containing facts for MariaDB Databases.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Resource ID.\n            returned: always\n            type: str\n            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.DBforMariaDB/servers/testser\n                    ver/databases/db1"\n        resource_group:\n            description:\n                - Resource group name.\n            returned: always\n            type: str\n            sample: testrg\n        server_name:\n            description:\n                - Server name.\n            returned: always\n            type: str\n            sample: testserver\n        name:\n            description:\n                - Resource name.\n            returned: always\n            type: str\n            sample: db1\n        charset:\n            description:\n                - The charset of the database.\n            returned: always\n            type: str\n            sample: UTF8\n        collation:\n            description:\n                - The collation of the database.\n            returned: always\n            type: str\n            sample: English_United States.1252\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.rdbms.mariadb import MariaDBManagementClient
    from msrest.serialization import Model
except ImportError:
    pass

class AzureRMMariaDbDatabaseInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True), server_name=dict(type='str', required=True), name=dict(type='str'))
        self.results = dict(changed=False)
        self.resource_group = None
        self.server_name = None
        self.name = None
        super(AzureRMMariaDbDatabaseInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_mariadbdatabase_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_mariadbdatabase_facts' module has been renamed to 'azure_rm_mariadbdatabase_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        if self.resource_group is not None and self.server_name is not None and (self.name is not None):
            self.results['databases'] = self.get()
        elif self.resource_group is not None and self.server_name is not None:
            self.results['databases'] = self.list_by_server()
        return self.results

    def get(self):
        response = None
        results = []
        try:
            response = self.mariadb_client.databases.get(resource_group_name=self.resource_group, server_name=self.server_name, database_name=self.name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.log('Could not get facts for Databases.')
        if response is not None:
            results.append(self.format_item(response))
        return results

    def list_by_server(self):
        response = None
        results = []
        try:
            response = self.mariadb_client.databases.list_by_server(resource_group_name=self.resource_group, server_name=self.server_name)
            self.log('Response : {0}'.format(response))
        except CloudError as e:
            self.fail('Error listing for server {0} - {1}'.format(self.server_name, str(e)))
        if response is not None:
            for item in response:
                results.append(self.format_item(item))
        return results

    def format_item(self, item):
        d = item.as_dict()
        d = {'resource_group': self.resource_group, 'server_name': self.server_name, 'name': d['name'], 'charset': d['charset'], 'collation': d['collation']}
        return d

def main():
    AzureRMMariaDbDatabaseInfo()
if __name__ == '__main__':
    main()

def test_AzureRMMariaDbDatabaseInfo_exec_module():
    ret = AzureRMMariaDbDatabaseInfo().exec_module()

def test_AzureRMMariaDbDatabaseInfo_get():
    ret = AzureRMMariaDbDatabaseInfo().get()

def test_AzureRMMariaDbDatabaseInfo_list_by_server():
    ret = AzureRMMariaDbDatabaseInfo().list_by_server()

def test_AzureRMMariaDbDatabaseInfo_format_item():
    ret = AzureRMMariaDbDatabaseInfo().format_item()