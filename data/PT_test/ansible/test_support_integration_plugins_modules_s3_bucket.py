from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: s3_bucket\nshort_description: Manage S3 buckets in AWS, DigitalOcean, Ceph, Walrus, FakeS3 and StorageGRID\ndescription:\n    - Manage S3 buckets in AWS, DigitalOcean, Ceph, Walrus, FakeS3 and StorageGRID\nversion_added: "2.0"\nrequirements: [ boto3 ]\nauthor: "Rob White (@wimnat)"\noptions:\n  force:\n    description:\n      - When trying to delete a bucket, delete all keys (including versions and delete markers)\n        in the bucket first (an s3 bucket must be empty for a successful deletion)\n    type: bool\n    default: \'no\'\n  name:\n    description:\n      - Name of the s3 bucket\n    required: true\n    type: str\n  policy:\n    description:\n      - The JSON policy as a string.\n    type: json\n  s3_url:\n    description:\n      - S3 URL endpoint for usage with DigitalOcean, Ceph, Eucalyptus and fakes3 etc.\n      - Assumes AWS if not specified.\n      - For Walrus, use FQDN of the endpoint without scheme nor path.\n    aliases: [ S3_URL ]\n    type: str\n  ceph:\n    description:\n      - Enable API compatibility with Ceph. It takes into account the S3 API subset working\n        with Ceph in order to provide the same module behaviour where possible.\n    type: bool\n    version_added: "2.2"\n  requester_pays:\n    description:\n      - With Requester Pays buckets, the requester instead of the bucket owner pays the cost\n        of the request and the data download from the bucket.\n    type: bool\n    default: False\n  state:\n    description:\n      - Create or remove the s3 bucket\n    required: false\n    default: present\n    choices: [ \'present\', \'absent\' ]\n    type: str\n  tags:\n    description:\n      - tags dict to apply to bucket\n    type: dict\n  purge_tags:\n    description:\n      - whether to remove tags that aren\'t present in the C(tags) parameter\n    type: bool\n    default: True\n    version_added: "2.9"\n  versioning:\n    description:\n      - Whether versioning is enabled or disabled (note that once versioning is enabled, it can only be suspended)\n    type: bool\n  encryption:\n    description:\n      - Describes the default server-side encryption to apply to new objects in the bucket.\n        In order to remove the server-side encryption, the encryption needs to be set to \'none\' explicitly.\n    choices: [ \'none\', \'AES256\', \'aws:kms\' ]\n    version_added: "2.9"\n    type: str\n  encryption_key_id:\n    description: KMS master key ID to use for the default encryption. This parameter is allowed if encryption is aws:kms. If\n                 not specified then it will default to the AWS provided KMS key.\n    version_added: "2.9"\n    type: str\nextends_documentation_fragment:\n    - aws\n    - ec2\nnotes:\n    - If C(requestPayment), C(policy), C(tagging) or C(versioning)\n      operations/API aren\'t implemented by the endpoint, module doesn\'t fail\n      if each parameter satisfies the following condition.\n      I(requester_pays) is C(False), I(policy), I(tags), and I(versioning) are C(None).\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Create a simple s3 bucket\n- s3_bucket:\n    name: mys3bucket\n    state: present\n\n# Create a simple s3 bucket on Ceph Rados Gateway\n- s3_bucket:\n    name: mys3bucket\n    s3_url: http://your-ceph-rados-gateway-server.xxx\n    ceph: true\n\n# Remove an s3 bucket and any keys it contains\n- s3_bucket:\n    name: mys3bucket\n    state: absent\n    force: yes\n\n# Create a bucket, add a policy from a file, enable requester pays, enable versioning and tag\n- s3_bucket:\n    name: mys3bucket\n    policy: "{{ lookup(\'file\',\'policy.json\') }}"\n    requester_pays: yes\n    versioning: yes\n    tags:\n      example: tag1\n      another: tag2\n\n# Create a simple DigitalOcean Spaces bucket using their provided regional endpoint\n- s3_bucket:\n    name: mydobucket\n    s3_url: \'https://nyc3.digitaloceanspaces.com\'\n\n# Create a bucket with AES256 encryption\n- s3_bucket:\n    name: mys3bucket\n    state: present\n    encryption: "AES256"\n\n# Create a bucket with aws:kms encryption, KMS key\n- s3_bucket:\n    name: mys3bucket\n    state: present\n    encryption: "aws:kms"\n    encryption_key_id: "arn:aws:kms:us-east-1:1234/5678example"\n\n# Create a bucket with aws:kms encryption, default key\n- s3_bucket:\n    name: mys3bucket\n    state: present\n    encryption: "aws:kms"\n'
import json
import os
import time
from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.module_utils.six import string_types
from ansible.module_utils.basic import to_text
from ansible.module_utils.aws.core import AnsibleAWSModule, is_boto3_error_code
from ansible.module_utils.ec2 import compare_policies, ec2_argument_spec, boto3_tag_list_to_ansible_dict, ansible_dict_to_boto3_tag_list
from ansible.module_utils.ec2 import get_aws_connection_info, boto3_conn, AWSRetry
try:
    from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError, WaiterError
