from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: cloudformation\nshort_description: Create or delete an AWS CloudFormation stack\ndescription:\n     - Launches or updates an AWS CloudFormation stack and waits for it complete.\nnotes:\n     - CloudFormation features change often, and this module tries to keep up. That means your botocore version should be fresh.\n       The version listed in the requirements is the oldest version that works with the module as a whole.\n       Some features may require recent versions, and we do not pinpoint a minimum version for each feature.\n       Instead of relying on the minimum version, keep botocore up to date. AWS is always releasing features and fixing bugs.\nversion_added: "1.1"\noptions:\n  stack_name:\n    description:\n      - Name of the CloudFormation stack.\n    required: true\n    type: str\n  disable_rollback:\n    description:\n      - If a stacks fails to form, rollback will remove the stack.\n    default: false\n    type: bool\n  on_create_failure:\n    description:\n      - Action to take upon failure of stack creation. Incompatible with the I(disable_rollback) option.\n    choices:\n      - DO_NOTHING\n      - ROLLBACK\n      - DELETE\n    version_added: "2.8"\n    type: str\n  create_timeout:\n    description:\n      - The amount of time (in minutes) that can pass before the stack status becomes CREATE_FAILED\n    version_added: "2.6"\n    type: int\n  template_parameters:\n    description:\n      - A list of hashes of all the template variables for the stack. The value can be a string or a dict.\n      - Dict can be used to set additional template parameter attributes like UsePreviousValue (see example).\n    default: {}\n    type: dict\n  state:\n    description:\n      - If I(state=present), stack will be created.\n      - If I(state=present) and if stack exists and template has changed, it will be updated.\n      - If I(state=absent), stack will be removed.\n    default: present\n    choices: [ present, absent ]\n    type: str\n  template:\n    description:\n      - The local path of the CloudFormation template.\n      - This must be the full path to the file, relative to the working directory. If using roles this may look\n        like C(roles/cloudformation/files/cloudformation-example.json).\n      - If I(state=present) and the stack does not exist yet, either I(template), I(template_body) or I(template_url)\n        must be specified (but only one of them).\n      - If I(state=present), the stack does exist, and neither I(template),\n        I(template_body) nor I(template_url) are specified, the previous template will be reused.\n    type: path\n  notification_arns:\n    description:\n      - A comma separated list of Simple Notification Service (SNS) topic ARNs to publish stack related events.\n    version_added: "2.0"\n    type: str\n  stack_policy:\n    description:\n      - The path of the CloudFormation stack policy. A policy cannot be removed once placed, but it can be modified.\n        for instance, allow all updates U(https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html#d0e9051)\n    version_added: "1.9"\n    type: str\n  tags:\n    description:\n      - Dictionary of tags to associate with stack and its resources during stack creation.\n      - Can be updated later, updating tags removes previous entries.\n    version_added: "1.4"\n    type: dict\n  template_url:\n    description:\n      - Location of file containing the template body. The URL must point to a template (max size 307,200 bytes) located in an\n        S3 bucket in the same region as the stack.\n      - If I(state=present) and the stack does not exist yet, either I(template), I(template_body) or I(template_url)\n        must be specified (but only one of them).\n      - If I(state=present), the stack does exist, and neither I(template), I(template_body) nor I(template_url) are specified,\n        the previous template will be reused.\n    version_added: "2.0"\n    type: str\n  create_changeset:\n    description:\n      - "If stack already exists create a changeset instead of directly applying changes.  See the AWS Change Sets docs\n        U(https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)."\n      - "WARNING: if the stack does not exist, it will be created without changeset. If I(state=absent), the stack will be\n        deleted immediately with no changeset."\n    type: bool\n    default: false\n    version_added: "2.4"\n  changeset_name:\n    description:\n      - Name given to the changeset when creating a changeset.\n      - Only used when I(create_changeset=true).\n      - By default a name prefixed with Ansible-STACKNAME is generated based on input parameters.\n        See the AWS Change Sets docs for more information\n        U(https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)\n    version_added: "2.4"\n    type: str\n  template_format:\n    description:\n    - This parameter is ignored since Ansible 2.3 and will be removed in Ansible 2.14.\n    - Templates are now passed raw to CloudFormation regardless of format.\n    version_added: "2.0"\n    type: str\n  role_arn:\n    description:\n    - The role that AWS CloudFormation assumes to create the stack. See the AWS CloudFormation Service Role\n      docs U(https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html)\n    version_added: "2.3"\n    type: str\n  termination_protection:\n    description:\n    - Enable or disable termination protection on the stack. Only works with botocore >= 1.7.18.\n    type: bool\n    version_added: "2.5"\n  template_body:\n    description:\n      - Template body. Use this to pass in the actual body of the CloudFormation template.\n      - If I(state=present) and the stack does not exist yet, either I(template), I(template_body) or I(template_url)\n        must be specified (but only one of them).\n      - If I(state=present), the stack does exist, and neither I(template), I(template_body) nor I(template_url)\n        are specified, the previous template will be reused.\n    version_added: "2.5"\n    type: str\n  events_limit:\n    description:\n    - Maximum number of CloudFormation events to fetch from a stack when creating or updating it.\n    default: 200\n    version_added: "2.7"\n    type: int\n  backoff_delay:\n    description:\n    - Number of seconds to wait for the next retry.\n    default: 3\n    version_added: "2.8"\n    type: int\n    required: False\n  backoff_max_delay:\n    description:\n    - Maximum amount of time to wait between retries.\n    default: 30\n    version_added: "2.8"\n    type: int\n    required: False\n  backoff_retries:\n    description:\n    - Number of times to retry operation.\n    - AWS API throttling mechanism fails CloudFormation module so we have to retry a couple of times.\n    default: 10\n    version_added: "2.8"\n    type: int\n    required: False\n  capabilities:\n    description:\n    - Specify capabilities that stack template contains.\n    - Valid values are C(CAPABILITY_IAM), C(CAPABILITY_NAMED_IAM) and C(CAPABILITY_AUTO_EXPAND).\n    type: list\n    elements: str\n    version_added: "2.8"\n    default: [ CAPABILITY_IAM, CAPABILITY_NAMED_IAM ]\n\nauthor: "James S. Martin (@jsmartin)"\nextends_documentation_fragment:\n- aws\n- ec2\nrequirements: [ boto3, botocore>=1.5.45 ]\n'
EXAMPLES = '\n- name: create a cloudformation stack\n  cloudformation:\n    stack_name: "ansible-cloudformation"\n    state: "present"\n    region: "us-east-1"\n    disable_rollback: true\n    template: "files/cloudformation-example.json"\n    template_parameters:\n      KeyName: "jmartin"\n      DiskType: "ephemeral"\n      InstanceType: "m1.small"\n      ClusterSize: 3\n    tags:\n      Stack: "ansible-cloudformation"\n\n# Basic role example\n- name: create a stack, specify role that cloudformation assumes\n  cloudformation:\n    stack_name: "ansible-cloudformation"\n    state: "present"\n    region: "us-east-1"\n    disable_rollback: true\n    template: "roles/cloudformation/files/cloudformation-example.json"\n    role_arn: \'arn:aws:iam::123456789012:role/cloudformation-iam-role\'\n\n- name: delete a stack\n  cloudformation:\n    stack_name: "ansible-cloudformation-old"\n    state: "absent"\n\n# Create a stack, pass in template from a URL, disable rollback if stack creation fails,\n# pass in some parameters to the template, provide tags for resources created\n- name: create a stack, pass in the template via an URL\n  cloudformation:\n    stack_name: "ansible-cloudformation"\n    state: present\n    region: us-east-1\n    disable_rollback: true\n    template_url: https://s3.amazonaws.com/my-bucket/cloudformation.template\n    template_parameters:\n      KeyName: jmartin\n      DiskType: ephemeral\n      InstanceType: m1.small\n      ClusterSize: 3\n    tags:\n      Stack: ansible-cloudformation\n\n# Create a stack, passing in template body using lookup of Jinja2 template, disable rollback if stack creation fails,\n# pass in some parameters to the template, provide tags for resources created\n- name: create a stack, pass in the template body via lookup template\n  cloudformation:\n    stack_name: "ansible-cloudformation"\n    state: present\n    region: us-east-1\n    disable_rollback: true\n    template_body: "{{ lookup(\'template\', \'cloudformation.j2\') }}"\n    template_parameters:\n      KeyName: jmartin\n      DiskType: ephemeral\n      InstanceType: m1.small\n      ClusterSize: 3\n    tags:\n      Stack: ansible-cloudformation\n\n# Pass a template parameter which uses CloudFormation\'s UsePreviousValue attribute\n# When use_previous_value is set to True, the given value will be ignored and\n# CloudFormation will use the value from a previously submitted template.\n# If use_previous_value is set to False (default) the given value is used.\n- cloudformation:\n    stack_name: "ansible-cloudformation"\n    state: "present"\n    region: "us-east-1"\n    template: "files/cloudformation-example.json"\n    template_parameters:\n      DBSnapshotIdentifier:\n        use_previous_value: True\n        value: arn:aws:rds:es-east-1:000000000000:snapshot:rds:my-db-snapshot\n      DBName:\n        use_previous_value: True\n    tags:\n      Stack: "ansible-cloudformation"\n\n# Enable termination protection on a stack.\n# If the stack already exists, this will update its termination protection\n- name: enable termination protection during stack creation\n  cloudformation:\n    stack_name: my_stack\n    state: present\n    template_url: https://s3.amazonaws.com/my-bucket/cloudformation.template\n    termination_protection: yes\n\n# Configure TimeoutInMinutes before the stack status becomes CREATE_FAILED\n# In this case, if disable_rollback is not set or is set to false, the stack will be rolled back.\n- name: enable termination protection during stack creation\n  cloudformation:\n    stack_name: my_stack\n    state: present\n    template_url: https://s3.amazonaws.com/my-bucket/cloudformation.template\n    create_timeout: 5\n\n# Configure rollback behaviour on the unsuccessful creation of a stack allowing\n# CloudFormation to clean up, or do nothing in the event of an unsuccessful\n# deployment\n# In this case, if on_create_failure is set to "DELETE", it will clean up the stack if\n# it fails to create\n- name: create stack which will delete on creation failure\n  cloudformation:\n    stack_name: my_stack\n    state: present\n    template_url: https://s3.amazonaws.com/my-bucket/cloudformation.template\n    on_create_failure: DELETE\n'
RETURN = '\nevents:\n  type: list\n  description: Most recent events in CloudFormation\'s event log. This may be from a previous run in some cases.\n  returned: always\n  sample: ["StackEvent AWS::CloudFormation::Stack stackname UPDATE_COMPLETE", "StackEvent AWS::CloudFormation::Stack stackname UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"]\nlog:\n  description: Debugging logs. Useful when modifying or finding an error.\n  returned: always\n  type: list\n  sample: ["updating stack"]\nchange_set_id:\n  description: The ID of the stack change set if one was created\n  returned:  I(state=present) and I(create_changeset=true)\n  type: str\n  sample: "arn:aws:cloudformation:us-east-1:012345678901:changeSet/Ansible-StackName-f4496805bd1b2be824d1e315c6884247ede41eb0"\nstack_resources:\n  description: AWS stack resources and their status. List of dictionaries, one dict per resource.\n  returned: state == present\n  type: list\n  sample: [\n          {\n              "last_updated_time": "2016-10-11T19:40:14.979000+00:00",\n              "logical_resource_id": "CFTestSg",\n              "physical_resource_id": "cloudformation2-CFTestSg-16UQ4CYQ57O9F",\n              "resource_type": "AWS::EC2::SecurityGroup",\n              "status": "UPDATE_COMPLETE",\n              "status_reason": null\n          }\n      ]\nstack_outputs:\n  type: dict\n  description: A key:value dictionary of all the stack outputs currently defined. If there are no stack outputs, it is an empty dictionary.\n  returned: state == present\n  sample: {"MySg": "AnsibleModuleTestYAML-CFTestSg-C8UVS567B6NS"}\n'
import json
import time
import uuid
import traceback
from hashlib import sha1
try:
    import boto3
    import botocore
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
from ansible.module_utils.ec2 import ansible_dict_to_boto3_tag_list, AWSRetry, boto3_conn, boto_exception, ec2_argument_spec, get_aws_connection_info
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

def get_stack_events(cfn, stack_name, events_limit, token_filter=None):
    """This event data was never correct, it worked as a side effect. So the v2.3 format is different."""
    ret = {'events': [], 'log': []}
    try:
        pg = cfn.get_paginator('describe_stack_events').paginate(StackName=stack_name, PaginationConfig={'MaxItems': events_limit})
        if token_filter is not None:
            events = list(pg.search("StackEvents[?ClientRequestToken == '{0}']".format(token_filter)))
        else:
            events = list(pg.search('StackEvents[*]'))
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as err:
        error_msg = boto_exception(err)
        if 'does not exist' in error_msg:
            ret['log'].append('Stack does not exist.')
            return ret
        ret['log'].append('Unknown error: ' + str(error_msg))
        return ret
    for e in events:
        eventline = 'StackEvent {ResourceType} {LogicalResourceId} {ResourceStatus}'.format(**e)
        ret['events'].append(eventline)
        if e['ResourceStatus'].endswith('FAILED'):
            failline = '{ResourceType} {LogicalResourceId} {ResourceStatus}: {ResourceStatusReason}'.format(**e)
            ret['log'].append(failline)
    return ret

def create_stack(module, stack_params, cfn, events_limit):
    if 'TemplateBody' not in stack_params and 'TemplateURL' not in stack_params:
        module.fail_json(msg="Either 'template', 'template_body' or 'template_url' is required when the stack does not exist.")
    if module.params.get('on_create_failure') is not None:
        stack_params['OnFailure'] = module.params['on_create_failure']
    else:
        stack_params['DisableRollback'] = module.params['disable_rollback']
    if module.params.get('create_timeout') is not None:
        stack_params['TimeoutInMinutes'] = module.params['create_timeout']
    if module.params.get('termination_protection') is not None:
        if boto_supports_termination_protection(cfn):
            stack_params['EnableTerminationProtection'] = bool(module.params.get('termination_protection'))
        else:
            module.fail_json(msg='termination_protection parameter requires botocore >= 1.7.18')
    try:
        response = cfn.create_stack(**stack_params)
        result = stack_operation(cfn, response['StackId'], 'CREATE', events_limit, stack_params.get('ClientRequestToken', None))
    except Exception as err:
        error_msg = boto_exception(err)
        module.fail_json(msg='Failed to create stack {0}: {1}.'.format(stack_params.get('StackName'), error_msg), exception=traceback.format_exc())
    if not result:
        module.fail_json(msg='empty result')
    return result

def list_changesets(cfn, stack_name):
    res = cfn.list_change_sets(StackName=stack_name)
    return [cs['ChangeSetName'] for cs in res['Summaries']]

def create_changeset(module, stack_params, cfn, events_limit):
    if 'TemplateBody' not in stack_params and 'TemplateURL' not in stack_params:
        module.fail_json(msg="Either 'template' or 'template_url' is required.")
    if module.params['changeset_name'] is not None:
        stack_params['ChangeSetName'] = module.params['changeset_name']
    stack_params.pop('ClientRequestToken', None)
    try:
        changeset_name = build_changeset_name(stack_params)
        stack_params['ChangeSetName'] = changeset_name
        pending_changesets = list_changesets(cfn, stack_params['StackName'])
        if changeset_name in pending_changesets:
            warning = 'WARNING: %d pending changeset(s) exist(s) for this stack!' % len(pending_changesets)
            result = dict(changed=False, output='ChangeSet %s already exists.' % changeset_name, warnings=[warning])
        else:
            cs = cfn.create_change_set(**stack_params)
            time_end = time.time() + 600
            while time.time() < time_end:
                try:
                    newcs = cfn.describe_change_set(ChangeSetName=cs['Id'])
                except botocore.exceptions.BotoCoreError as err:
                    error_msg = boto_exception(err)
                    module.fail_json(msg=error_msg)
                if newcs['Status'] == 'CREATE_PENDING' or newcs['Status'] == 'CREATE_IN_PROGRESS':
                    time.sleep(1)
                elif newcs['Status'] == 'FAILED' and "The submitted information didn't contain changes" in newcs['StatusReason']:
                    cfn.delete_change_set(ChangeSetName=cs['Id'])
                    result = dict(changed=False, output='The created Change Set did not contain any changes to this stack and was deleted.')
                    return result
                else:
                    break
                time.sleep(1)
            result = stack_operation(cfn, stack_params['StackName'], 'CREATE_CHANGESET', events_limit)
            result['change_set_id'] = cs['Id']
            result['warnings'] = ['Created changeset named %s for stack %s' % (changeset_name, stack_params['StackName']), 'You can execute it using: aws cloudformation execute-change-set --change-set-name %s' % cs['Id'], 'NOTE that dependencies on this stack might fail due to pending changes!']
    except Exception as err:
        error_msg = boto_exception(err)
        if 'No updates are to be performed.' in error_msg:
            result = dict(changed=False, output='Stack is already up-to-date.')
        else:
            module.fail_json(msg='Failed to create change set: {0}'.format(error_msg), exception=traceback.format_exc())
    if not result:
        module.fail_json(msg='empty result')
    return result

def update_stack(module, stack_params, cfn, events_limit):
    if 'TemplateBody' not in stack_params and 'TemplateURL' not in stack_params:
        stack_params['UsePreviousTemplate'] = True
    try:
        cfn.update_stack(**stack_params)
        result = stack_operation(cfn, stack_params['StackName'], 'UPDATE', events_limit, stack_params.get('ClientRequestToken', None))
    except Exception as err:
        error_msg = boto_exception(err)
        if 'No updates are to be performed.' in error_msg:
            result = dict(changed=False, output='Stack is already up-to-date.')
        else:
            module.fail_json(msg='Failed to update stack {0}: {1}'.format(stack_params.get('StackName'), error_msg), exception=traceback.format_exc())
    if not result:
        module.fail_json(msg='empty result')
    return result

def update_termination_protection(module, cfn, stack_name, desired_termination_protection_state):
    """updates termination protection of a stack"""
    if not boto_supports_termination_protection(cfn):
        module.fail_json(msg='termination_protection parameter requires botocore >= 1.7.18')
    stack = get_stack_facts(cfn, stack_name)
    if stack:
        if stack['EnableTerminationProtection'] is not desired_termination_protection_state:
            try:
                cfn.update_termination_protection(EnableTerminationProtection=desired_termination_protection_state, StackName=stack_name)
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg=boto_exception(e), exception=traceback.format_exc())

