from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_webapp_info\n\nversion_added: "2.9"\n\nshort_description: Get Azure web app facts\n\ndescription:\n    - Get facts for a specific web app or all web app in a resource group, or all web app in current subscription.\n\noptions:\n    name:\n        description:\n            - Only show results for a specific web app.\n    resource_group:\n        description:\n            - Limit results by resource group.\n    return_publish_profile:\n        description:\n            - Indicate whether to return publishing profile of the web app.\n        default: False\n        type: bool\n    tags:\n        description:\n            - Limit results by providing a list of tags. Format tags as \'key\' or \'key:value\'.\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Yunge Zhu (@yungezz)\n'
EXAMPLES = '\n    - name: Get facts for web app by name\n      azure_rm_webapp_info:\n        resource_group: myResourceGroup\n        name: winwebapp1\n\n    - name: Get facts for web apps in resource group\n      azure_rm_webapp_info:\n        resource_group: myResourceGroup\n\n    - name: Get facts for web apps with tags\n      azure_rm_webapp_info:\n        tags:\n          - testtag\n          - foo:bar\n'
RETURN = '\nwebapps:\n    description:\n        - List of web apps.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - ID of the web app.\n            returned: always\n            type: str\n            sample: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/myWebApp\n        name:\n            description:\n                - Name of the web app.\n            returned: always\n            type: str\n            sample: winwebapp1\n        resource_group:\n            description:\n                - Resource group of the web app.\n            returned: always\n            type: str\n            sample: myResourceGroup\n        location:\n            description:\n                - Location of the web app.\n            returned: always\n            type: str\n            sample: eastus\n        plan:\n            description:\n                - ID of app service plan used by the web app.\n            returned: always\n            type: str\n            sample: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/serverfarms/myAppServicePlan\n        app_settings:\n            description:\n                - App settings of the application. Only returned when web app has app settings.\n            returned: always\n            type: dict\n            sample: {\n                    "testkey": "testvalue",\n                    "testkey2": "testvalue2"\n                    }\n        frameworks:\n            description:\n                - Frameworks of the application. Only returned when web app has frameworks.\n            returned: always\n            type: list\n            sample: [\n                    {\n                        "name": "net_framework",\n                        "version": "v4.0"\n                    },\n                    {\n                        "name": "java",\n                        "settings": {\n                            "java_container": "tomcat",\n                            "java_container_version": "8.5"\n                        },\n                        "version": "1.7"\n                    },\n                    {\n                        "name": "php",\n                        "version": "5.6"\n                    }\n                    ]\n        availability_state:\n            description:\n                - Availability of this web app.\n            returned: always\n            type: str\n            sample: Normal\n        default_host_name:\n            description:\n                - Host name of the web app.\n            returned: always\n            type: str\n            sample: vxxisurg397winapp4.azurewebsites.net\n        enabled:\n            description:\n                - Indicates the web app enabled or not.\n            returned: always\n            type: bool\n            sample: true\n        enabled_host_names:\n            description:\n                - Enabled host names of the web app.\n            returned: always\n            type: list\n            sample: [\n                    "vxxisurg397winapp4.azurewebsites.net",\n                    "vxxisurg397winapp4.scm.azurewebsites.net"\n                    ]\n        host_name_ssl_states:\n            description:\n                - SSL state per host names of the web app.\n            returned: always\n            type: list\n            sample: [\n                    {\n                        "hostType": "Standard",\n                        "name": "vxxisurg397winapp4.azurewebsites.net",\n                        "sslState": "Disabled"\n                    },\n                    {\n                        "hostType": "Repository",\n                        "name": "vxxisurg397winapp4.scm.azurewebsites.net",\n                        "sslState": "Disabled"\n                    }\n                    ]\n        host_names:\n            description:\n                - Host names of the web app.\n            returned: always\n            type: list\n            sample: [\n                    "vxxisurg397winapp4.azurewebsites.net"\n                    ]\n        outbound_ip_addresses:\n            description:\n                - Outbound IP address of the web app.\n            returned: always\n            type: str\n            sample: "40.71.11.131,40.85.166.200,168.62.166.67,137.135.126.248,137.135.121.45"\n        ftp_publish_url:\n            description:\n                - Publishing URL of the web app when deployment type is FTP.\n            returned: always\n            type: str\n            sample: ftp://xxxx.ftp.azurewebsites.windows.net\n        state:\n            description:\n                - State of the web app.\n            returned: always\n            type: str\n            sample: running\n        publishing_username:\n            description:\n                - Publishing profile user name.\n            returned: only when I(return_publish_profile=True).\n            type: str\n            sample: "$vxxisuRG397winapp4"\n        publishing_password:\n            description:\n                - Publishing profile password.\n            returned: only when I(return_publish_profile=True).\n            type: str\n            sample: "uvANsPQpGjWJmrFfm4Ssd5rpBSqGhjMk11pMSgW2vCsQtNx9tcgZ0xN26s9A"\n        tags:\n            description:\n               - Tags assigned to the resource. Dictionary of string:string pairs.\n            returned: always\n            type: dict\n            sample: { tag1: abc }\n'
try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.polling import LROPoller
    from azure.common import AzureMissingResourceHttpError, AzureHttpError