except ImportError:
    pass

def create_or_update_bucket(s3_client, module, location):
    policy = module.params.get('policy')
    name = module.params.get('name')
    requester_pays = module.params.get('requester_pays')
    tags = module.params.get('tags')
    purge_tags = module.params.get('purge_tags')
    versioning = module.params.get('versioning')
    encryption = module.params.get('encryption')
    encryption_key_id = module.params.get('encryption_key_id')
    changed = False
    result = {}
    try:
        bucket_is_present = bucket_exists(s3_client, name)
    except EndpointConnectionError as e:
        module.fail_json_aws(e, msg='Invalid endpoint provided: %s' % to_text(e))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to check bucket presence')
    if not bucket_is_present:
        try:
            bucket_changed = create_bucket(s3_client, name, location)
            s3_client.get_waiter('bucket_exists').wait(Bucket=name)
            changed = changed or bucket_changed
        except WaiterError as e:
            module.fail_json_aws(e, msg='An error occurred waiting for the bucket to become available')
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg='Failed while creating bucket')
    try:
        versioning_status = get_bucket_versioning(s3_client, name)
    except BotoCoreError as exp:
        module.fail_json_aws(exp, msg='Failed to get bucket versioning')
    except ClientError as exp:
        if exp.response['Error']['Code'] != 'NotImplemented' or versioning is not None:
            module.fail_json_aws(exp, msg='Failed to get bucket versioning')
    else:
        if versioning is not None:
            required_versioning = None
            if versioning and versioning_status.get('Status') != 'Enabled':
                required_versioning = 'Enabled'
            elif not versioning and versioning_status.get('Status') == 'Enabled':
                required_versioning = 'Suspended'
            if required_versioning:
                try:
                    put_bucket_versioning(s3_client, name, required_versioning)
                    changed = True
                except (BotoCoreError, ClientError) as e:
                    module.fail_json_aws(e, msg='Failed to update bucket versioning')
                versioning_status = wait_versioning_is_applied(module, s3_client, name, required_versioning)
        result['versioning'] = {'Versioning': versioning_status.get('Status', 'Disabled'), 'MfaDelete': versioning_status.get('MFADelete', 'Disabled')}
    try:
        requester_pays_status = get_bucket_request_payment(s3_client, name)
    except BotoCoreError as exp:
        module.fail_json_aws(exp, msg='Failed to get bucket request payment')
    except ClientError as exp:
        if exp.response['Error']['Code'] not in ('NotImplemented', 'XNotImplemented') or requester_pays:
            module.fail_json_aws(exp, msg='Failed to get bucket request payment')
    else:
        if requester_pays:
            payer = 'Requester' if requester_pays else 'BucketOwner'
            if requester_pays_status != payer:
                put_bucket_request_payment(s3_client, name, payer)
                requester_pays_status = wait_payer_is_applied(module, s3_client, name, payer, should_fail=False)
                if requester_pays_status is None:
                    put_bucket_request_payment(s3_client, name, payer)
                    requester_pays_status = wait_payer_is_applied(module, s3_client, name, payer, should_fail=True)
                changed = True
        result['requester_pays'] = requester_pays
    try:
        current_policy = get_bucket_policy(s3_client, name)
    except BotoCoreError as exp:
        module.fail_json_aws(exp, msg='Failed to get bucket policy')
    except ClientError as exp:
        if exp.response['Error']['Code'] != 'NotImplemented' or policy is not None:
            module.fail_json_aws(exp, msg='Failed to get bucket policy')
    else:
        if policy is not None:
            if isinstance(policy, string_types):
                policy = json.loads(policy)
            if not policy and current_policy:
                try:
                    delete_bucket_policy(s3_client, name)
                except (BotoCoreError, ClientError) as e:
                    module.fail_json_aws(e, msg='Failed to delete bucket policy')
                current_policy = wait_policy_is_applied(module, s3_client, name, policy)
                changed = True
            elif compare_policies(current_policy, policy):
                try:
                    put_bucket_policy(s3_client, name, policy)
                except (BotoCoreError, ClientError) as e:
                    module.fail_json_aws(e, msg='Failed to update bucket policy')
                current_policy = wait_policy_is_applied(module, s3_client, name, policy, should_fail=False)
                if current_policy is None:
                    put_bucket_policy(s3_client, name, policy)
                    current_policy = wait_policy_is_applied(module, s3_client, name, policy, should_fail=True)
                changed = True
        result['policy'] = current_policy
    try:
        current_tags_dict = get_current_bucket_tags_dict(s3_client, name)
    except BotoCoreError as exp:
        module.fail_json_aws(exp, msg='Failed to get bucket tags')
    except ClientError as exp:
        if exp.response['Error']['Code'] not in ('NotImplemented', 'XNotImplemented') or tags is not None:
            module.fail_json_aws(exp, msg='Failed to get bucket tags')
    else:
        if tags is not None:
            tags = dict(((to_text(k), to_text(v)) for (k, v) in tags.items()))
            if not purge_tags:
                current_copy = current_tags_dict.copy()
                current_copy.update(tags)
                tags = current_copy
            if current_tags_dict != tags:
                if tags:
                    try:
                        put_bucket_tagging(s3_client, name, tags)
                    except (BotoCoreError, ClientError) as e:
                        module.fail_json_aws(e, msg='Failed to update bucket tags')
                elif purge_tags:
                    try:
                        delete_bucket_tagging(s3_client, name)
                    except (BotoCoreError, ClientError) as e:
                        module.fail_json_aws(e, msg='Failed to delete bucket tags')
                current_tags_dict = wait_tags_are_applied(module, s3_client, name, tags)
                changed = True
        result['tags'] = current_tags_dict
    if hasattr(s3_client, 'get_bucket_encryption'):
        try:
            current_encryption = get_bucket_encryption(s3_client, name)
        except (ClientError, BotoCoreError) as e:
            module.fail_json_aws(e, msg='Failed to get bucket encryption')
    elif encryption is not None:
        module.fail_json(msg='Using bucket encryption requires botocore version >= 1.7.41')
    if encryption is not None:
        current_encryption_algorithm = current_encryption.get('SSEAlgorithm') if current_encryption else None
        current_encryption_key = current_encryption.get('KMSMasterKeyID') if current_encryption else None
        if encryption == 'none' and current_encryption_algorithm is not None:
            try:
                delete_bucket_encryption(s3_client, name)
            except (BotoCoreError, ClientError) as e:
                module.fail_json_aws(e, msg='Failed to delete bucket encryption')
            current_encryption = wait_encryption_is_applied(module, s3_client, name, None)
            changed = True
        elif encryption != 'none' and encryption != current_encryption_algorithm or (encryption == 'aws:kms' and current_encryption_key != encryption_key_id):
            expected_encryption = {'SSEAlgorithm': encryption}
            if encryption == 'aws:kms' and encryption_key_id is not None:
                expected_encryption.update({'KMSMasterKeyID': encryption_key_id})
            try:
                put_bucket_encryption(s3_client, name, expected_encryption)
            except (BotoCoreError, ClientError) as e:
                module.fail_json_aws(e, msg='Failed to set bucket encryption')
            current_encryption = wait_encryption_is_applied(module, s3_client, name, expected_encryption)
            changed = True
        result['encryption'] = current_encryption
    module.exit_json(changed=changed, name=name, **result)

