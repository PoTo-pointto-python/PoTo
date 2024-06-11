from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: ec2_vpc_subnet\nshort_description: Manage subnets in AWS virtual private clouds\ndescription:\n    - Manage subnets in AWS virtual private clouds.\nversion_added: "2.0"\nauthor:\n- Robert Estelle (@erydo)\n- Brad Davidson (@brandond)\nrequirements: [ boto3 ]\noptions:\n  az:\n    description:\n      - "The availability zone for the subnet."\n    type: str\n  cidr:\n    description:\n      - "The CIDR block for the subnet. E.g. 192.0.2.0/24."\n    type: str\n    required: true\n  ipv6_cidr:\n    description:\n      - "The IPv6 CIDR block for the subnet. The VPC must have a /56 block assigned and this value must be a valid IPv6 /64 that falls in the VPC range."\n      - "Required if I(assign_instances_ipv6=true)"\n    version_added: "2.5"\n    type: str\n  tags:\n    description:\n      - "A dict of tags to apply to the subnet. Any tags currently applied to the subnet and not present here will be removed."\n    aliases: [ \'resource_tags\' ]\n    type: dict\n  state:\n    description:\n      - "Create or remove the subnet."\n    default: present\n    choices: [ \'present\', \'absent\' ]\n    type: str\n  vpc_id:\n    description:\n      - "VPC ID of the VPC in which to create or delete the subnet."\n    required: true\n    type: str\n  map_public:\n    description:\n      - "Specify C(yes) to indicate that instances launched into the subnet should be assigned public IP address by default."\n    type: bool\n    default: \'no\'\n    version_added: "2.4"\n  assign_instances_ipv6:\n    description:\n      - "Specify C(yes) to indicate that instances launched into the subnet should be automatically assigned an IPv6 address."\n    type: bool\n    default: false\n    version_added: "2.5"\n  wait:\n    description:\n      - "When I(wait=true) and I(state=present), module will wait for subnet to be in available state before continuing."\n    type: bool\n    default: true\n    version_added: "2.5"\n  wait_timeout:\n    description:\n      - "Number of seconds to wait for subnet to become available I(wait=True)."\n    default: 300\n    version_added: "2.5"\n    type: int\n  purge_tags:\n    description:\n      - Whether or not to remove tags that do not appear in the I(tags) list.\n    type: bool\n    default: true\n    version_added: "2.5"\nextends_documentation_fragment:\n    - aws\n    - ec2\n'
EXAMPLES = "\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n- name: Create subnet for database servers\n  ec2_vpc_subnet:\n    state: present\n    vpc_id: vpc-123456\n    cidr: 10.0.1.16/28\n    tags:\n      Name: Database Subnet\n  register: database_subnet\n\n- name: Remove subnet for database servers\n  ec2_vpc_subnet:\n    state: absent\n    vpc_id: vpc-123456\n    cidr: 10.0.1.16/28\n\n- name: Create subnet with IPv6 block assigned\n  ec2_vpc_subnet:\n    state: present\n    vpc_id: vpc-123456\n    cidr: 10.1.100.0/24\n    ipv6_cidr: 2001:db8:0:102::/64\n\n- name: Remove IPv6 block assigned to subnet\n  ec2_vpc_subnet:\n    state: present\n    vpc_id: vpc-123456\n    cidr: 10.1.100.0/24\n    ipv6_cidr: ''\n"
RETURN = '\nsubnet:\n    description: Dictionary of subnet values\n    returned: I(state=present)\n    type: complex\n    contains:\n        id:\n            description: Subnet resource id\n            returned: I(state=present)\n            type: str\n            sample: subnet-b883b2c4\n        cidr_block:\n            description: The IPv4 CIDR of the Subnet\n            returned: I(state=present)\n            type: str\n            sample: "10.0.0.0/16"\n        ipv6_cidr_block:\n            description: The IPv6 CIDR block actively associated with the Subnet\n            returned: I(state=present)\n            type: str\n            sample: "2001:db8:0:102::/64"\n        availability_zone:\n            description: Availability zone of the Subnet\n            returned: I(state=present)\n            type: str\n            sample: us-east-1a\n        state:\n            description: state of the Subnet\n            returned: I(state=present)\n            type: str\n            sample: available\n        tags:\n            description: tags attached to the Subnet, includes name\n            returned: I(state=present)\n            type: dict\n            sample: {"Name": "My Subnet", "env": "staging"}\n        map_public_ip_on_launch:\n            description: whether public IP is auto-assigned to new instances\n            returned: I(state=present)\n            type: bool\n            sample: false\n        assign_ipv6_address_on_creation:\n            description: whether IPv6 address is auto-assigned to new instances\n            returned: I(state=present)\n            type: bool\n            sample: false\n        vpc_id:\n            description: the id of the VPC where this Subnet exists\n            returned: I(state=present)\n            type: str\n            sample: vpc-67236184\n        available_ip_address_count:\n            description: number of available IPv4 addresses\n            returned: I(state=present)\n            type: str\n            sample: 251\n        default_for_az:\n            description: indicates whether this is the default Subnet for this Availability Zone\n            returned: I(state=present)\n            type: bool\n            sample: false\n        ipv6_association_id:\n            description: The IPv6 association ID for the currently associated CIDR\n            returned: I(state=present)\n            type: str\n            sample: subnet-cidr-assoc-b85c74d2\n        ipv6_cidr_block_association_set:\n            description: An array of IPv6 cidr block association set information.\n            returned: I(state=present)\n            type: complex\n            contains:\n                association_id:\n                    description: The association ID\n                    returned: always\n                    type: str\n                ipv6_cidr_block:\n                    description: The IPv6 CIDR block that is associated with the subnet.\n                    returned: always\n                    type: str\n                ipv6_cidr_block_state:\n                    description: A hash/dict that contains a single item. The state of the cidr block association.\n                    returned: always\n                    type: dict\n                    contains:\n                        state:\n                            description: The CIDR block association state.\n                            returned: always\n                            type: str\n'
import time
try:
    import botocore
except ImportError:
    pass
from ansible.module_utils._text import to_text
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.aws.waiters import get_waiter
from ansible.module_utils.ec2 import ansible_dict_to_boto3_filter_list, ansible_dict_to_boto3_tag_list, camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict, compare_aws_tags, AWSRetry

def get_subnet_info(subnet):
    if 'Subnets' in subnet:
        return [get_subnet_info(s) for s in subnet['Subnets']]
    elif 'Subnet' in subnet:
        subnet = camel_dict_to_snake_dict(subnet['Subnet'])
    else:
        subnet = camel_dict_to_snake_dict(subnet)
    if 'tags' in subnet:
        subnet['tags'] = boto3_tag_list_to_ansible_dict(subnet['tags'])
    else:
        subnet['tags'] = dict()
    if 'subnet_id' in subnet:
        subnet['id'] = subnet['subnet_id']
        del subnet['subnet_id']
    subnet['ipv6_cidr_block'] = ''
    subnet['ipv6_association_id'] = ''
    ipv6set = subnet.get('ipv6_cidr_block_association_set')
    if ipv6set:
        for item in ipv6set:
            if item.get('ipv6_cidr_block_state', {}).get('state') in ('associated', 'associating'):
                subnet['ipv6_cidr_block'] = item['ipv6_cidr_block']
                subnet['ipv6_association_id'] = item['association_id']
    return subnet

@AWSRetry.exponential_backoff()
def describe_subnets_with_backoff(client, **params):
    return client.describe_subnets(**params)

def waiter_params(module, params, start_time):
    if not module.botocore_at_least('1.7.0'):
        remaining_wait_timeout = int(module.params['wait_timeout'] + start_time - time.time())
        params['WaiterConfig'] = {'Delay': 5, 'MaxAttempts': remaining_wait_timeout // 5}
    return params

def handle_waiter(conn, module, waiter_name, params, start_time):
    try:
        get_waiter(conn, waiter_name).wait(**waiter_params(module, params, start_time))
    except botocore.exceptions.WaiterError as e:
        module.fail_json_aws(e, 'Failed to wait for updates to complete')
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, 'An exception happened while trying to wait for updates')

def create_subnet(conn, module, vpc_id, cidr, ipv6_cidr=None, az=None, start_time=None):
    wait = module.params['wait']
    wait_timeout = module.params['wait_timeout']
    params = dict(VpcId=vpc_id, CidrBlock=cidr)
    if ipv6_cidr:
        params['Ipv6CidrBlock'] = ipv6_cidr
    if az:
        params['AvailabilityZone'] = az
    try:
        subnet = get_subnet_info(conn.create_subnet(**params))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't create subnet")
    if wait and subnet.get('state') != 'available':
        handle_waiter(conn, module, 'subnet_exists', {'SubnetIds': [subnet['id']]}, start_time)
        try:
            conn.get_waiter('subnet_available').wait(**waiter_params(module, {'SubnetIds': [subnet['id']]}, start_time))
            subnet['state'] = 'available'
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, 'Create subnet action timed out waiting for subnet to become available')
    return subnet

