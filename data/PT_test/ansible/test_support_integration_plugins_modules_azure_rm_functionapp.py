from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_functionapp\nversion_added: "2.4"\nshort_description: Manage Azure Function Apps\ndescription:\n    - Create, update or delete an Azure Function App.\noptions:\n    resource_group:\n        description:\n            - Name of resource group.\n        required: true\n        aliases:\n            - resource_group_name\n    name:\n        description:\n            - Name of the Azure Function App.\n        required: true\n    location:\n        description:\n            - Valid Azure location. Defaults to location of the resource group.\n    plan:\n        description:\n            - App service plan.\n            - It can be name of existing app service plan in same resource group as function app.\n            - It can be resource id of existing app service plan.\n            - Resource id. For example /subscriptions/<subs_id>/resourceGroups/<resource_group>/providers/Microsoft.Web/serverFarms/<plan_name>.\n            - It can be a dict which contains C(name), C(resource_group).\n            - C(name). Name of app service plan.\n            - C(resource_group). Resource group name of app service plan.\n        version_added: "2.8"\n    container_settings:\n        description: Web app container settings.\n        suboptions:\n            name:\n                description:\n                    - Name of container. For example "imagename:tag".\n            registry_server_url:\n                description:\n                    - Container registry server url. For example C(mydockerregistry.io).\n            registry_server_user:\n                description:\n                    - The container registry server user name.\n            registry_server_password:\n                description:\n                    - The container registry server password.\n        version_added: "2.8"\n    storage_account:\n        description:\n            - Name of the storage account to use.\n        required: true\n        aliases:\n            - storage\n            - storage_account_name\n    app_settings:\n        description:\n            - Dictionary containing application settings.\n    state:\n        description:\n            - Assert the state of the Function App. Use C(present) to create or update a Function App and C(absent) to delete.\n        default: present\n        choices:\n            - absent\n            - present\n\nextends_documentation_fragment:\n    - azure\n    - azure_tags\n\nauthor:\n    - Thomas Stringer (@trstringer)\n'
EXAMPLES = '\n- name: Create a function app\n  azure_rm_functionapp:\n    resource_group: myResourceGroup\n    name: myFunctionApp\n    storage_account: myStorageAccount\n\n- name: Create a function app with app settings\n  azure_rm_functionapp:\n    resource_group: myResourceGroup\n    name: myFunctionApp\n    storage_account: myStorageAccount\n    app_settings:\n      setting1: value1\n      setting2: value2\n\n- name: Create container based function app\n  azure_rm_functionapp:\n    resource_group: myResourceGroup\n    name: myFunctionApp\n    storage_account: myStorageAccount\n    plan:\n      resource_group: myResourceGroup\n      name: myAppPlan\n    container_settings:\n      name: httpd\n      registry_server_url: index.docker.io\n\n- name: Delete a function app\n  azure_rm_functionapp:\n    resource_group: myResourceGroup\n    name: myFunctionApp\n    state: absent\n'
RETURN = '\nstate:\n    description:\n        - Current state of the Azure Function App.\n    returned: success\n    type: dict\n    example:\n        id: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/myFunctionApp\n        name: myfunctionapp\n        kind: functionapp\n        location: East US\n        type: Microsoft.Web/sites\n        state: Running\n        host_names:\n          - myfunctionapp.azurewebsites.net\n        repository_site_name: myfunctionapp\n        usage_state: Normal\n        enabled: true\n        enabled_host_names:\n          - myfunctionapp.azurewebsites.net\n          - myfunctionapp.scm.azurewebsites.net\n        availability_state: Normal\n        host_name_ssl_states:\n          - name: myfunctionapp.azurewebsites.net\n            ssl_state: Disabled\n            host_type: Standard\n          - name: myfunctionapp.scm.azurewebsites.net\n            ssl_state: Disabled\n            host_type: Repository\n        server_farm_id: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/serverfarms/EastUSPlan\n        reserved: false\n        last_modified_time_utc: 2017-08-22T18:54:01.190Z\n        scm_site_also_stopped: false\n        client_affinity_enabled: true\n        client_cert_enabled: false\n        host_names_disabled: false\n        outbound_ip_addresses: ............\n        container_size: 1536\n        daily_memory_time_quota: 0\n        resource_group: myResourceGroup\n        default_host_name: myfunctionapp.azurewebsites.net\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.web.models import site_config, app_service_plan, Site, SiteConfig, NameValuePair, SiteSourceControl, AppServicePlan, SkuDescription
    from azure.mgmt.resource.resources import ResourceManagementClient
    from msrest.polling import LROPoller