def boto_supports_termination_protection(cfn):
    """termination protection was added in botocore 1.7.18"""
    return hasattr(cfn, 'update_termination_protection')

def stack_operation(cfn, stack_name, operation, events_limit, op_token=None):
    """gets the status of a stack while it is created/updated/deleted"""
    existed = []
    while True:
        try:
            stack = get_stack_facts(cfn, stack_name)
            existed.append('yes')
        except Exception:
            if 'yes' in existed or operation == 'DELETE':
                ret = get_stack_events(cfn, stack_name, events_limit, op_token)
                ret.update({'changed': True, 'output': 'Stack Deleted'})
                return ret
            else:
                return {'changed': True, 'failed': True, 'output': 'Stack Not Found', 'exception': traceback.format_exc()}
        ret = get_stack_events(cfn, stack_name, events_limit, op_token)
        if not stack:
            if 'yes' in existed or operation == 'DELETE':
                ret = get_stack_events(cfn, stack_name, events_limit, op_token)
                ret.update({'changed': True, 'output': 'Stack Deleted'})
                return ret
            else:
                ret.update({'changed': False, 'failed': True, 'output': 'Stack not found.'})
                return ret
        elif stack['StackStatus'].endswith('ROLLBACK_COMPLETE') and operation != 'CREATE_CHANGESET':
            ret.update({'changed': True, 'failed': True, 'output': 'Problem with %s. Rollback complete' % operation})
            return ret
        elif stack['StackStatus'] == 'DELETE_COMPLETE' and operation == 'CREATE':
            ret.update({'changed': True, 'failed': True, 'output': 'Stack create failed. Delete complete.'})
            return ret
        elif stack['StackStatus'].endswith('_COMPLETE'):
            ret.update({'changed': True, 'output': 'Stack %s complete' % operation})
            return ret
        elif stack['StackStatus'].endswith('_ROLLBACK_FAILED'):
            ret.update({'changed': True, 'failed': True, 'output': 'Stack %s rollback failed' % operation})
            return ret
        elif stack['StackStatus'].endswith('_FAILED'):
            ret.update({'changed': True, 'failed': True, 'output': 'Stack %s failed' % operation})
            return ret
        else:
            time.sleep(5)
    return {'failed': True, 'output': 'Failed for unknown reasons.'}

