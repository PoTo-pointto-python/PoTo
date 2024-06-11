from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_functionapp_info\nversion_added: "2.9"\nshort_description: Get Azure Function App facts\ndescription:\n    - Get facts for one Azure Function App or all Function Apps within a resource group.\noptions:\n    name:\n        description:\n            - Only show results for a specific Function App.\n    resource_group:\n        description:\n            - Limit results to a resource group. Required when filtering by name.\n        aliases:\n            - resource_group_name\n    tags:\n        description:\n            - Limit results by providing a list of tags. Format tags as \'key\' or \'key:value\'.\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Thomas Stringer (@trstringer)\n'
EXAMPLES = '\n    - name: Get facts for one Function App\n      azure_rm_functionapp_info:\n        resource_group: myResourceGroup\n        name: myfunctionapp\n\n    - name: Get facts for all Function Apps in a resource group\n      azure_rm_functionapp_info:\n        resource_group: myResourceGroup\n\n    - name: Get facts for all Function Apps by tags\n      azure_rm_functionapp_info:\n        tags:\n          - testing\n'
RETURN = '\nazure_functionapps:\n    description:\n        - List of Azure Function Apps dicts.\n    returned: always\n    type: list\n    example:\n        id: /subscriptions/.../resourceGroups/ansible-rg/providers/Microsoft.Web/sites/myfunctionapp\n        name: myfunctionapp\n        kind: functionapp\n        location: East US\n        type: Microsoft.Web/sites\n        state: Running\n        host_names:\n          - myfunctionapp.azurewebsites.net\n        repository_site_name: myfunctionapp\n        usage_state: Normal\n        enabled: true\n        enabled_host_names:\n          - myfunctionapp.azurewebsites.net\n          - myfunctionapp.scm.azurewebsites.net\n        availability_state: Normal\n        host_name_ssl_states:\n          - name: myfunctionapp.azurewebsites.net\n            ssl_state: Disabled\n            host_type: Standard\n          - name: myfunctionapp.scm.azurewebsites.net\n            ssl_state: Disabled\n            host_type: Repository\n        server_farm_id: /subscriptions/.../resourceGroups/ansible-rg/providers/Microsoft.Web/serverfarms/EastUSPlan\n        reserved: false\n        last_modified_time_utc: 2017-08-22T18:54:01.190Z\n        scm_site_also_stopped: false\n        client_affinity_enabled: true\n        client_cert_enabled: false\n        host_names_disabled: false\n        outbound_ip_addresses: ............\n        container_size: 1536\n        daily_memory_time_quota: 0\n        resource_group: myResourceGroup\n        default_host_name: myfunctionapp.azurewebsites.net\n'
try:
    from msrestazure.azure_exceptions import CloudError
except Exception:
    pass
from ansible.module_utils.azure_rm_common import AzureRMModuleBase

class AzureRMFunctionAppInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(name=dict(type='str'), resource_group=dict(type='str', aliases=['resource_group_name']), tags=dict(type='list'))
        self.results = dict(changed=False, ansible_info=dict(azure_functionapps=[]))
        self.name = None
        self.resource_group = None
        self.tags = None
        super(AzureRMFunctionAppInfo, self).__init__(self.module_arg_spec, supports_tags=False, facts_module=True)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_functionapp_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_functionapp_facts' module has been renamed to 'azure_rm_functionapp_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        if self.name and (not self.resource_group):
            self.fail('Parameter error: resource group required when filtering by name.')
        if self.name:
            self.results['ansible_info']['azure_functionapps'] = self.get_functionapp()
        elif self.resource_group:
            self.results['ansible_info']['azure_functionapps'] = self.list_resource_group()
        else:
            self.results['ansible_info']['azure_functionapps'] = self.list_all()
        return self.results

    def get_functionapp(self):
        self.log('Get properties for Function App {0}'.format(self.name))
        function_app = None
        result = []
        try:
            function_app = self.web_client.web_apps.get(self.resource_group, self.name)
        except CloudError:
            pass
        if function_app and self.has_tags(function_app.tags, self.tags):
            result = function_app.as_dict()
        return [result]

    def list_resource_group(self):
        self.log('List items')
        try:
            response = self.web_client.web_apps.list_by_resource_group(self.resource_group)
        except Exception as exc:
            self.fail('Error listing for resource group {0} - {1}'.format(self.resource_group, str(exc)))
        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(item.as_dict())
        return results

    def list_all(self):
        self.log('List all items')
        try:
            response = self.web_client.web_apps.list_by_resource_group(self.resource_group)
        except Exception as exc:
            self.fail('Error listing all items - {0}'.format(str(exc)))
        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(item.as_dict())
        return results

def main():
    AzureRMFunctionAppInfo()
if __name__ == '__main__':
    main()

def test_AzureRMFunctionAppInfo_exec_module():
    ret = AzureRMFunctionAppInfo().exec_module()

def test_AzureRMFunctionAppInfo_get_functionapp():
    ret = AzureRMFunctionAppInfo().get_functionapp()

def test_AzureRMFunctionAppInfo_list_resource_group():
    ret = AzureRMFunctionAppInfo().list_resource_group()

def test_AzureRMFunctionAppInfo_list_all():
    ret = AzureRMFunctionAppInfo().list_all()