def bucket_exists(s3_client, bucket_name):
    all_buckets = s3_client.list_buckets(Bucket=bucket_name)['Buckets']
    return any((bucket['Name'] == bucket_name for bucket in all_buckets))

@AWSRetry.exponential_backoff(max_delay=120)
def create_bucket(s3_client, bucket_name, location):
    try:
        configuration = {}
        if location not in ('us-east-1', None):
            configuration['LocationConstraint'] = location
        if len(configuration) > 0:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=configuration)
        else:
            s3_client.create_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            return False
        else:
            raise e

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def put_bucket_tagging(s3_client, bucket_name, tags):
    s3_client.put_bucket_tagging(Bucket=bucket_name, Tagging={'TagSet': ansible_dict_to_boto3_tag_list(tags)})

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def put_bucket_policy(s3_client, bucket_name, policy):
    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def delete_bucket_policy(s3_client, bucket_name):
    s3_client.delete_bucket_policy(Bucket=bucket_name)

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def get_bucket_policy(s3_client, bucket_name):
    try:
        current_policy = json.loads(s3_client.get_bucket_policy(Bucket=bucket_name).get('Policy'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            current_policy = None
        else:
            raise e
    return current_policy

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def put_bucket_request_payment(s3_client, bucket_name, payer):
    s3_client.put_bucket_request_payment(Bucket=bucket_name, RequestPaymentConfiguration={'Payer': payer})

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def get_bucket_request_payment(s3_client, bucket_name):
    return s3_client.get_bucket_request_payment(Bucket=bucket_name).get('Payer')

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def get_bucket_versioning(s3_client, bucket_name):
    return s3_client.get_bucket_versioning(Bucket=bucket_name)

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def put_bucket_versioning(s3_client, bucket_name, required_versioning):
    s3_client.put_bucket_versioning(Bucket=bucket_name, VersioningConfiguration={'Status': required_versioning})

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def get_bucket_encryption(s3_client, bucket_name):
    try:
        result = s3_client.get_bucket_encryption(Bucket=bucket_name)
        return result.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])[0].get('ApplyServerSideEncryptionByDefault')
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            return None
        else:
            raise e
    except (IndexError, KeyError):
        return None

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def put_bucket_encryption(s3_client, bucket_name, encryption):
    server_side_encryption_configuration = {'Rules': [{'ApplyServerSideEncryptionByDefault': encryption}]}
    s3_client.put_bucket_encryption(Bucket=bucket_name, ServerSideEncryptionConfiguration=server_side_encryption_configuration)

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def delete_bucket_tagging(s3_client, bucket_name):
    s3_client.delete_bucket_tagging(Bucket=bucket_name)