def build_changeset_name(stack_params):
    if 'ChangeSetName' in stack_params:
        return stack_params['ChangeSetName']
    json_params = json.dumps(stack_params, sort_keys=True)
    return 'Ansible-{0}-{1}'.format(stack_params['StackName'], sha1(to_bytes(json_params, errors='surrogate_or_strict')).hexdigest())

def check_mode_changeset(module, stack_params, cfn):
    """Create a change set, describe it and delete it before returning check mode outputs."""
    stack_params['ChangeSetName'] = build_changeset_name(stack_params)
    stack_params.pop('ClientRequestToken', None)
    try:
        change_set = cfn.create_change_set(**stack_params)
        for i in range(60):
            description = cfn.describe_change_set(ChangeSetName=change_set['Id'])
            if description['Status'] in ('CREATE_COMPLETE', 'FAILED'):
                break
            time.sleep(5)
        else:
            module.fail_json(msg='Failed to create change set %s' % stack_params['ChangeSetName'])
        cfn.delete_change_set(ChangeSetName=change_set['Id'])
        reason = description.get('StatusReason')
        if description['Status'] == 'FAILED' and "didn't contain changes" in description['StatusReason']:
            return {'changed': False, 'msg': reason, 'meta': description['StatusReason']}
        return {'changed': True, 'msg': reason, 'meta': description['Changes']}
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as err:
        error_msg = boto_exception(err)
        module.fail_json(msg=error_msg, exception=traceback.format_exc())

