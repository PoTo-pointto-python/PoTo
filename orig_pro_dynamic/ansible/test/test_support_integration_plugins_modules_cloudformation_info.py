from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: cloudformation_info\nshort_description: Obtain information about an AWS CloudFormation stack\ndescription:\n  - Gets information about an AWS CloudFormation stack.\n  - This module was called C(cloudformation_facts) before Ansible 2.9, returning C(ansible_facts).\n    Note that the M(cloudformation_info) module no longer returns C(ansible_facts)!\nrequirements:\n  - boto3 >= 1.0.0\n  - python >= 2.6\nversion_added: "2.2"\nauthor:\n    - Justin Menga (@jmenga)\n    - Kevin Coming (@waffie1)\noptions:\n    stack_name:\n        description:\n          - The name or id of the CloudFormation stack. Gathers information on all stacks by default.\n        type: str\n    all_facts:\n        description:\n            - Get all stack information for the stack.\n        type: bool\n        default: false\n    stack_events:\n        description:\n            - Get stack events for the stack.\n        type: bool\n        default: false\n    stack_template:\n        description:\n            - Get stack template body for the stack.\n        type: bool\n        default: false\n    stack_resources:\n        description:\n            - Get stack resources for the stack.\n        type: bool\n        default: false\n    stack_policy:\n        description:\n            - Get stack policy for the stack.\n        type: bool\n        default: false\n    stack_change_sets:\n        description:\n            - Get stack change sets for the stack\n        type: bool\n        default: false\n        version_added: \'2.10\'\nextends_documentation_fragment:\n    - aws\n    - ec2\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Get summary information about a stack\n- cloudformation_info:\n    stack_name: my-cloudformation-stack\n  register: output\n\n- debug:\n    msg: "{{ output[\'cloudformation\'][\'my-cloudformation-stack\'] }}"\n\n# When the module is called as cloudformation_facts, return values are published\n# in ansible_facts[\'cloudformation\'][<stack_name>] and can be used as follows.\n# Note that this is deprecated and will stop working in Ansible 2.13.\n\n- cloudformation_facts:\n    stack_name: my-cloudformation-stack\n\n- debug:\n    msg: "{{ ansible_facts[\'cloudformation\'][\'my-cloudformation-stack\'] }}"\n\n# Get stack outputs, when you have the stack name available as a fact\n- set_fact:\n    stack_name: my-awesome-stack\n\n- cloudformation_info:\n    stack_name: "{{ stack_name }}"\n  register: my_stack\n\n- debug:\n    msg: "{{ my_stack.cloudformation[stack_name].stack_outputs }}"\n\n# Get all stack information about a stack\n- cloudformation_info:\n    stack_name: my-cloudformation-stack\n    all_facts: true\n\n# Get stack resource and stack policy information about a stack\n- cloudformation_info:\n    stack_name: my-cloudformation-stack\n    stack_resources: true\n    stack_policy: true\n\n# Fail if the stack doesn\'t exist\n- name: try to get facts about a stack but fail if it doesn\'t exist\n  cloudformation_info:\n    stack_name: nonexistent-stack\n    all_facts: yes\n  failed_when: cloudformation[\'nonexistent-stack\'] is undefined\n'
RETURN = '\nstack_description:\n    description: Summary facts about the stack\n    returned: if the stack exists\n    type: dict\nstack_outputs:\n    description: Dictionary of stack outputs keyed by the value of each output \'OutputKey\' parameter and corresponding value of each\n                 output \'OutputValue\' parameter\n    returned: if the stack exists\n    type: dict\n    sample:\n      ApplicationDatabaseName: dazvlpr01xj55a.ap-southeast-2.rds.amazonaws.com\nstack_parameters:\n    description: Dictionary of stack parameters keyed by the value of each parameter \'ParameterKey\' parameter and corresponding value of\n                 each parameter \'ParameterValue\' parameter\n    returned: if the stack exists\n    type: dict\n    sample:\n      DatabaseEngine: mysql\n      DatabasePassword: "***"\nstack_events:\n    description: All stack events for the stack\n    returned: only if all_facts or stack_events is true and the stack exists\n    type: list\nstack_policy:\n    description: Describes the stack policy for the stack\n    returned: only if all_facts or stack_policy is true and the stack exists\n    type: dict\nstack_template:\n    description: Describes the stack template for the stack\n    returned: only if all_facts or stack_template is true and the stack exists\n    type: dict\nstack_resource_list:\n    description: Describes stack resources for the stack\n    returned: only if all_facts or stack_resourses is true and the stack exists\n    type: list\nstack_resources:\n    description: Dictionary of stack resources keyed by the value of each resource \'LogicalResourceId\' parameter and corresponding value of each\n                 resource \'PhysicalResourceId\' parameter\n    returned: only if all_facts or stack_resourses is true and the stack exists\n    type: dict\n    sample:\n      AutoScalingGroup: "dev-someapp-AutoscalingGroup-1SKEXXBCAN0S7"\n      AutoScalingSecurityGroup: "sg-abcd1234"\n      ApplicationDatabase: "dazvlpr01xj55a"\nstack_change_sets:\n    description: A list of stack change sets.  Each item in the list represents the details of a specific changeset\n\n    returned: only if all_facts or stack_change_sets is true and the stack exists\n    type: list\n'
import json
import traceback
from functools import partial
from ansible.module_utils._text import to_native
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, AWSRetry, boto3_tag_list_to_ansible_dict
try:
    import botocore