@AWSRetry.exponential_backoff(max_delay=120, catch_extra_error_codes=['NoSuchBucket'])
def delete_bucket_encryption(s3_client, bucket_name):
    s3_client.delete_bucket_encryption(Bucket=bucket_name)

@AWSRetry.exponential_backoff(max_delay=120)
def delete_bucket(s3_client, bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            pass
        else:
            raise e

def wait_policy_is_applied(module, s3_client, bucket_name, expected_policy, should_fail=True):
    for dummy in range(0, 12):
        try:
            current_policy = get_bucket_policy(s3_client, bucket_name)
        except (ClientError, BotoCoreError) as e:
            module.fail_json_aws(e, msg='Failed to get bucket policy')
        if compare_policies(current_policy, expected_policy):
            time.sleep(5)
        else:
            return current_policy
    if should_fail:
        module.fail_json(msg='Bucket policy failed to apply in the expected time')
    else:
        return None

def wait_payer_is_applied(module, s3_client, bucket_name, expected_payer, should_fail=True):
    for dummy in range(0, 12):
        try:
            requester_pays_status = get_bucket_request_payment(s3_client, bucket_name)
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg='Failed to get bucket request payment')
        if requester_pays_status != expected_payer:
            time.sleep(5)
        else:
            return requester_pays_status
    if should_fail:
        module.fail_json(msg='Bucket request payment failed to apply in the expected time')
    else:
        return None

