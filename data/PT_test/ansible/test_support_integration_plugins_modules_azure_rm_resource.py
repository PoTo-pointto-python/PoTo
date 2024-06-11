from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_resource\nversion_added: "2.6"\nshort_description: Create any Azure resource\ndescription:\n    - Create, update or delete any Azure resource using Azure REST API.\n    - This module gives access to resources that are not supported via Ansible modules.\n    - Refer to U(https://docs.microsoft.com/en-us/rest/api/) regarding details related to specific resource REST API.\n\noptions:\n    url:\n        description:\n            - Azure RM Resource URL.\n    api_version:\n        description:\n            - Specific API version to be used.\n    provider:\n        description:\n            - Provider type.\n            - Required if URL is not specified.\n    resource_group:\n        description:\n            - Resource group to be used.\n            - Required if URL is not specified.\n    resource_type:\n        description:\n            - Resource type.\n            - Required if URL is not specified.\n    resource_name:\n        description:\n            - Resource name.\n            - Required if URL Is not specified.\n    subresource:\n        description:\n            - List of subresources.\n        suboptions:\n            namespace:\n                description:\n                    - Subresource namespace.\n            type:\n                description:\n                    - Subresource type.\n            name:\n                description:\n                    - Subresource name.\n    body:\n        description:\n            - The body of the HTTP request/response to the web service.\n    method:\n        description:\n            - The HTTP method of the request or response. It must be uppercase.\n        choices:\n            - GET\n            - PUT\n            - POST\n            - HEAD\n            - PATCH\n            - DELETE\n            - MERGE\n        default: "PUT"\n    status_code:\n        description:\n            - A valid, numeric, HTTP status code that signifies success of the request. Can also be comma separated list of status codes.\n        type: list\n        default: [ 200, 201, 202 ]\n    idempotency:\n        description:\n            - If enabled, idempotency check will be done by using I(method=GET) first and then comparing with I(body).\n        default: no\n        type: bool\n    polling_timeout:\n        description:\n            - If enabled, idempotency check will be done by using I(method=GET) first and then comparing with I(body).\n        default: 0\n        type: int\n        version_added: "2.8"\n    polling_interval:\n        description:\n            - If enabled, idempotency check will be done by using I(method=GET) first and then comparing with I(body).\n        default: 60\n        type: int\n        version_added: "2.8"\n    state:\n        description:\n            - Assert the state of the resource. Use C(present) to create or update resource or C(absent) to delete resource.\n        default: present\n        choices:\n            - absent\n            - present\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n\n'
EXAMPLES = '\n  - name: Update scaleset info using azure_rm_resource\n    azure_rm_resource:\n      resource_group: myResourceGroup\n      provider: compute\n      resource_type: virtualmachinescalesets\n      resource_name: myVmss\n      api_version: "2017-12-01"\n      body: { body }\n'
RETURN = '\nresponse:\n    description:\n        - Response specific to resource type.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Resource ID.\n            type: str\n            returned: always\n            sample: "/subscriptions/xxxx...xxxx/resourceGroups/v-xisuRG/providers/Microsoft.Storage/storageAccounts/staccb57dc95183"\n        kind:\n            description:\n                - The kind of storage.\n            type: str\n            returned: always\n            sample: Storage\n        location:\n            description:\n                - The resource location, defaults to location of the resource group.\n            type: str\n            returned: always\n            sample: eastus\n        name:\n            description:\n                The storage account name.\n            type: str\n            returned: always\n            sample: staccb57dc95183\n        properties:\n            description:\n                - The storage account\'s related properties.\n            type: dict\n            returned: always\n            sample: {\n                    "creationTime": "2019-06-13T06:34:33.0996676Z",\n                    "encryption": {\n                                  "keySource": "Microsoft.Storage",\n                                  "services": {\n                                              "blob": {\n                                              "enabled": true,\n                                              "lastEnabledTime": "2019-06-13T06:34:33.1934074Z"\n                                                      },\n                                              "file": {\n                                                      "enabled": true,\n                                                      "lastEnabledTime": "2019-06-13T06:34:33.1934074Z"\n                                                      }\n                                               }\n                                  },\n                    "networkAcls": {\n                    "bypass": "AzureServices",\n                    "defaultAction": "Allow",\n                    "ipRules": [],\n                    "virtualNetworkRules": []\n                                   },\n                    "primaryEndpoints": {\n                    "blob": "https://staccb57dc95183.blob.core.windows.net/",\n                    "file": "https://staccb57dc95183.file.core.windows.net/",\n                    "queue": "https://staccb57dc95183.queue.core.windows.net/",\n                    "table": "https://staccb57dc95183.table.core.windows.net/"\n                                       },\n                    "primaryLocation": "eastus",\n                    "provisioningState": "Succeeded",\n                    "secondaryLocation": "westus",\n                    "statusOfPrimary": "available",\n                    "statusOfSecondary": "available",\n                    "supportsHttpsTrafficOnly": false\n                    }\n        sku:\n            description:\n                - The storage account SKU.\n            type: dict\n            returned: always\n            sample: {\n                    "name": "Standard_GRS",\n                    "tier": "Standard"\n                    }\n        tags:\n            description:\n                - Resource tags.\n            type: dict\n            returned: always\n            sample: { \'key1\': \'value1\' }\n        type:\n            description:\n                - The resource type.\n            type: str\n            returned: always\n            sample: "Microsoft.Storage/storageAccounts"\n\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
from ansible.module_utils.azure_rm_common_rest import GenericRestClient
from ansible.module_utils.common.dict_transformations import dict_merge
try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.service_client import ServiceClient
    from msrestazure.tools import resource_id, is_valid_resource_id
    import json
except ImportError:
    pass

class AzureRMResource(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(url=dict(type='str'), provider=dict(type='str'), resource_group=dict(type='str'), resource_type=dict(type='str'), resource_name=dict(type='str'), subresource=dict(type='list', default=[]), api_version=dict(type='str'), method=dict(type='str', default='PUT', choices=['GET', 'PUT', 'POST', 'HEAD', 'PATCH', 'DELETE', 'MERGE']), body=dict(type='raw'), status_code=dict(type='list', default=[200, 201, 202]), idempotency=dict(type='bool', default=False), polling_timeout=dict(type='int', default=0), polling_interval=dict(type='int', default=60), state=dict(type='str', default='present', choices=['present', 'absent']))
        self.results = dict(changed=False, response=None)
        self.mgmt_client = None
        self.url = None
        self.api_version = None
        self.provider = None
        self.resource_group = None
        self.resource_type = None
        self.resource_name = None
        self.subresource_type = None
        self.subresource_name = None
        self.subresource = []
        self.method = None
        self.status_code = []
        self.idempotency = False
        self.polling_timeout = None
        self.polling_interval = None
        self.state = None
        self.body = None
        super(AzureRMResource, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(GenericRestClient, base_url=self._cloud_environment.endpoints.resource_manager)
        if self.state == 'absent':
            self.method = 'DELETE'
            self.status_code.append(204)
        if self.url is None:
            orphan = None
            rargs = dict()
            rargs['subscription'] = self.subscription_id
            rargs['resource_group'] = self.resource_group
            if not (self.provider is None or self.provider.lower().startswith('.microsoft')):
                rargs['namespace'] = 'Microsoft.' + self.provider
            else:
                rargs['namespace'] = self.provider
            if self.resource_type is not None and self.resource_name is not None:
                rargs['type'] = self.resource_type
                rargs['name'] = self.resource_name
                for i in range(len(self.subresource)):
                    resource_ns = self.subresource[i].get('namespace', None)
                    resource_type = self.subresource[i].get('type', None)
                    resource_name = self.subresource[i].get('name', None)
                    if resource_type is not None and resource_name is not None:
                        rargs['child_namespace_' + str(i + 1)] = resource_ns
                        rargs['child_type_' + str(i + 1)] = resource_type
                        rargs['child_name_' + str(i + 1)] = resource_name
                    else:
                        orphan = resource_type
            else:
                orphan = self.resource_type
            self.url = resource_id(**rargs)
            if orphan is not None:
                self.url += '/' + orphan
        if not self.api_version:
            try:
                if '/providers/' in self.url:
                    provider = self.url.split('/providers/')[1].split('/')[0]
                    resourceType = self.url.split(provider + '/')[1].split('/')[0]
                    url = '/subscriptions/' + self.subscription_id + '/providers/' + provider
                    api_versions = json.loads(self.mgmt_client.query(url, 'GET', {'api-version': '2015-01-01'}, None, None, [200], 0, 0).text)
                    for rt in api_versions['resourceTypes']:
                        if rt['resourceType'].lower() == resourceType.lower():
                            self.api_version = rt['apiVersions'][0]
                            break
                else:
                    self.api_version = '2018-05-01'
                if not self.api_version:
                    self.fail("Couldn't find api version for {0}/{1}".format(provider, resourceType))
            except Exception as exc:
                self.fail('Failed to obtain API version: {0}'.format(str(exc)))
        query_parameters = {}
        query_parameters['api-version'] = self.api_version
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        needs_update = True
        response = None
        if self.idempotency:
            original = self.mgmt_client.query(self.url, 'GET', query_parameters, None, None, [200, 404], 0, 0)
            if original.status_code == 404:
                if self.state == 'absent':
                    needs_update = False
            else:
                try:
                    response = json.loads(original.text)
                    needs_update = dict_merge(response, self.body) != response
                except Exception:
                    pass
        if needs_update:
            response = self.mgmt_client.query(self.url, self.method, query_parameters, header_parameters, self.body, self.status_code, self.polling_timeout, self.polling_interval)
            if self.state == 'present':
                try:
                    response = json.loads(response.text)
                except Exception:
                    response = response.text
            else:
                response = None
        self.results['response'] = response
        self.results['changed'] = needs_update
        return self.results

def main():
    AzureRMResource()
if __name__ == '__main__':
    main()

def test_AzureRMResource_exec_module():
    ret = AzureRMResource().exec_module()