except ImportError:
    pass

class CloudFormationServiceManager:
    """Handles CloudFormation Services"""

    def __init__(self, module):
        self.module = module
        self.client = module.client('cloudformation')

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def describe_stacks_with_backoff(self, **kwargs):
        paginator = self.client.get_paginator('describe_stacks')
        return paginator.paginate(**kwargs).build_full_result()['Stacks']

    def describe_stacks(self, stack_name=None):
        try:
            kwargs = {'StackName': stack_name} if stack_name else {}
            response = self.describe_stacks_with_backoff(**kwargs)
            if response is not None:
                return response
            self.module.fail_json(msg='Error describing stack(s) - an empty response was returned')
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            if 'does not exist' in e.response['Error']['Message']:
                return {}
            self.module.fail_json_aws(e, msg='Error describing stack ' + stack_name)

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def list_stack_resources_with_backoff(self, stack_name):
        paginator = self.client.get_paginator('list_stack_resources')
        return paginator.paginate(StackName=stack_name).build_full_result()['StackResourceSummaries']

    def list_stack_resources(self, stack_name):
        try:
            return self.list_stack_resources_with_backoff(stack_name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg='Error listing stack resources for stack ' + stack_name)

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def describe_stack_events_with_backoff(self, stack_name):
        paginator = self.client.get_paginator('describe_stack_events')
        return paginator.paginate(StackName=stack_name).build_full_result()['StackEvents']

    def describe_stack_events(self, stack_name):
        try:
            return self.describe_stack_events_with_backoff(stack_name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg='Error listing stack events for stack ' + stack_name)

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def list_stack_change_sets_with_backoff(self, stack_name):
        paginator = self.client.get_paginator('list_change_sets')
        return paginator.paginate(StackName=stack_name).build_full_result()['Summaries']

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def describe_stack_change_set_with_backoff(self, **kwargs):
        paginator = self.client.get_paginator('describe_change_set')
        return paginator.paginate(**kwargs).build_full_result()

    def describe_stack_change_sets(self, stack_name):
        changes = []
        try:
            change_sets = self.list_stack_change_sets_with_backoff(stack_name)
            for item in change_sets:
                changes.append(self.describe_stack_change_set_with_backoff(StackName=stack_name, ChangeSetName=item['ChangeSetName']))
            return changes
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg='Error describing stack change sets for stack ' + stack_name)

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def get_stack_policy_with_backoff(self, stack_name):
        return self.client.get_stack_policy(StackName=stack_name)

    def get_stack_policy(self, stack_name):
        try:
            response = self.get_stack_policy_with_backoff(stack_name)
            stack_policy = response.get('StackPolicyBody')
            if stack_policy:
                return json.loads(stack_policy)
            return dict()
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg='Error getting stack policy for stack ' + stack_name)

    @AWSRetry.exponential_backoff(retries=5, delay=5)
    def get_template_with_backoff(self, stack_name):
        return self.client.get_template(StackName=stack_name)

    def get_template(self, stack_name):
        try:
            response = self.get_template_with_backoff(stack_name)
            return response.get('TemplateBody')
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg='Error getting stack template for stack ' + stack_name)

def to_dict(items, key, value):
    """ Transforms a list of items to a Key/Value dictionary """
    if items:
        return dict(zip([i.get(key) for i in items], [i.get(value) for i in items]))
    else:
        return dict()

