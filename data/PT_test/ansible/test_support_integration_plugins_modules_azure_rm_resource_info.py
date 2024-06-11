from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_resource_info\nversion_added: "2.9"\nshort_description: Generic facts of Azure resources\ndescription:\n    - Obtain facts of any resource using Azure REST API.\n    - This module gives access to resources that are not supported via Ansible modules.\n    - Refer to U(https://docs.microsoft.com/en-us/rest/api/) regarding details related to specific resource REST API.\n\noptions:\n    url:\n        description:\n            - Azure RM Resource URL.\n    api_version:\n        description:\n            - Specific API version to be used.\n    provider:\n        description:\n            - Provider type, should be specified in no URL is given.\n    resource_group:\n        description:\n            - Resource group to be used.\n            - Required if URL is not specified.\n    resource_type:\n        description:\n            - Resource type.\n    resource_name:\n        description:\n            - Resource name.\n    subresource:\n        description:\n            - List of subresources.\n        suboptions:\n            namespace:\n                description:\n                    - Subresource namespace.\n            type:\n                description:\n                    - Subresource type.\n            name:\n                description:\n                    - Subresource name.\n\nextends_documentation_fragment:\n    - azure\n\nauthor:\n    - Zim Kalinowski (@zikalino)\n\n'
EXAMPLES = '\n  - name: Get scaleset info\n    azure_rm_resource_info:\n      resource_group: myResourceGroup\n      provider: compute\n      resource_type: virtualmachinescalesets\n      resource_name: myVmss\n      api_version: "2017-12-01"\n\n  - name: Query all the resources in the resource group\n    azure_rm_resource_info:\n      resource_group: "{{ resource_group }}"\n      resource_type: resources\n'
RETURN = '\nresponse:\n    description:\n        - Response specific to resource type.\n    returned: always\n    type: complex\n    contains:\n        id:\n            description:\n                - Id of the Azure resource.\n            type: str\n            returned: always\n            sample: "/subscriptions/xxxx...xxxx/resourceGroups/v-xisuRG/providers/Microsoft.Compute/virtualMachines/myVM"\n        location:\n            description:\n                - Resource location.\n            type: str\n            returned: always\n            sample: eastus\n        name:\n            description:\n                - Resource name.\n            type: str\n            returned: always\n            sample: myVM\n        properties:\n            description:\n                - Specifies the virtual machine\'s property.\n            type: complex\n            returned: always\n            contains:\n                diagnosticsProfile:\n                    description:\n                        - Specifies the boot diagnostic settings state.\n                    type: complex\n                    returned: always\n                    contains:\n                        bootDiagnostics:\n                            description:\n                                - A debugging feature, which to view Console Output and Screenshot to diagnose VM status.\n                            type: dict\n                            returned: always\n                            sample: {\n                                    "enabled": true,\n                                    "storageUri": "https://vxisurgdiag.blob.core.windows.net/"\n                                    }\n                hardwareProfile:\n                    description:\n                        - Specifies the hardware settings for the virtual machine.\n                    type: dict\n                    returned: always\n                    sample: {\n                            "vmSize": "Standard_D2s_v3"\n                            }\n                networkProfile:\n                    description:\n                        - Specifies the network interfaces of the virtual machine.\n                    type: complex\n                    returned: always\n                    contains:\n                        networkInterfaces:\n                            description:\n                                - Describes a network interface reference.\n                            type: list\n                            returned: always\n                            sample:\n                                - {\n                                  "id": "/subscriptions/xxxx...xxxx/resourceGroups/v-xisuRG/providers/Microsoft.Network/networkInterfaces/myvm441"\n                                  }\n                osProfile:\n                    description:\n                        - Specifies the operating system settings for the virtual machine.\n                    type: complex\n                    returned: always\n                    contains:\n                        adminUsername:\n                            description:\n                                - Specifies the name of the administrator account.\n                            type: str\n                            returned: always\n                            sample: azureuser\n                        allowExtensionOperations:\n                            description:\n                                - Specifies whether extension operations should be allowed on the virtual machine.\n                                - This may only be set to False when no extensions are present on the virtual machine.\n                            type: bool\n                            returned: always\n                            sample: true\n                        computerName:\n                            description:\n                                - Specifies the host OS name of the virtual machine.\n                            type: str\n                            returned: always\n                            sample: myVM\n                        requireGuestProvisionSignale:\n                            description:\n                                - Specifies the host require guest provision signal or not.\n                            type: bool\n                            returned: always\n                            sample: true\n                        secrets:\n                            description:\n                                - Specifies set of certificates that should be installed onto the virtual machine.\n                            type: list\n                            returned: always\n                            sample: []\n                        linuxConfiguration:\n                            description:\n                                - Specifies the Linux operating system settings on the virtual machine.\n                            type: dict\n                            returned: when OS type is Linux\n                            sample: {\n                                    "disablePasswordAuthentication": false,\n                                    "provisionVMAgent": true\n                                     }\n                provisioningState:\n                    description:\n                        - The provisioning state.\n                    type: str\n                    returned: always\n                    sample: Succeeded\n                vmID:\n                    description:\n                        - Specifies the VM unique ID which is a 128-bits identifier that is encoded and stored in all Azure laaS VMs SMBIOS.\n                        - It can be read using platform BIOS commands.\n                    type: str\n                    returned: always\n                    sample: "eb86d9bb-6725-4787-a487-2e497d5b340c"\n                storageProfile:\n                    description:\n                        - Specifies the storage account type for the managed disk.\n                    type: complex\n                    returned: always\n                    contains:\n                        dataDisks:\n                            description:\n                                - Specifies the parameters that are used to add a data disk to virtual machine.\n                            type: list\n                            returned: always\n                            sample:\n                                - {\n                                  "caching": "None",\n                                  "createOption": "Attach",\n                                  "diskSizeGB": 1023,\n                                  "lun": 2,\n                                  "managedDisk": {\n                                                "id": "/subscriptions/xxxx....xxxx/resourceGroups/V-XISURG/providers/Microsoft.Compute/disks/testdisk2",\n                                                 "storageAccountType": "StandardSSD_LRS"\n                                                },\n                                  "name": "testdisk2"\n                                   }\n                                - {\n                                  "caching": "None",\n                                  "createOption": "Attach",\n                                  "diskSizeGB": 1023,\n                                  "lun": 1,\n                                  "managedDisk": {\n                                                "id": "/subscriptions/xxxx...xxxx/resourceGroups/V-XISURG/providers/Microsoft.Compute/disks/testdisk3",\n                                                "storageAccountType": "StandardSSD_LRS"\n                                                },\n                                  "name": "testdisk3"\n                                  }\n\n                        imageReference:\n                            description:\n                                - Specifies information about the image to use.\n                            type: dict\n                            returned: always\n                            sample: {\n                                   "offer": "UbuntuServer",\n                                   "publisher": "Canonical",\n                                   "sku": "18.04-LTS",\n                                   "version": "latest"\n                                   }\n                        osDisk:\n                            description:\n                                - Specifies information about the operating system disk used by the virtual machine.\n                            type: dict\n                            returned: always\n                            sample: {\n                                   "caching": "ReadWrite",\n                                   "createOption": "FromImage",\n                                   "diskSizeGB": 30,\n                                   "managedDisk": {\n                                                  "id": "/subscriptions/xxx...xxxx/resourceGroups/v-xisuRG/providers/Microsoft.Compute/disks/myVM_disk1_xxx",\n                                                  "storageAccountType": "Premium_LRS"\n                                                   },\n                                   "name": "myVM_disk1_xxx",\n                                   "osType": "Linux"\n                                   }\n        type:\n            description:\n                - The type of identity used for the virtual machine.\n            type: str\n            returned: always\n            sample: "Microsoft.Compute/virtualMachines"\n'
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
from ansible.module_utils.azure_rm_common_rest import GenericRestClient
try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.service_client import ServiceClient
    from msrestazure.tools import resource_id, is_valid_resource_id
    import json
except ImportError:
    pass

class AzureRMResourceInfo(AzureRMModuleBase):

    def __init__(self):
        self.module_arg_spec = dict(url=dict(type='str'), provider=dict(type='str'), resource_group=dict(type='str'), resource_type=dict(type='str'), resource_name=dict(type='str'), subresource=dict(type='list', default=[]), api_version=dict(type='str'))
        self.results = dict(response=[])
        self.mgmt_client = None
        self.url = None
        self.api_version = None
        self.provider = None
        self.resource_group = None
        self.resource_type = None
        self.resource_name = None
        self.subresource = []
        super(AzureRMResourceInfo, self).__init__(self.module_arg_spec, supports_tags=False)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_resource_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_resource_facts' module has been renamed to 'azure_rm_resource_info'", version='2.13', collection_name='ansible.builtin')
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])
        self.mgmt_client = self.get_mgmt_svc_client(GenericRestClient, base_url=self._cloud_environment.endpoints.resource_manager)
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
        self.results['url'] = self.url
        query_parameters = {}
        query_parameters['api-version'] = self.api_version
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        skiptoken = None
        while True:
            if skiptoken:
                query_parameters['skiptoken'] = skiptoken
            response = self.mgmt_client.query(self.url, 'GET', query_parameters, header_parameters, None, [200, 404], 0, 0)
            try:
                response = json.loads(response.text)
                if isinstance(response, dict):
                    if response.get('value'):
                        self.results['response'] = self.results['response'] + response['value']
                        skiptoken = response.get('nextLink')
                    else:
                        self.results['response'] = self.results['response'] + [response]
            except Exception as e:
                self.fail('Failed to parse response: ' + str(e))
            if not skiptoken:
                break
        return self.results

def main():
    AzureRMResourceInfo()
if __name__ == '__main__':
    main()

def test_AzureRMResourceInfo_exec_module():
    ret = AzureRMResourceInfo().exec_module()