def ensure_tags(conn, module, subnet, tags, purge_tags, start_time):
    changed = False
    filters = ansible_dict_to_boto3_filter_list({'resource-id': subnet['id'], 'resource-type': 'subnet'})
    try:
        cur_tags = conn.describe_tags(Filters=filters)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't describe tags")
    (to_update, to_delete) = compare_aws_tags(boto3_tag_list_to_ansible_dict(cur_tags.get('Tags')), tags, purge_tags)
    if to_update:
        try:
            if not module.check_mode:
                AWSRetry.exponential_backoff(catch_extra_error_codes=['InvalidSubnetID.NotFound'])(conn.create_tags)(Resources=[subnet['id']], Tags=ansible_dict_to_boto3_tag_list(to_update))
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create tags")
    if to_delete:
        try:
            if not module.check_mode:
                tags_list = []
                for key in to_delete:
                    tags_list.append({'Key': key})
                AWSRetry.exponential_backoff(catch_extra_error_codes=['InvalidSubnetID.NotFound'])(conn.delete_tags)(Resources=[subnet['id']], Tags=tags_list)
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete tags")
    if module.params['wait'] and (not module.check_mode):
        filters = [{'Name': 'tag:{0}'.format(k), 'Values': [v]} for (k, v) in tags.items()]
        handle_waiter(conn, module, 'subnet_exists', {'SubnetIds': [subnet['id']], 'Filters': filters}, start_time)
    return changed

