from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: sts_assume_role\nshort_description: Assume a role using AWS Security Token Service and obtain temporary credentials\ndescription:\n    - Assume a role using AWS Security Token Service and obtain temporary credentials.\nversion_added: "2.0"\nauthor:\n    - Boris Ekelchik (@bekelchik)\n    - Marek Piatek (@piontas)\noptions:\n  role_arn:\n    description:\n      - The Amazon Resource Name (ARN) of the role that the caller is\n        assuming U(https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html#Identifiers_ARNs).\n    required: true\n    type: str\n  role_session_name:\n    description:\n      - Name of the role\'s session - will be used by CloudTrail.\n    required: true\n    type: str\n  policy:\n    description:\n      - Supplemental policy to use in addition to assumed role\'s policies.\n    type: str\n  duration_seconds:\n    description:\n      - The duration, in seconds, of the role session. The value can range from 900 seconds (15 minutes) to 43200 seconds (12 hours).\n      - The max depends on the IAM role\'s sessions duration setting.\n      - By default, the value is set to 3600 seconds.\n    type: int\n  external_id:\n    description:\n      - A unique identifier that is used by third parties to assume a role in their customers\' accounts.\n    type: str\n  mfa_serial_number:\n    description:\n      - The identification number of the MFA device that is associated with the user who is making the AssumeRole call.\n    type: str\n  mfa_token:\n    description:\n      - The value provided by the MFA device, if the trust policy of the role being assumed requires MFA.\n    type: str\nnotes:\n  - In order to use the assumed role in a following playbook task you must pass the access_key, access_secret and access_token.\nextends_documentation_fragment:\n    - aws\n    - ec2\nrequirements:\n    - boto3\n    - botocore\n    - python >= 2.6\n'
RETURN = '\nsts_creds:\n    description: The temporary security credentials, which include an access key ID, a secret access key, and a security (or session) token\n    returned: always\n    type: dict\n    sample:\n      access_key: XXXXXXXXXXXXXXXXXXXX\n      expiration: 2017-11-11T11:11:11+00:00\n      secret_key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n      session_token: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nsts_user:\n    description: The Amazon Resource Name (ARN) and the assumed role ID\n    returned: always\n    type: dict\n    sample:\n      assumed_role_id: arn:aws:sts::123456789012:assumed-role/demo/Bob\n      arn: ARO123EXAMPLE123:Bob\nchanged:\n    description: True if obtaining the credentials succeeds\n    type: bool\n    returned: always\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Assume an existing role (more details: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)\n- sts_assume_role:\n    role_arn: "arn:aws:iam::123456789012:role/someRole"\n    role_session_name: "someRoleSession"\n  register: assumed_role\n\n# Use the assumed role above to tag an instance in account 123456789012\n- ec2_tag:\n    aws_access_key: "{{ assumed_role.sts_creds.access_key }}"\n    aws_secret_key: "{{ assumed_role.sts_creds.secret_key }}"\n    security_token: "{{ assumed_role.sts_creds.session_token }}"\n    resource: i-xyzxyz01\n    state: present\n    tags:\n      MyNewTag: value\n\n'
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import camel_dict_to_snake_dict
try:
    from botocore.exceptions import ClientError, ParamValidationError
except ImportError:
    pass

def _parse_response(response):
    credentials = response.get('Credentials', {})
    user = response.get('AssumedRoleUser', {})
    sts_cred = {'access_key': credentials.get('AccessKeyId'), 'secret_key': credentials.get('SecretAccessKey'), 'session_token': credentials.get('SessionToken'), 'expiration': credentials.get('Expiration')}
    sts_user = camel_dict_to_snake_dict(user)
    return (sts_cred, sts_user)

def assume_role_policy(connection, module):
    params = {'RoleArn': module.params.get('role_arn'), 'RoleSessionName': module.params.get('role_session_name'), 'Policy': module.params.get('policy'), 'DurationSeconds': module.params.get('duration_seconds'), 'ExternalId': module.params.get('external_id'), 'SerialNumber': module.params.get('mfa_serial_number'), 'TokenCode': module.params.get('mfa_token')}
    changed = False
    kwargs = dict(((k, v) for (k, v) in params.items() if v is not None))
    try:
        response = connection.assume_role(**kwargs)
        changed = True
    except (ClientError, ParamValidationError) as e:
        module.fail_json_aws(e)
    (sts_cred, sts_user) = _parse_response(response)
    module.exit_json(changed=changed, sts_creds=sts_cred, sts_user=sts_user)

def main():
    argument_spec = dict(role_arn=dict(required=True), role_session_name=dict(required=True), duration_seconds=dict(required=False, default=None, type='int'), external_id=dict(required=False, default=None), policy=dict(required=False, default=None), mfa_serial_number=dict(required=False, default=None), mfa_token=dict(required=False, default=None))
    module = AnsibleAWSModule(argument_spec=argument_spec)
    connection = module.client('sts')
    assume_role_policy(connection, module)
if __name__ == '__main__':
    main()