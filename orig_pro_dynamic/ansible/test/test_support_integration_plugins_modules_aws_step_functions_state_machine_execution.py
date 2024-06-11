from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: aws_step_functions_state_machine_execution\n\nshort_description: Start or stop execution of an AWS Step Functions state machine.\n\nversion_added: "2.10"\n\ndescription:\n    - Start or stop execution of a state machine in AWS Step Functions.\n\noptions:\n    action:\n        description: Desired action (start or stop) for a state machine execution.\n        default: start\n        choices: [ start, stop ]\n        type: str\n    name:\n        description: Name of the execution.\n        type: str\n    execution_input:\n        description: The JSON input data for the execution.\n        type: json\n        default: {}\n    state_machine_arn:\n        description: The ARN of the state machine that will be executed.\n        type: str\n    execution_arn:\n        description: The ARN of the execution you wish to stop.\n        type: str\n    cause:\n        description: A detailed explanation of the cause for stopping the execution.\n        type: str\n        default: \'\'\n    error:\n        description: The error code of the failure to pass in when stopping the execution.\n        type: str\n        default: \'\'\n\nextends_documentation_fragment:\n    - aws\n    - ec2\n\nauthor:\n    - Prasad Katti (@prasadkatti)\n'
EXAMPLES = '\n- name: Start an execution of a state machine\n  aws_step_functions_state_machine_execution:\n    name: an_execution_name\n    execution_input: \'{ "IsHelloWorldExample": true }\'\n    state_machine_arn: "arn:aws:states:us-west-2:682285639423:stateMachine:HelloWorldStateMachine"\n\n- name: Stop an execution of a state machine\n  aws_step_functions_state_machine_execution:\n    action: stop\n    execution_arn: "arn:aws:states:us-west-2:682285639423:execution:HelloWorldStateMachineCopy:a1e8e2b5-5dfe-d40e-d9e3-6201061047c8"\n    cause: "cause of task failure"\n    error: "error code of the failure"\n'
RETURN = '\nexecution_arn:\n    description: ARN of the AWS Step Functions state machine execution.\n    type: str\n    returned: if action == start and changed == True\n    sample: "arn:aws:states:us-west-2:682285639423:execution:HelloWorldStateMachineCopy:a1e8e2b5-5dfe-d40e-d9e3-6201061047c8"\nstart_date:\n    description: The date the execution is started.\n    type: str\n    returned: if action == start and changed == True\n    sample: "2019-11-02T22:39:49.071000-07:00"\nstop_date:\n    description: The date the execution is stopped.\n    type: str\n    returned: if action == stop\n    sample: "2019-11-02T22:39:49.071000-07:00"\n'
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict
try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass

def start_execution(module, sfn_client):
    """
    start_execution uses execution name to determine if a previous execution already exists.
    If an execution by the provided name exists, call client.start_execution will not be called.
    """
    state_machine_arn = module.params.get('state_machine_arn')
    name = module.params.get('name')
    execution_input = module.params.get('execution_input')
    try:
        page_iterators = sfn_client.get_paginator('list_executions').paginate(stateMachineArn=state_machine_arn)
        for execution in page_iterators.build_full_result()['executions']:
            if name == execution['name']:
                check_mode(module, msg='State machine execution already exists.', changed=False)
                module.exit_json(changed=False)
        check_mode(module, msg='State machine execution would be started.', changed=True)
        res_execution = sfn_client.start_execution(stateMachineArn=state_machine_arn, name=name, input=execution_input)
    except (ClientError, BotoCoreError) as e:
        if e.response['Error']['Code'] == 'ExecutionAlreadyExists':
            module.exit_json(changed=False)
        module.fail_json_aws(e, msg='Failed to start execution.')
    module.exit_json(changed=True, **camel_dict_to_snake_dict(res_execution))

def stop_execution(module, sfn_client):
    cause = module.params.get('cause')
    error = module.params.get('error')
    execution_arn = module.params.get('execution_arn')
    try:
        execution_status = sfn_client.describe_execution(executionArn=execution_arn)['status']
        if execution_status != 'RUNNING':
            check_mode(module, msg='State machine execution is not running.', changed=False)
            module.exit_json(changed=False)
        check_mode(module, msg='State machine execution would be stopped.', changed=True)
        res = sfn_client.stop_execution(executionArn=execution_arn, cause=cause, error=error)
    except (ClientError, BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to stop execution.')
    module.exit_json(changed=True, **camel_dict_to_snake_dict(res))

def check_mode(module, msg='', changed=False):
    if module.check_mode:
        module.exit_json(changed=changed, output=msg)

def main():
    module_args = dict(action=dict(choices=['start', 'stop'], default='start'), name=dict(type='str'), execution_input=dict(type='json', default={}), state_machine_arn=dict(type='str'), cause=dict(type='str', default=''), error=dict(type='str', default=''), execution_arn=dict(type='str'))
    module = AnsibleAWSModule(argument_spec=module_args, required_if=[('action', 'start', ['name', 'state_machine_arn']), ('action', 'stop', ['execution_arn'])], supports_check_mode=True)
    sfn_client = module.client('stepfunctions')
    action = module.params.get('action')
    if action == 'start':
        start_execution(module, sfn_client)
    else:
        stop_execution(module, sfn_client)
if __name__ == '__main__':
    main()