def ensure_map_public(conn, module, subnet, map_public, check_mode, start_time):
    if check_mode:
        return
    try:
        conn.modify_subnet_attribute(SubnetId=subnet['id'], MapPublicIpOnLaunch={'Value': map_public})
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't modify subnet attribute")

def ensure_assign_ipv6_on_create(conn, module, subnet, assign_instances_ipv6, check_mode, start_time):
    if check_mode:
        return
    try:
        conn.modify_subnet_attribute(SubnetId=subnet['id'], AssignIpv6AddressOnCreation={'Value': assign_instances_ipv6})
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't modify subnet attribute")

def disassociate_ipv6_cidr(conn, module, subnet, start_time):
    if subnet.get('assign_ipv6_address_on_creation'):
        ensure_assign_ipv6_on_create(conn, module, subnet, False, False, start_time)
    try:
        conn.disassociate_subnet_cidr_block(AssociationId=subnet['ipv6_association_id'])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't disassociate ipv6 cidr block id {0} from subnet {1}".format(subnet['ipv6_association_id'], subnet['id']))
    if module.params['wait']:
        filters = ansible_dict_to_boto3_filter_list({'ipv6-cidr-block-association.state': ['disassociated'], 'vpc-id': subnet['vpc_id']})
        handle_waiter(conn, module, 'subnet_exists', {'SubnetIds': [subnet['id']], 'Filters': filters}, start_time)

def ensure_ipv6_cidr_block(conn, module, subnet, ipv6_cidr, check_mode, start_time):
    wait = module.params['wait']
    changed = False
    if subnet['ipv6_association_id'] and (not ipv6_cidr):
        if not check_mode:
            disassociate_ipv6_cidr(conn, module, subnet, start_time)
        changed = True
    if ipv6_cidr:
        filters = ansible_dict_to_boto3_filter_list({'ipv6-cidr-block-association.ipv6-cidr-block': ipv6_cidr, 'vpc-id': subnet['vpc_id']})
        try:
            check_subnets = get_subnet_info(describe_subnets_with_backoff(conn, Filters=filters))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't get subnet info")
        if check_subnets and check_subnets[0]['ipv6_cidr_block']:
            module.fail_json(msg="The IPv6 CIDR '{0}' conflicts with another subnet".format(ipv6_cidr))
        if subnet['ipv6_association_id']:
            if not check_mode:
                disassociate_ipv6_cidr(conn, module, subnet, start_time)
            changed = True
        try:
            if not check_mode:
                associate_resp = conn.associate_subnet_cidr_block(SubnetId=subnet['id'], Ipv6CidrBlock=ipv6_cidr)
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't associate ipv6 cidr {0} to {1}".format(ipv6_cidr, subnet['id']))
        else:
            if not check_mode and wait:
                filters = ansible_dict_to_boto3_filter_list({'ipv6-cidr-block-association.state': ['associated'], 'vpc-id': subnet['vpc_id']})
                handle_waiter(conn, module, 'subnet_exists', {'SubnetIds': [subnet['id']], 'Filters': filters}, start_time)
        if associate_resp.get('Ipv6CidrBlockAssociation', {}).get('AssociationId'):
            subnet['ipv6_association_id'] = associate_resp['Ipv6CidrBlockAssociation']['AssociationId']
            subnet['ipv6_cidr_block'] = associate_resp['Ipv6CidrBlockAssociation']['Ipv6CidrBlock']
            if subnet['ipv6_cidr_block_association_set']:
                subnet['ipv6_cidr_block_association_set'][0] = camel_dict_to_snake_dict(associate_resp['Ipv6CidrBlockAssociation'])
            else:
                subnet['ipv6_cidr_block_association_set'].append(camel_dict_to_snake_dict(associate_resp['Ipv6CidrBlockAssociation']))
    return changed