def wait_encryption_is_applied(module, s3_client, bucket_name, expected_encryption):
    for dummy in range(0, 12):
        try:
            encryption = get_bucket_encryption(s3_client, bucket_name)
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg='Failed to get updated encryption for bucket')
        if encryption != expected_encryption:
            time.sleep(5)
        else:
            return encryption
    module.fail_json(msg='Bucket encryption failed to apply in the expected time')

def wait_versioning_is_applied(module, s3_client, bucket_name, required_versioning):
    for dummy in range(0, 24):
        try:
            versioning_status = get_bucket_versioning(s3_client, bucket_name)
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg='Failed to get updated versioning for bucket')
        if versioning_status.get('Status') != required_versioning:
            time.sleep(8)
        else:
            return versioning_status
    module.fail_json(msg='Bucket versioning failed to apply in the expected time')

def wait_tags_are_applied(module, s3_client, bucket_name, expected_tags_dict):
    for dummy in range(0, 12):
        try:
            current_tags_dict = get_current_bucket_tags_dict(s3_client, bucket_name)
        except (ClientError, BotoCoreError) as e:
            module.fail_json_aws(e, msg='Failed to get bucket policy')
        if current_tags_dict != expected_tags_dict:
            time.sleep(5)
        else:
            return current_tags_dict
    module.fail_json(msg='Bucket tags failed to apply in the expected time')

def get_current_bucket_tags_dict(s3_client, bucket_name):
    try:
        current_tags = s3_client.get_bucket_tagging(Bucket=bucket_name).get('TagSet')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchTagSet':
            return {}
        raise e
    return boto3_tag_list_to_ansible_dict(current_tags)

def paginated_list(s3_client, **pagination_params):
    pg = s3_client.get_paginator('list_objects_v2')
    for page in pg.paginate(**pagination_params):
        yield [data['Key'] for data in page.get('Contents', [])]

def paginated_versions_list(s3_client, **pagination_params):
    try:
        pg = s3_client.get_paginator('list_object_versions')
        for page in pg.paginate(**pagination_params):
            yield [(data['Key'], data['VersionId']) for data in page.get('Versions', []) + page.get('DeleteMarkers', [])]
    except is_boto3_error_code('NoSuchBucket'):
        yield []

def destroy_bucket(s3_client, module):
    force = module.params.get('force')
    name = module.params.get('name')
    try:
        bucket_is_present = bucket_exists(s3_client, name)
    except EndpointConnectionError as e:
        module.fail_json_aws(e, msg='Invalid endpoint provided: %s' % to_text(e))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to check bucket presence')
    if not bucket_is_present:
        module.exit_json(changed=False)
    if force:
        try:
            for key_version_pairs in paginated_versions_list(s3_client, Bucket=name):
                formatted_keys = [{'Key': key, 'VersionId': version} for (key, version) in key_version_pairs]
                for fk in formatted_keys:
                    if not fk.get('VersionId'):
                        fk.pop('VersionId')
                if formatted_keys:
                    resp = s3_client.delete_objects(Bucket=name, Delete={'Objects': formatted_keys})
                    if resp.get('Errors'):
                        module.fail_json(msg='Could not empty bucket before deleting. Could not delete objects: {0}'.format(', '.join([k['Key'] for k in resp['Errors']])), errors=resp['Errors'], response=resp)
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg='Failed while deleting bucket')
    try:
        delete_bucket(s3_client, name)
        s3_client.get_waiter('bucket_not_exists').wait(Bucket=name, WaiterConfig=dict(Delay=5, MaxAttempts=60))
    except WaiterError as e:
        module.fail_json_aws(e, msg='An error occurred waiting for the bucket to be deleted.')
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to delete bucket')
    module.exit_json(changed=True)