def main():
    argument_spec = dict(stack_name=dict(), all_facts=dict(required=False, default=False, type='bool'), stack_policy=dict(required=False, default=False, type='bool'), stack_events=dict(required=False, default=False, type='bool'), stack_resources=dict(required=False, default=False, type='bool'), stack_template=dict(required=False, default=False, type='bool'), stack_change_sets=dict(required=False, default=False, type='bool'))
    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    is_old_facts = module._name == 'cloudformation_facts'
    if is_old_facts:
        module.deprecate("The 'cloudformation_facts' module has been renamed to 'cloudformation_info', and the renamed one no longer returns ansible_facts", version='2.13', collection_name='ansible.builtin')
    service_mgr = CloudFormationServiceManager(module)
    if is_old_facts:
        result = {'ansible_facts': {'cloudformation': {}}}
    else:
        result = {'cloudformation': {}}
    for stack_description in service_mgr.describe_stacks(module.params.get('stack_name')):
        facts = {'stack_description': stack_description}
        stack_name = stack_description.get('StackName')
        if facts['stack_description']:
            facts['stack_outputs'] = to_dict(facts['stack_description'].get('Outputs'), 'OutputKey', 'OutputValue')
            facts['stack_parameters'] = to_dict(facts['stack_description'].get('Parameters'), 'ParameterKey', 'ParameterValue')
            facts['stack_tags'] = boto3_tag_list_to_ansible_dict(facts['stack_description'].get('Tags'))
        all_facts = module.params.get('all_facts')
        if all_facts or module.params.get('stack_resources'):
            facts['stack_resource_list'] = service_mgr.list_stack_resources(stack_name)
            facts['stack_resources'] = to_dict(facts.get('stack_resource_list'), 'LogicalResourceId', 'PhysicalResourceId')
        if all_facts or module.params.get('stack_template'):
            facts['stack_template'] = service_mgr.get_template(stack_name)
        if all_facts or module.params.get('stack_policy'):
            facts['stack_policy'] = service_mgr.get_stack_policy(stack_name)
        if all_facts or module.params.get('stack_events'):
            facts['stack_events'] = service_mgr.describe_stack_events(stack_name)
        if all_facts or module.params.get('stack_change_sets'):
            facts['stack_change_sets'] = service_mgr.describe_stack_change_sets(stack_name)
        if is_old_facts:
            result['ansible_facts']['cloudformation'][stack_name] = facts
        else:
            result['cloudformation'][stack_name] = camel_dict_to_snake_dict(facts, ignore_list=('stack_outputs', 'stack_parameters', 'stack_policy', 'stack_resources', 'stack_tags', 'stack_template'))
    module.exit_json(changed=False, **result)
if __name__ == '__main__':
    main()

def test_CloudFormationServiceManager_describe_stacks_with_backoff():
    ret = CloudFormationServiceManager().describe_stacks_with_backoff()

def test_CloudFormationServiceManager_describe_stacks():
    ret = CloudFormationServiceManager().describe_stacks()

def test_CloudFormationServiceManager_list_stack_resources_with_backoff():
    ret = CloudFormationServiceManager().list_stack_resources_with_backoff()

def test_CloudFormationServiceManager_list_stack_resources():
    ret = CloudFormationServiceManager().list_stack_resources()

def test_CloudFormationServiceManager_describe_stack_events_with_backoff():
    ret = CloudFormationServiceManager().describe_stack_events_with_backoff()

def test_CloudFormationServiceManager_describe_stack_events():
    ret = CloudFormationServiceManager().describe_stack_events()

def test_CloudFormationServiceManager_list_stack_change_sets_with_backoff():
    ret = CloudFormationServiceManager().list_stack_change_sets_with_backoff()

def test_CloudFormationServiceManager_describe_stack_change_set_with_backoff():
    ret = CloudFormationServiceManager().describe_stack_change_set_with_backoff()

def test_CloudFormationServiceManager_describe_stack_change_sets():
    ret = CloudFormationServiceManager().describe_stack_change_sets()

def test_CloudFormationServiceManager_get_stack_policy_with_backoff():
    ret = CloudFormationServiceManager().get_stack_policy_with_backoff()

def test_CloudFormationServiceManager_get_stack_policy():
    ret = CloudFormationServiceManager().get_stack_policy()

def test_CloudFormationServiceManager_get_template_with_backoff():
    ret = CloudFormationServiceManager().get_template_with_backoff()

def test_CloudFormationServiceManager_get_template():
    ret = CloudFormationServiceManager().get_template()