except ImportError:
    pass
container_settings_spec = dict(name=dict(type='str', required=True), registry_server_url=dict(type='str'), registry_server_user=dict(type='str'), registry_server_password=dict(type='str', no_log=True))

class AzureRMFunctionApp(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True, aliases=['resource_group_name']), name=dict(type='str', required=True), state=dict(type='str', default='present', choices=['present', 'absent']), location=dict(type='str'), storage_account=dict(type='str', aliases=['storage', 'storage_account_name']), app_settings=dict(type='dict'), plan=dict(type='raw'), container_settings=dict(type='dict', options=container_settings_spec))
        self.results = dict(changed=False, state=dict())
        self.resource_group = None
        self.name = None
        self.state = None
        self.location = None
        self.storage_account = None
        self.app_settings = None
        self.plan = None
        self.container_settings = None
        required_if = [('state', 'present', ['storage_account'])]
        super(AzureRMFunctionApp, self).__init__(self.module_arg_spec, supports_check_mode=True, required_if=required_if)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        if self.app_settings is None:
            self.app_settings = dict()
        try:
            resource_group = self.rm_client.resource_groups.get(self.resource_group)
        except CloudError:
            self.fail('Unable to retrieve resource group')
        self.location = self.location or resource_group.location
        try:
            function_app = self.web_client.web_apps.get(resource_group_name=self.resource_group, name=self.name)
            exists = function_app is not None
        except CloudError as exc:
            exists = False
        if self.state == 'absent':
            if exists:
                if self.check_mode:
                    self.results['changed'] = True
                    return self.results
                try:
                    self.web_client.web_apps.delete(resource_group_name=self.resource_group, name=self.name)
                    self.results['changed'] = True
                except CloudError as exc:
                    self.fail('Failure while deleting web app: {0}'.format(exc))
            else:
                self.results['changed'] = False
        else:
            kind = 'functionapp'
            linux_fx_version = None
            if self.container_settings and self.container_settings.get('name'):
                kind = 'functionapp,linux,container'
                linux_fx_version = 'DOCKER|'
                if self.container_settings.get('registry_server_url'):
                    self.app_settings['DOCKER_REGISTRY_SERVER_URL'] = 'https://' + self.container_settings['registry_server_url']
                    linux_fx_version += self.container_settings['registry_server_url'] + '/'
                linux_fx_version += self.container_settings['name']
                if self.container_settings.get('registry_server_user'):
                    self.app_settings['DOCKER_REGISTRY_SERVER_USERNAME'] = self.container_settings.get('registry_server_user')
                if self.container_settings.get('registry_server_password'):
                    self.app_settings['DOCKER_REGISTRY_SERVER_PASSWORD'] = self.container_settings.get('registry_server_password')
            if not self.plan and function_app:
                self.plan = function_app.server_farm_id
            if not exists:
                function_app = Site(location=self.location, kind=kind, site_config=SiteConfig(app_settings=self.aggregated_app_settings(), scm_type='LocalGit'))
                self.results['changed'] = True
            else:
                (self.results['changed'], function_app) = self.update(function_app)
            if self.plan:
                if isinstance(self.plan, dict):
                    self.plan = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Web/serverfarms/{2}'.format(self.subscription_id, self.plan.get('resource_group', self.resource_group), self.plan.get('name'))
                function_app.server_farm_id = self.plan
            if linux_fx_version:
                function_app.site_config.linux_fx_version = linux_fx_version
            if self.check_mode:
                self.results['state'] = function_app.as_dict()
            elif self.results['changed']:
                try:
                    new_function_app = self.web_client.web_apps.create_or_update(resource_group_name=self.resource_group, name=self.name, site_envelope=function_app).result()
                    self.results['state'] = new_function_app.as_dict()
                except CloudError as exc:
                    self.fail('Error creating or updating web app: {0}'.format(exc))
        return self.results

    def update(self, source_function_app):
        """Update the Site object if there are any changes"""
        source_app_settings = self.web_client.web_apps.list_application_settings(resource_group_name=self.resource_group, name=self.name)
        (changed, target_app_settings) = self.update_app_settings(source_app_settings.properties)
        source_function_app.site_config = SiteConfig(app_settings=target_app_settings, scm_type='LocalGit')
        return (changed, source_function_app)

    def update_app_settings(self, source_app_settings):
        """Update app settings"""
        target_app_settings = self.aggregated_app_settings()
        target_app_settings_dict = dict([(i.name, i.value) for i in target_app_settings])
        return (target_app_settings_dict != source_app_settings, target_app_settings)

    def necessary_functionapp_settings(self):
        """Construct the necessary app settings required for an Azure Function App"""
        function_app_settings = []
        if self.container_settings is None:
            for key in ['AzureWebJobsStorage', 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING', 'AzureWebJobsDashboard']:
                function_app_settings.append(NameValuePair(name=key, value=self.storage_connection_string))
            function_app_settings.append(NameValuePair(name='FUNCTIONS_EXTENSION_VERSION', value='~1'))
            function_app_settings.append(NameValuePair(name='WEBSITE_NODE_DEFAULT_VERSION', value='6.5.0'))
            function_app_settings.append(NameValuePair(name='WEBSITE_CONTENTSHARE', value=self.name))
        else:
            function_app_settings.append(NameValuePair(name='FUNCTIONS_EXTENSION_VERSION', value='~2'))
            function_app_settings.append(NameValuePair(name='WEBSITES_ENABLE_APP_SERVICE_STORAGE', value=False))
            function_app_settings.append(NameValuePair(name='AzureWebJobsStorage', value=self.storage_connection_string))
        return function_app_settings

    def aggregated_app_settings(self):
        """Combine both system and user app settings"""
        function_app_settings = self.necessary_functionapp_settings()
        for app_setting_key in self.app_settings:
            found_setting = None
            for s in function_app_settings:
                if s.name == app_setting_key:
                    found_setting = s
                    break
            if found_setting:
                found_setting.value = self.app_settings[app_setting_key]
            else:
                function_app_settings.append(NameValuePair(name=app_setting_key, value=self.app_settings[app_setting_key]))
        return function_app_settings

    @property
    def storage_connection_string(self):
        """Construct the storage account connection string"""
        return 'DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1}'.format(self.storage_account, self.storage_key)

    @property
    def storage_key(self):
        """Retrieve the storage account key"""
        return self.storage_client.storage_accounts.list_keys(resource_group_name=self.resource_group, account_name=self.storage_account).keys[0].value

def main():
    """Main function execution"""
    AzureRMFunctionApp()
if __name__ == '__main__':
    main()

def test_AzureRMFunctionApp_exec_module():
    ret = AzureRMFunctionApp().exec_module()

def test_AzureRMFunctionApp_update():
    ret = AzureRMFunctionApp().update()

def test_AzureRMFunctionApp_update_app_settings():
    ret = AzureRMFunctionApp().update_app_settings()

def test_AzureRMFunctionApp_necessary_functionapp_settings():
    ret = AzureRMFunctionApp().necessary_functionapp_settings()

def test_AzureRMFunctionApp_aggregated_app_settings():
    ret = AzureRMFunctionApp().aggregated_app_settings()

def test_AzureRMFunctionApp_storage_connection_string():
    ret = AzureRMFunctionApp().storage_connection_string()

def test_AzureRMFunctionApp_storage_key():
    ret = AzureRMFunctionApp().storage_key()