except Exception:
    pass
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
AZURE_OBJECT_CLASS = 'WebApp'

class AzureRMWebAppInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(name=dict(type='str'), resource_group=dict(type='str'), tags=dict(type='list'), return_publish_profile=dict(type='bool', default=False))
        self.results = dict(changed=False, webapps=[])
        self.name = None
        self.resource_group = None
        self.tags = None
        self.return_publish_profile = False
        self.framework_names = ['net_framework', 'java', 'php', 'node', 'python', 'dotnetcore', 'ruby']
        super(AzureRMWebAppInfo, self).__init__(self.module_arg_spec, supports_tags=False, facts_module=True)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_webapp_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_webapp_facts' module has been renamed to 'azure_rm_webapp_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        if self.name:
            self.results['webapps'] = self.list_by_name()
        elif self.resource_group:
            self.results['webapps'] = self.list_by_resource_group()
        else:
            self.results['webapps'] = self.list_all()
        return self.results

    def list_by_name(self):
        self.log('Get web app {0}'.format(self.name))
        item = None
        result = []
        try:
            item = self.web_client.web_apps.get(self.resource_group, self.name)
        except CloudError:
            pass
        if item and self.has_tags(item.tags, self.tags):
            curated_result = self.get_curated_webapp(self.resource_group, self.name, item)
            result = [curated_result]
        return result

    def list_by_resource_group(self):
        self.log('List web apps in resource groups {0}'.format(self.resource_group))
        try:
            response = list(self.web_client.web_apps.list_by_resource_group(self.resource_group))
        except CloudError as exc:
            request_id = exc.request_id if exc.request_id else ''
            self.fail('Error listing web apps in resource groups {0}, request id: {1} - {2}'.format(self.resource_group, request_id, str(exc)))
        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                curated_output = self.get_curated_webapp(self.resource_group, item.name, item)
                results.append(curated_output)
        return results

    def list_all(self):
        self.log('List web apps in current subscription')
        try:
            response = list(self.web_client.web_apps.list())
        except CloudError as exc:
            request_id = exc.request_id if exc.request_id else ''
            self.fail('Error listing web apps, request id {0} - {1}'.format(request_id, str(exc)))
        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                curated_output = self.get_curated_webapp(item.resource_group, item.name, item)
                results.append(curated_output)
        return results

    def list_webapp_configuration(self, resource_group, name):
        self.log('Get web app {0} configuration'.format(name))
        response = []
        try:
            response = self.web_client.web_apps.get_configuration(resource_group_name=resource_group, name=name)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} configuration, request id {1} - {2}'.format(name, request_id, str(ex)))
        return response.as_dict()

    def list_webapp_appsettings(self, resource_group, name):
        self.log('Get web app {0} app settings'.format(name))
        response = []
        try:
            response = self.web_client.web_apps.list_application_settings(resource_group_name=resource_group, name=name)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} app settings, request id {1} - {2}'.format(name, request_id, str(ex)))
        return response.as_dict()

    def get_publish_credentials(self, resource_group, name):
        self.log('Get web app {0} publish credentials'.format(name))
        try:
            poller = self.web_client.web_apps.list_publishing_credentials(resource_group, name)
            if isinstance(poller, LROPoller):
                response = self.get_poller_result(poller)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} publishing credentials - {1}'.format(request_id, str(ex)))
        return response

    def get_webapp_ftp_publish_url(self, resource_group, name):
        import xmltodict
        self.log('Get web app {0} app publish profile'.format(name))
        url = None
        try:
            content = self.web_client.web_apps.list_publishing_profile_xml_with_secrets(resource_group_name=resource_group, name=name)
            if not content:
                return url
            full_xml = ''
            for f in content:
                full_xml += f.decode()
            profiles = xmltodict.parse(full_xml, xml_attribs=True)['publishData']['publishProfile']
            if not profiles:
                return url
            for profile in profiles:
                if profile['@publishMethod'] == 'FTP':
                    url = profile['@publishUrl']
        except CloudError as ex:
            self.fail('Error getting web app {0} app settings'.format(name))
        return url

    def get_curated_webapp(self, resource_group, name, webapp):
        pip = self.serialize_obj(webapp, AZURE_OBJECT_CLASS)
        try:
            site_config = self.list_webapp_configuration(resource_group, name)
            app_settings = self.list_webapp_appsettings(resource_group, name)
            publish_cred = self.get_publish_credentials(resource_group, name)
            ftp_publish_url = self.get_webapp_ftp_publish_url(resource_group, name)
        except CloudError as ex:
            pass
        return self.construct_curated_webapp(webapp=pip, configuration=site_config, app_settings=app_settings, deployment_slot=None, ftp_publish_url=ftp_publish_url, publish_credentials=publish_cred)

    def construct_curated_webapp(self, webapp, configuration=None, app_settings=None, deployment_slot=None, ftp_publish_url=None, publish_credentials=None):
        curated_output = dict()
        curated_output['id'] = webapp['id']
        curated_output['name'] = webapp['name']
        curated_output['resource_group'] = webapp['properties']['resourceGroup']
        curated_output['location'] = webapp['location']
        curated_output['plan'] = webapp['properties']['serverFarmId']
        curated_output['tags'] = webapp.get('tags', None)
        curated_output['app_state'] = webapp['properties']['state']
        curated_output['availability_state'] = webapp['properties']['availabilityState']
        curated_output['default_host_name'] = webapp['properties']['defaultHostName']
        curated_output['host_names'] = webapp['properties']['hostNames']
        curated_output['enabled'] = webapp['properties']['enabled']
        curated_output['enabled_host_names'] = webapp['properties']['enabledHostNames']
        curated_output['host_name_ssl_states'] = webapp['properties']['hostNameSslStates']
        curated_output['outbound_ip_addresses'] = webapp['properties']['outboundIpAddresses']
        if configuration:
            curated_output['frameworks'] = []
            for fx_name in self.framework_names:
                fx_version = configuration.get(fx_name + '_version', None)
                if fx_version:
                    fx = {'name': fx_name, 'version': fx_version}
                    if fx_name == 'java':
                        if configuration['java_container'] and configuration['java_container_version']:
                            settings = {'java_container': configuration['java_container'].lower(), 'java_container_version': configuration['java_container_version']}
                            fx['settings'] = settings
                    curated_output['frameworks'].append(fx)
            if configuration.get('linux_fx_version', None):
                tmp = configuration.get('linux_fx_version').split('|')
                if len(tmp) == 2:
                    curated_output['frameworks'].append({'name': tmp[0].lower(), 'version': tmp[1]})
        if app_settings and app_settings.get('properties', None):
            curated_output['app_settings'] = dict()
            for item in app_settings['properties']:
                curated_output['app_settings'][item] = app_settings['properties'][item]
        if deployment_slot:
            curated_output['deployment_slot'] = deployment_slot
        if ftp_publish_url:
            curated_output['ftp_publish_url'] = ftp_publish_url
        if publish_credentials and self.return_publish_profile:
            curated_output['publishing_username'] = publish_credentials.publishing_user_name
            curated_output['publishing_password'] = publish_credentials.publishing_password
        return curated_output