def is_fakes3(s3_url):
    """ Return True if s3_url has scheme fakes3:// """
    if s3_url is not None:
        return urlparse(s3_url).scheme in ('fakes3', 'fakes3s')
    else:
        return False

def get_s3_client(module, aws_connect_kwargs, location, ceph, s3_url):
    if s3_url and ceph:
        ceph = urlparse(s3_url)
        params = dict(module=module, conn_type='client', resource='s3', use_ssl=ceph.scheme == 'https', region=location, endpoint=s3_url, **aws_connect_kwargs)
    elif is_fakes3(s3_url):
        fakes3 = urlparse(s3_url)
        port = fakes3.port
        if fakes3.scheme == 'fakes3s':
            protocol = 'https'
            if port is None:
                port = 443
        else:
            protocol = 'http'
            if port is None:
                port = 80
        params = dict(module=module, conn_type='client', resource='s3', region=location, endpoint='%s://%s:%s' % (protocol, fakes3.hostname, to_text(port)), use_ssl=fakes3.scheme == 'fakes3s', **aws_connect_kwargs)
    else:
        params = dict(module=module, conn_type='client', resource='s3', region=location, endpoint=s3_url, **aws_connect_kwargs)
    return boto3_conn(**params)

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(force=dict(default=False, type='bool'), policy=dict(type='json'), name=dict(required=True), requester_pays=dict(default=False, type='bool'), s3_url=dict(aliases=['S3_URL']), state=dict(default='present', choices=['present', 'absent']), tags=dict(type='dict'), purge_tags=dict(type='bool', default=True), versioning=dict(type='bool'), ceph=dict(default=False, type='bool'), encryption=dict(choices=['none', 'AES256', 'aws:kms']), encryption_key_id=dict()))
    module = AnsibleAWSModule(argument_spec=argument_spec)
    (region, ec2_url, aws_connect_kwargs) = get_aws_connection_info(module, boto3=True)
    if region in ('us-east-1', '', None):
        location = 'us-east-1'
    else:
        location = region
    s3_url = module.params.get('s3_url')
    ceph = module.params.get('ceph')
    if not s3_url and 'S3_URL' in os.environ:
        s3_url = os.environ['S3_URL']
    if ceph and (not s3_url):
        module.fail_json(msg='ceph flavour requires s3_url')
    if s3_url:
        for key in ['validate_certs', 'security_token', 'profile_name']:
            aws_connect_kwargs.pop(key, None)
    s3_client = get_s3_client(module, aws_connect_kwargs, location, ceph, s3_url)
    if s3_client is None:
        module.fail_json(msg='Unknown error, failed to create s3 connection, no information from boto.')
    state = module.params.get('state')
    encryption = module.params.get('encryption')
    encryption_key_id = module.params.get('encryption_key_id')
    if encryption_key_id is not None and encryption is None:
        module.fail_json(msg='You must specify encryption parameter along with encryption_key_id.')
    elif encryption_key_id is not None and encryption != 'aws:kms':
        module.fail_json(msg="Only 'aws:kms' is a valid option for encryption parameter when you specify encryption_key_id.")
    if state == 'present':
        create_or_update_bucket(s3_client, module, location)
    elif state == 'absent':
        destroy_bucket(s3_client, module)
if __name__ == '__main__':
    main()