from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: ec2_eni_info\nshort_description: Gather information about ec2 ENI interfaces in AWS\ndescription:\n    - Gather information about ec2 ENI interfaces in AWS.\n    - This module was called C(ec2_eni_facts) before Ansible 2.9. The usage did not change.\nversion_added: "2.0"\nauthor: "Rob White (@wimnat)"\nrequirements: [ boto3 ]\noptions:\n  filters:\n    description:\n      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.\n        See U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeNetworkInterfaces.html) for possible filters.\n    type: dict\nextends_documentation_fragment:\n    - aws\n    - ec2\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Gather information about all ENIs\n- ec2_eni_info:\n\n# Gather information about a particular ENI\n- ec2_eni_info:\n    filters:\n      network-interface-id: eni-xxxxxxx\n\n'
RETURN = '\nnetwork_interfaces:\n  description: List of matching elastic network interfaces\n  returned: always\n  type: complex\n  contains:\n    association:\n      description: Info of associated elastic IP (EIP)\n      returned: always, empty dict if no association exists\n      type: dict\n      sample: {\n          allocation_id: "eipalloc-5sdf123",\n          association_id: "eipassoc-8sdf123",\n          ip_owner_id: "4415120123456",\n          public_dns_name: "ec2-52-1-0-63.compute-1.amazonaws.com",\n          public_ip: "52.1.0.63"\n        }\n    attachment:\n      description: Info about attached ec2 instance\n      returned: always, empty dict if ENI is not attached\n      type: dict\n      sample: {\n        attach_time: "2017-08-05T15:25:47+00:00",\n        attachment_id: "eni-attach-149d21234",\n        delete_on_termination: false,\n        device_index: 1,\n        instance_id: "i-15b8d3cadbafa1234",\n        instance_owner_id: "4415120123456",\n        status: "attached"\n      }\n    availability_zone:\n      description: Availability zone of ENI\n      returned: always\n      type: str\n      sample: "us-east-1b"\n    description:\n      description: Description text for ENI\n      returned: always\n      type: str\n      sample: "My favourite network interface"\n    groups:\n      description: List of attached security groups\n      returned: always\n      type: list\n      sample: [\n        {\n          group_id: "sg-26d0f1234",\n          group_name: "my_ec2_security_group"\n        }\n      ]\n    id:\n      description: The id of the ENI (alias for network_interface_id)\n      returned: always\n      type: str\n      sample: "eni-392fsdf"\n    interface_type:\n      description: Type of the network interface\n      returned: always\n      type: str\n      sample: "interface"\n    ipv6_addresses:\n      description: List of IPv6 addresses for this interface\n      returned: always\n      type: list\n      sample: []\n    mac_address:\n      description: MAC address of the network interface\n      returned: always\n      type: str\n      sample: "0a:f8:10:2f:ab:a1"\n    network_interface_id:\n      description: The id of the ENI\n      returned: always\n      type: str\n      sample: "eni-392fsdf"\n    owner_id:\n      description: AWS account id of the owner of the ENI\n      returned: always\n      type: str\n      sample: "4415120123456"\n    private_dns_name:\n      description: Private DNS name for the ENI\n      returned: always\n      type: str\n      sample: "ip-172-16-1-180.ec2.internal"\n    private_ip_address:\n      description: Private IP address for the ENI\n      returned: always\n      type: str\n      sample: "172.16.1.180"\n    private_ip_addresses:\n      description: List of private IP addresses attached to the ENI\n      returned: always\n      type: list\n      sample: []\n    requester_id:\n      description: The ID of the entity that launched the ENI\n      returned: always\n      type: str\n      sample: "AIDAIONYVJQNIAZFT3ABC"\n    requester_managed:\n      description:  Indicates whether the network interface is being managed by an AWS service.\n      returned: always\n      type: bool\n      sample: false\n    source_dest_check:\n      description: Indicates whether the network interface performs source/destination checking.\n      returned: always\n      type: bool\n      sample: false\n    status:\n      description: Indicates if the network interface is attached to an instance or not\n      returned: always\n      type: str\n      sample: "in-use"\n    subnet_id:\n      description: Subnet ID the ENI is in\n      returned: always\n      type: str\n      sample: "subnet-7bbf01234"\n    tag_set:\n      description: Dictionary of tags added to the ENI\n      returned: always\n      type: dict\n      sample: {}\n    vpc_id:\n      description: ID of the VPC the network interface it part of\n      returned: always\n      type: str\n      sample: "vpc-b3f1f123"\n'
try:
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import ansible_dict_to_boto3_filter_list, boto3_conn
from ansible.module_utils.ec2 import boto3_tag_list_to_ansible_dict, camel_dict_to_snake_dict
from ansible.module_utils.ec2 import ec2_argument_spec, get_aws_connection_info

def list_eni(connection, module):
    if module.params.get('filters') is None:
        filters = []
    else:
        filters = ansible_dict_to_boto3_filter_list(module.params.get('filters'))
    try:
        network_interfaces_result = connection.describe_network_interfaces(Filters=filters)['NetworkInterfaces']
    except (ClientError, NoCredentialsError) as e:
        module.fail_json(msg=e.message)
    camel_network_interfaces = []
    for network_interface in network_interfaces_result:
        network_interface['TagSet'] = boto3_tag_list_to_ansible_dict(network_interface['TagSet'])
        network_interface['Id'] = network_interface['NetworkInterfaceId']
        camel_network_interfaces.append(camel_dict_to_snake_dict(network_interface))
    module.exit_json(network_interfaces=camel_network_interfaces)

def get_eni_info(interface):
    private_addresses = []
    for ip in interface.private_ip_addresses:
        private_addresses.append({'private_ip_address': ip.private_ip_address, 'primary_address': ip.primary})
    interface_info = {'id': interface.id, 'subnet_id': interface.subnet_id, 'vpc_id': interface.vpc_id, 'description': interface.description, 'owner_id': interface.owner_id, 'status': interface.status, 'mac_address': interface.mac_address, 'private_ip_address': interface.private_ip_address, 'source_dest_check': interface.source_dest_check, 'groups': dict(((group.id, group.name) for group in interface.groups)), 'private_ip_addresses': private_addresses}
    if hasattr(interface, 'publicDnsName'):
        interface_info['association'] = {'public_ip_address': interface.publicIp, 'public_dns_name': interface.publicDnsName, 'ip_owner_id': interface.ipOwnerId}
    if interface.attachment is not None:
        interface_info['attachment'] = {'attachment_id': interface.attachment.id, 'instance_id': interface.attachment.instance_id, 'device_index': interface.attachment.device_index, 'status': interface.attachment.status, 'attach_time': interface.attachment.attach_time, 'delete_on_termination': interface.attachment.delete_on_termination}
    return interface_info

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(filters=dict(default=None, type='dict')))
    module = AnsibleModule(argument_spec=argument_spec)
    if module._name == 'ec2_eni_facts':
        module.deprecate("The 'ec2_eni_facts' module has been renamed to 'ec2_eni_info'", version='2.13', collection_name='ansible.builtin')
    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')
    (region, ec2_url, aws_connect_params) = get_aws_connection_info(module, boto3=True)
    connection = boto3_conn(module, conn_type='client', resource='ec2', region=region, endpoint=ec2_url, **aws_connect_params)
    list_eni(connection, module)
if __name__ == '__main__':
    main()