def main():
    AzureRMWebAppInfo()
if __name__ == '__main__':
    main()

def test_AzureRMWebAppInfo_exec_module():
    ret = AzureRMWebAppInfo().exec_module()

def test_AzureRMWebAppInfo_list_by_name():
    ret = AzureRMWebAppInfo().list_by_name()

def test_AzureRMWebAppInfo_list_by_resource_group():
    ret = AzureRMWebAppInfo().list_by_resource_group()

def test_AzureRMWebAppInfo_list_all():
    ret = AzureRMWebAppInfo().list_all()

def test_AzureRMWebAppInfo_list_webapp_configuration():
    ret = AzureRMWebAppInfo().list_webapp_configuration()

def test_AzureRMWebAppInfo_list_webapp_appsettings():
    ret = AzureRMWebAppInfo().list_webapp_appsettings()

def test_AzureRMWebAppInfo_get_publish_credentials():
    ret = AzureRMWebAppInfo().get_publish_credentials()

def test_AzureRMWebAppInfo_get_webapp_ftp_publish_url():
    ret = AzureRMWebAppInfo().get_webapp_ftp_publish_url()

def test_AzureRMWebAppInfo_get_curated_webapp():
    ret = AzureRMWebAppInfo().get_curated_webapp()

def test_AzureRMWebAppInfo_construct_curated_webapp():
    ret = AzureRMWebAppInfo().construct_curated_webapp()