def get_stack_facts(cfn, stack_name):
    try:
        stack_response = cfn.describe_stacks(StackName=stack_name)
        stack_info = stack_response['Stacks'][0]
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as err:
        error_msg = boto_exception(err)
        if 'does not exist' in error_msg:
            return None
        raise err
    if stack_response and stack_response.get('Stacks', None):
        stacks = stack_response['Stacks']
        if len(stacks):
            stack_info = stacks[0]
    return stack_info

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(stack_name=dict(required=True), template_parameters=dict(required=False, type='dict', default={}), state=dict(default='present', choices=['present', 'absent']), template=dict(default=None, required=False, type='path'), notification_arns=dict(default=None, required=False), stack_policy=dict(default=None, required=False), disable_rollback=dict(default=False, type='bool'), on_create_failure=dict(default=None, required=False, choices=['DO_NOTHING', 'ROLLBACK', 'DELETE']), create_timeout=dict(default=None, type='int'), template_url=dict(default=None, required=False), template_body=dict(default=None, required=False), template_format=dict(removed_in_version='2.14'), create_changeset=dict(default=False, type='bool'), changeset_name=dict(default=None, required=False), role_arn=dict(default=None, required=False), tags=dict(default=None, type='dict'), termination_protection=dict(default=None, type='bool'), events_limit=dict(default=200, type='int'), backoff_retries=dict(type='int', default=10, required=False), backoff_delay=dict(type='int', default=3, required=False), backoff_max_delay=dict(type='int', default=30, required=False), capabilities=dict(type='list', default=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'])))
    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=[['template_url', 'template', 'template_body'], ['disable_rollback', 'on_create_failure']], supports_check_mode=True)
    if not HAS_BOTO3:
        module.fail_json(msg='boto3 and botocore are required for this module')
    invalid_capabilities = []
    user_capabilities = module.params.get('capabilities')
    for user_cap in user_capabilities:
        if user_cap not in ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']:
            invalid_capabilities.append(user_cap)
    if invalid_capabilities:
        module.fail_json(msg='Specified capabilities are invalid : %r, please check documentation for valid capabilities' % invalid_capabilities)
    stack_params = {'Capabilities': user_capabilities, 'ClientRequestToken': to_native(uuid.uuid4())}
    state = module.params['state']
    stack_params['StackName'] = module.params['stack_name']
    if module.params['template'] is not None:
        with open(module.params['template'], 'r') as template_fh:
            stack_params['TemplateBody'] = template_fh.read()
    elif module.params['template_body'] is not None:
        stack_params['TemplateBody'] = module.params['template_body']
    elif module.params['template_url'] is not None:
        stack_params['TemplateURL'] = module.params['template_url']
    if module.params.get('notification_arns'):
        stack_params['NotificationARNs'] = module.params['notification_arns'].split(',')
    else:
        stack_params['NotificationARNs'] = []
    if module.params['stack_policy'] is not None and (not module.check_mode) and (not module.params['create_changeset']):
        with open(module.params['stack_policy'], 'r') as stack_policy_fh:
            stack_params['StackPolicyBody'] = stack_policy_fh.read()
    template_parameters = module.params['template_parameters']
    stack_params['Parameters'] = []
    for (k, v) in template_parameters.items():
        if isinstance(v, dict):
            param = dict(ParameterKey=k)
            if 'value' in v:
                param['ParameterValue'] = str(v['value'])
            if 'use_previous_value' in v and bool(v['use_previous_value']):
                param['UsePreviousValue'] = True
                param.pop('ParameterValue', None)
            stack_params['Parameters'].append(param)
        else:
            stack_params['Parameters'].append({'ParameterKey': k, 'ParameterValue': str(v)})
    if isinstance(module.params.get('tags'), dict):
        stack_params['Tags'] = ansible_dict_to_boto3_tag_list(module.params['tags'])
    if module.params.get('role_arn'):
        stack_params['RoleARN'] = module.params['role_arn']
    result = {}
    try:
        (region, ec2_url, aws_connect_kwargs) = get_aws_connection_info(module, boto3=True)
        cfn = boto3_conn(module, conn_type='client', resource='cloudformation', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except botocore.exceptions.NoCredentialsError as e:
        module.fail_json(msg=boto_exception(e))
    backoff_wrapper = AWSRetry.jittered_backoff(retries=module.params.get('backoff_retries'), delay=module.params.get('backoff_delay'), max_delay=module.params.get('backoff_max_delay'))
    cfn.describe_stack_events = backoff_wrapper(cfn.describe_stack_events)
    cfn.create_stack = backoff_wrapper(cfn.create_stack)
    cfn.list_change_sets = backoff_wrapper(cfn.list_change_sets)
    cfn.create_change_set = backoff_wrapper(cfn.create_change_set)
    cfn.update_stack = backoff_wrapper(cfn.update_stack)
    cfn.describe_stacks = backoff_wrapper(cfn.describe_stacks)
    cfn.list_stack_resources = backoff_wrapper(cfn.list_stack_resources)
    cfn.delete_stack = backoff_wrapper(cfn.delete_stack)
    if boto_supports_termination_protection(cfn):
        cfn.update_termination_protection = backoff_wrapper(cfn.update_termination_protection)
    stack_info = get_stack_facts(cfn, stack_params['StackName'])
    if module.check_mode:
        if state == 'absent' and stack_info:
            module.exit_json(changed=True, msg='Stack would be deleted', meta=[])
        elif state == 'absent' and (not stack_info):
            module.exit_json(changed=False, msg="Stack doesn't exist", meta=[])
        elif state == 'present' and (not stack_info):
            module.exit_json(changed=True, msg='New stack would be created', meta=[])
        else:
            module.exit_json(**check_mode_changeset(module, stack_params, cfn))
    if state == 'present':
        if not stack_info:
            result = create_stack(module, stack_params, cfn, module.params.get('events_limit'))
        elif module.params.get('create_changeset'):
            result = create_changeset(module, stack_params, cfn, module.params.get('events_limit'))
        else:
            if module.params.get('termination_protection') is not None:
                update_termination_protection(module, cfn, stack_params['StackName'], bool(module.params.get('termination_protection')))
            result = update_stack(module, stack_params, cfn, module.params.get('events_limit'))
        stack = get_stack_facts(cfn, stack_params['StackName'])
        if stack is not None:
            if result.get('stack_outputs') is None:
                result['stack_outputs'] = {}
            for output in stack.get('Outputs', []):
                result['stack_outputs'][output['OutputKey']] = output['OutputValue']
            stack_resources = []
            reslist = cfn.list_stack_resources(StackName=stack_params['StackName'])
            for res in reslist.get('StackResourceSummaries', []):
                stack_resources.append({'logical_resource_id': res['LogicalResourceId'], 'physical_resource_id': res.get('PhysicalResourceId', ''), 'resource_type': res['ResourceType'], 'last_updated_time': res['LastUpdatedTimestamp'], 'status': res['ResourceStatus'], 'status_reason': res.get('ResourceStatusReason')})
            result['stack_resources'] = stack_resources
    elif state == 'absent':
        try:
            stack = get_stack_facts(cfn, stack_params['StackName'])
            if not stack:
                result = {'changed': False, 'output': 'Stack not found.'}
            else:
                if stack_params.get('RoleARN') is None:
                    cfn.delete_stack(StackName=stack_params['StackName'])
                else:
                    cfn.delete_stack(StackName=stack_params['StackName'], RoleARN=stack_params['RoleARN'])
                result = stack_operation(cfn, stack_params['StackName'], 'DELETE', module.params.get('events_limit'), stack_params.get('ClientRequestToken', None))
        except Exception as err:
            module.fail_json(msg=boto_exception(err), exception=traceback.format_exc())
    module.exit_json(**result)
if __name__ == '__main__':
    main()