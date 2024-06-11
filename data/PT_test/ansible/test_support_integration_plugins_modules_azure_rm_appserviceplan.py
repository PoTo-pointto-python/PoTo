from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: azure_rm_appserviceplan\nversion_added: "2.7"\nshort_description: Manage App Service Plan\ndescription:\n    - Create, update and delete instance of App Service Plan.\n\noptions:\n    resource_group:\n        description:\n            - Name of the resource group to which the resource belongs.\n        required: True\n\n    name:\n        description:\n            - Unique name of the app service plan to create or update.\n        required: True\n\n    location:\n        description:\n            - Resource location. If not set, location from the resource group will be used as default.\n\n    sku:\n        description:\n            - The pricing tiers, e.g., C(F1), C(D1), C(B1), C(B2), C(B3), C(S1), C(P1), C(P1V2) etc.\n            - Please see U(https://azure.microsoft.com/en-us/pricing/details/app-service/plans/) for more detail.\n            - For Linux app service plan, please see U(https://azure.microsoft.com/en-us/pricing/details/app-service/linux/) for more detail.\n    is_linux:\n        description:\n            - Describe whether to host webapp on Linux worker.\n        type: bool\n        default: false\n\n    number_of_workers:\n        description:\n            - Describe number of workers to be allocated.\n\n    state:\n      description:\n          - Assert the state of the app service plan.\n          - Use C(present) to create or update an app service plan and C(absent) to delete it.\n      default: present\n      choices:\n          - absent\n          - present\n\nextends_documentation_fragment:\n    - azure\n    - azure_tags\n\nauthor:\n    - Yunge Zhu (@yungezz)\n\n'
EXAMPLES = '\n    - name: Create a windows app service plan\n      azure_rm_appserviceplan:\n        resource_group: myResourceGroup\n        name: myAppPlan\n        location: eastus\n        sku: S1\n\n    - name: Create a linux app service plan\n      azure_rm_appserviceplan:\n        resource_group: myResourceGroup\n        name: myAppPlan\n        location: eastus\n        sku: S1\n        is_linux: true\n        number_of_workers: 1\n\n    - name: update sku of existing windows app service plan\n      azure_rm_appserviceplan:\n        resource_group: myResourceGroup\n        name: myAppPlan\n        location: eastus\n        sku: S2\n'
RETURN = '\nazure_appserviceplan:\n    description: Facts about the current state of the app service plan.\n    returned: always\n    type: dict\n    sample: {\n            "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/serverfarms/myAppPlan"\n    }\n'
import time
from ansible.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.polling import LROPoller
    from msrestazure.azure_operation import AzureOperationPoller
    from msrest.serialization import Model
    from azure.mgmt.web.models import app_service_plan, AppServicePlan, SkuDescription
except ImportError:
    pass

def _normalize_sku(sku):
    if sku is None:
        return sku
    sku = sku.upper()
    if sku == 'FREE':
        return 'F1'
    elif sku == 'SHARED':
        return 'D1'
    return sku

def get_sku_name(tier):
    tier = tier.upper()
    if tier == 'F1' or tier == 'FREE':
        return 'FREE'
    elif tier == 'D1' or tier == 'SHARED':
        return 'SHARED'
    elif tier in ['B1', 'B2', 'B3', 'BASIC']:
        return 'BASIC'
    elif tier in ['S1', 'S2', 'S3']:
        return 'STANDARD'
    elif tier in ['P1', 'P2', 'P3']:
        return 'PREMIUM'
    elif tier in ['P1V2', 'P2V2', 'P3V2']:
        return 'PREMIUMV2'
    else:
        return None

def appserviceplan_to_dict(plan):
    return dict(id=plan.id, name=plan.name, kind=plan.kind, location=plan.location, reserved=plan.reserved, is_linux=plan.reserved, provisioning_state=plan.provisioning_state, status=plan.status, target_worker_count=plan.target_worker_count, sku=dict(name=plan.sku.name, size=plan.sku.size, tier=plan.sku.tier, family=plan.sku.family, capacity=plan.sku.capacity), resource_group=plan.resource_group, number_of_sites=plan.number_of_sites, tags=plan.tags if plan.tags else None)

class AzureRMAppServicePlans(AzureRMModuleBase):
    """Configuration class for an Azure RM App Service Plan resource"""

    def __init__(self):
        self.module_arg_spec = dict(resource_group=dict(type='str', required=True), name=dict(type='str', required=True), location=dict(type='str'), sku=dict(type='str'), is_linux=dict(type='bool', default=False), number_of_workers=dict(type='str'), state=dict(type='str', default='present', choices=['present', 'absent']))
        self.resource_group = None
        self.name = None
        self.location = None
        self.sku = None
        self.is_linux = None
        self.number_of_workers = 1
        self.tags = None
        self.results = dict(changed=False, ansible_facts=dict(azure_appserviceplan=None))
        self.state = None
        super(AzureRMAppServicePlans, self).__init__(derived_arg_spec=self.module_arg_spec, supports_check_mode=True, supports_tags=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""
        for key in list(self.module_arg_spec.keys()) + ['tags']:
            if kwargs[key]:
                setattr(self, key, kwargs[key])
        old_response = None
        response = None
        to_be_updated = False
        resource_group = self.get_resource_group(self.resource_group)
        if not self.location:
            self.location = resource_group.location
        old_response = self.get_plan()
        if not old_response:
            self.log("App Service plan doesn't exist")
            if self.state == 'present':
                to_be_updated = True
                if not self.sku:
                    self.fail('Please specify sku in plan when creation')
        else:
            self.log('App Service Plan already exists')
            if self.state == 'present':
                self.log('Result: {0}'.format(old_response))
                (update_tags, newtags) = self.update_tags(old_response.get('tags', dict()))
                if update_tags:
                    to_be_updated = True
                    self.tags = newtags
                if self.sku and _normalize_sku(self.sku) != old_response['sku']['size']:
                    to_be_updated = True
                if self.number_of_workers and int(self.number_of_workers) != old_response['sku']['capacity']:
                    to_be_updated = True
                if self.is_linux and self.is_linux != old_response['reserved']:
                    self.fail('Operation not allowed: cannot update reserved of app service plan.')
        if old_response:
            self.results['id'] = old_response['id']
        if to_be_updated:
            self.log('Need to Create/Update app service plan')
            self.results['changed'] = True
            if self.check_mode:
                return self.results
            response = self.create_or_update_plan()
            self.results['id'] = response['id']
        if self.state == 'absent' and old_response:
            self.log('Delete app service plan')
            self.results['changed'] = True
            if self.check_mode:
                return self.results
            self.delete_plan()
            self.log('App service plan instance deleted')
        return self.results

    def get_plan(self):
        """
        Gets app service plan
        :return: deserialized app service plan dictionary
        """
        self.log('Get App Service Plan {0}'.format(self.name))
        try:
            response = self.web_client.app_service_plans.get(self.resource_group, self.name)
            if response:
                self.log('Response : {0}'.format(response))
                self.log('App Service Plan : {0} found'.format(response.name))
                return appserviceplan_to_dict(response)
        except CloudError as ex:
            self.log("Didn't find app service plan {0} in resource group {1}".format(self.name, self.resource_group))
        return False

    def create_or_update_plan(self):
        """
        Creates app service plan
        :return: deserialized app service plan dictionary
        """
        self.log('Create App Service Plan {0}'.format(self.name))
        try:
            sku = _normalize_sku(self.sku)
            sku_def = SkuDescription(tier=get_sku_name(sku), name=sku, capacity=self.number_of_workers)
            plan_def = AppServicePlan(location=self.location, app_service_plan_name=self.name, sku=sku_def, reserved=self.is_linux, tags=self.tags if self.tags else None)
            response = self.web_client.app_service_plans.create_or_update(self.resource_group, self.name, plan_def)
            if isinstance(response, LROPoller) or isinstance(response, AzureOperationPoller):
                response = self.get_poller_result(response)
            self.log('Response : {0}'.format(response))
            return appserviceplan_to_dict(response)
        except CloudError as ex:
            self.fail('Failed to create app service plan {0} in resource group {1}: {2}'.format(self.name, self.resource_group, str(ex)))

    def delete_plan(self):
        """
        Deletes specified App service plan in the specified subscription and resource group.

        :return: True
        """
        self.log('Deleting the App service plan {0}'.format(self.name))
        try:
            response = self.web_client.app_service_plans.delete(resource_group_name=self.resource_group, name=self.name)
        except CloudError as e:
            self.log('Error attempting to delete App service plan.')
            self.fail('Error deleting the App service plan : {0}'.format(str(e)))
        return True

def main():
    """Main execution"""
    AzureRMAppServicePlans()
if __name__ == '__main__':
    main()

def test_AzureRMAppServicePlans_exec_module():
    ret = AzureRMAppServicePlans().exec_module()

def test_AzureRMAppServicePlans_get_plan():
    ret = AzureRMAppServicePlans().get_plan()

def test_AzureRMAppServicePlans_create_or_update_plan():
    ret = AzureRMAppServicePlans().create_or_update_plan()

def test_AzureRMAppServicePlans_delete_plan():
    ret = AzureRMAppServicePlans().delete_plan()