def get_matching_subnet(conn, module, vpc_id, cidr):
    filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id, 'cidr-block': cidr})
    try:
        subnets = get_subnet_info(describe_subnets_with_backoff(conn, Filters=filters))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get matching subnet")
    if subnets:
        return subnets[0]
    return None

def ensure_subnet_present(conn, module):
    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    changed = False
    start_time = time.time()
    if subnet is None:
        if not module.check_mode:
            subnet = create_subnet(conn, module, module.params['vpc_id'], module.params['cidr'], ipv6_cidr=module.params['ipv6_cidr'], az=module.params['az'], start_time=start_time)
        changed = True
        if subnet is None:
            return {'changed': changed, 'subnet': {}}
    if module.params['wait']:
        handle_waiter(conn, module, 'subnet_exists', {'SubnetIds': [subnet['id']]}, start_time)
    if module.params['ipv6_cidr'] != subnet.get('ipv6_cidr_block'):
        if ensure_ipv6_cidr_block(conn, module, subnet, module.params['ipv6_cidr'], module.check_mode, start_time):
            changed = True
    if module.params['map_public'] != subnet['map_public_ip_on_launch']:
        ensure_map_public(conn, module, subnet, module.params['map_public'], module.check_mode, start_time)
        changed = True
    if module.params['assign_instances_ipv6'] != subnet.get('assign_ipv6_address_on_creation'):
        ensure_assign_ipv6_on_create(conn, module, subnet, module.params['assign_instances_ipv6'], module.check_mode, start_time)
        changed = True
    if module.params['tags'] != subnet['tags']:
        stringified_tags_dict = dict(((to_text(k), to_text(v)) for (k, v) in module.params['tags'].items()))
        if ensure_tags(conn, module, subnet, stringified_tags_dict, module.params['purge_tags'], start_time):
            changed = True
    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    if not module.check_mode and module.params['wait']:
        subnet = ensure_final_subnet(conn, module, subnet, start_time)
    return {'changed': changed, 'subnet': subnet}

def ensure_final_subnet(conn, module, subnet, start_time):
    for rewait in range(0, 30):
        map_public_correct = False
        assign_ipv6_correct = False
        if module.params['map_public'] == subnet['map_public_ip_on_launch']:
            map_public_correct = True
        elif module.params['map_public']:
            handle_waiter(conn, module, 'subnet_has_map_public', {'SubnetIds': [subnet['id']]}, start_time)
        else:
            handle_waiter(conn, module, 'subnet_no_map_public', {'SubnetIds': [subnet['id']]}, start_time)
        if module.params['assign_instances_ipv6'] == subnet.get('assign_ipv6_address_on_creation'):
            assign_ipv6_correct = True
        elif module.params['assign_instances_ipv6']:
            handle_waiter(conn, module, 'subnet_has_assign_ipv6', {'SubnetIds': [subnet['id']]}, start_time)
        else:
            handle_waiter(conn, module, 'subnet_no_assign_ipv6', {'SubnetIds': [subnet['id']]}, start_time)
        if map_public_correct and assign_ipv6_correct:
            break
        time.sleep(5)
        subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    return subnet

def ensure_subnet_absent(conn, module):
    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    if subnet is None:
        return {'changed': False}
    try:
        if not module.check_mode:
            conn.delete_subnet(SubnetId=subnet['id'])
            if module.params['wait']:
                handle_waiter(conn, module, 'subnet_deleted', {'SubnetIds': [subnet['id']]}, time.time())
        return {'changed': True}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete subnet")

def main():
    argument_spec = dict(az=dict(default=None, required=False), cidr=dict(required=True), ipv6_cidr=dict(default='', required=False), state=dict(default='present', choices=['present', 'absent']), tags=dict(default={}, required=False, type='dict', aliases=['resource_tags']), vpc_id=dict(required=True), map_public=dict(default=False, required=False, type='bool'), assign_instances_ipv6=dict(default=False, required=False, type='bool'), wait=dict(type='bool', default=True), wait_timeout=dict(type='int', default=300, required=False), purge_tags=dict(default=True, type='bool'))
    required_if = [('assign_instances_ipv6', True, ['ipv6_cidr'])]
    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True, required_if=required_if)
    if module.params.get('assign_instances_ipv6') and (not module.params.get('ipv6_cidr')):
        module.fail_json(msg='assign_instances_ipv6 is True but ipv6_cidr is None or an empty string')
    if not module.botocore_at_least('1.7.0'):
        module.warn('botocore >= 1.7.0 is required to use wait_timeout for custom wait times')
    connection = module.client('ec2')
    state = module.params.get('state')
    try:
        if state == 'present':
            result = ensure_subnet_present(connection, module)
        elif state == 'absent':
            result = ensure_subnet_absent(connection, module)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)
    module.exit_json(**result)
if __name__ == '__main__':
    main()