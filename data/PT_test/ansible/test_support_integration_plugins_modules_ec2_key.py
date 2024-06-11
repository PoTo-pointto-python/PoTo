from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: ec2_key\nversion_added: "1.5"\nshort_description: create or delete an ec2 key pair\ndescription:\n    - create or delete an ec2 key pair.\noptions:\n  name:\n    description:\n      - Name of the key pair.\n    required: true\n    type: str\n  key_material:\n    description:\n      - Public key material.\n    required: false\n    type: str\n  force:\n    description:\n      - Force overwrite of already existing key pair if key has changed.\n    required: false\n    default: true\n    type: bool\n    version_added: "2.3"\n  state:\n    description:\n      - create or delete keypair\n    required: false\n    choices: [ present, absent ]\n    default: \'present\'\n    type: str\n  wait:\n    description:\n      - This option has no effect since version 2.5 and will be removed in 2.14.\n    version_added: "1.6"\n    type: bool\n  wait_timeout:\n    description:\n      - This option has no effect since version 2.5 and will be removed in 2.14.\n    version_added: "1.6"\n    type: int\n    required: false\n\nextends_documentation_fragment:\n  - aws\n  - ec2\nrequirements: [ boto3 ]\nauthor:\n  - "Vincent Viallet (@zbal)"\n  - "Prasad Katti (@prasadkatti)"\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n- name: create a new ec2 key pair, returns generated private key\n  ec2_key:\n    name: my_keypair\n\n- name: create key pair using provided key_material\n  ec2_key:\n    name: my_keypair\n    key_material: \'ssh-rsa AAAAxyz...== me@example.com\'\n\n- name: create key pair using key_material obtained using \'file\' lookup plugin\n  ec2_key:\n    name: my_keypair\n    key_material: "{{ lookup(\'file\', \'/path/to/public_key/id_rsa.pub\') }}"\n\n# try creating a key pair with the name of an already existing keypair\n# but don\'t overwrite it even if the key is different (force=false)\n- name: try creating a key pair with name of an already existing keypair\n  ec2_key:\n    name: my_existing_keypair\n    key_material: \'ssh-rsa AAAAxyz...== me@example.com\'\n    force: false\n\n- name: remove key pair by name\n  ec2_key:\n    name: my_keypair\n    state: absent\n'
RETURN = "\nchanged:\n  description: whether a keypair was created/deleted\n  returned: always\n  type: bool\n  sample: true\nmsg:\n  description: short message describing the action taken\n  returned: always\n  type: str\n  sample: key pair created\nkey:\n  description: details of the keypair (this is set to null when state is absent)\n  returned: always\n  type: complex\n  contains:\n    fingerprint:\n      description: fingerprint of the key\n      returned: when state is present\n      type: str\n      sample: 'b0:22:49:61:d9:44:9d:0c:7e:ac:8a:32:93:21:6c:e8:fb:59:62:43'\n    name:\n      description: name of the keypair\n      returned: when state is present\n      type: str\n      sample: my_keypair\n    private_key:\n      description: private key of a newly created keypair\n      returned: when a new keypair is created by AWS (key_material is not provided)\n      type: str\n      sample: '-----BEGIN RSA PRIVATE KEY-----\n        MIIEowIBAAKC...\n        -----END RSA PRIVATE KEY-----'\n"
import uuid
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils._text import to_bytes
try:
    from botocore.exceptions import ClientError
except ImportError:
    pass

def extract_key_data(key):
    data = {'name': key['KeyName'], 'fingerprint': key['KeyFingerprint']}
    if 'KeyMaterial' in key:
        data['private_key'] = key['KeyMaterial']
    return data

def get_key_fingerprint(module, ec2_client, key_material):
    """
    EC2's fingerprints are non-trivial to generate, so push this key
    to a temporary name and make ec2 calculate the fingerprint for us.
    http://blog.jbrowne.com/?p=23
    https://forums.aws.amazon.com/thread.jspa?messageID=352828
    """
    name_in_use = True
    while name_in_use:
        random_name = 'ansible-' + str(uuid.uuid4())
        name_in_use = find_key_pair(module, ec2_client, random_name)
    temp_key = import_key_pair(module, ec2_client, random_name, key_material)
    delete_key_pair(module, ec2_client, random_name, finish_task=False)
    return temp_key['KeyFingerprint']

def find_key_pair(module, ec2_client, name):
    try:
        key = ec2_client.describe_key_pairs(KeyNames=[name])['KeyPairs'][0]
    except ClientError as err:
        if err.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            return None
        module.fail_json_aws(err, msg='error finding keypair')
    except IndexError:
        key = None
    return key

def create_key_pair(module, ec2_client, name, key_material, force):
    key = find_key_pair(module, ec2_client, name)
    if key:
        if key_material and force:
            if not module.check_mode:
                new_fingerprint = get_key_fingerprint(module, ec2_client, key_material)
                if key['KeyFingerprint'] != new_fingerprint:
                    delete_key_pair(module, ec2_client, name, finish_task=False)
                    key = import_key_pair(module, ec2_client, name, key_material)
                    key_data = extract_key_data(key)
                    module.exit_json(changed=True, key=key_data, msg='key pair updated')
            else:
                module.exit_json(changed=True, key=extract_key_data(key), msg='key pair updated')
        key_data = extract_key_data(key)
        module.exit_json(changed=False, key=key_data, msg='key pair already exists')
    else:
        key_data = None
        if not module.check_mode:
            if key_material:
                key = import_key_pair(module, ec2_client, name, key_material)
            else:
                try:
                    key = ec2_client.create_key_pair(KeyName=name)
                except ClientError as err:
                    module.fail_json_aws(err, msg='error creating key')
            key_data = extract_key_data(key)
        module.exit_json(changed=True, key=key_data, msg='key pair created')

def import_key_pair(module, ec2_client, name, key_material):
    try:
        key = ec2_client.import_key_pair(KeyName=name, PublicKeyMaterial=to_bytes(key_material))
    except ClientError as err:
        module.fail_json_aws(err, msg='error importing key')
    return key

def delete_key_pair(module, ec2_client, name, finish_task=True):
    key = find_key_pair(module, ec2_client, name)
    if key:
        if not module.check_mode:
            try:
                ec2_client.delete_key_pair(KeyName=name)
            except ClientError as err:
                module.fail_json_aws(err, msg='error deleting key')
        if not finish_task:
            return
        module.exit_json(changed=True, key=None, msg='key deleted')
    module.exit_json(key=None, msg='key did not exist')

def main():
    argument_spec = dict(name=dict(required=True), key_material=dict(), force=dict(type='bool', default=True), state=dict(default='present', choices=['present', 'absent']), wait=dict(type='bool', removed_in_version='2.14'), wait_timeout=dict(type='int', removed_in_version='2.14'))
    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    ec2_client = module.client('ec2')
    name = module.params['name']
    state = module.params.get('state')
    key_material = module.params.get('key_material')
    force = module.params.get('force')
    if state == 'absent':
        delete_key_pair(module, ec2_client, name)
    elif state == 'present':
        create_key_pair(module, ec2_client, name, key_material, force)
if __name__ == '__main__':
    main()