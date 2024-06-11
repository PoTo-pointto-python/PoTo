from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: ec2_ami_info\nversion_added: '2.5'\nshort_description: Gather information about ec2 AMIs\ndescription:\n  - Gather information about ec2 AMIs\n  - This module was called C(ec2_ami_facts) before Ansible 2.9. The usage did not change.\nauthor:\n  - Prasad Katti (@prasadkatti)\nrequirements: [ boto3 ]\noptions:\n  image_ids:\n    description: One or more image IDs.\n    aliases: [image_id]\n    type: list\n    elements: str\n  filters:\n    description:\n      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.\n      - See U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeImages.html) for possible filters.\n      - Filter names and values are case sensitive.\n    type: dict\n  owners:\n    description:\n      - Filter the images by the owner. Valid options are an AWS account ID, self,\n        or an AWS owner alias ( amazon | aws-marketplace | microsoft ).\n    aliases: [owner]\n    type: list\n    elements: str\n  executable_users:\n    description:\n      - Filter images by users with explicit launch permissions. Valid options are an AWS account ID, self, or all (public AMIs).\n    aliases: [executable_user]\n    type: list\n    elements: str\n  describe_image_attributes:\n    description:\n      - Describe attributes (like launchPermission) of the images found.\n    default: no\n    type: bool\n\nextends_documentation_fragment:\n    - aws\n    - ec2\n"
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n- name: gather information about an AMI using ami-id\n  ec2_ami_info:\n    image_ids: ami-5b488823\n\n- name: gather information about all AMIs with tag key Name and value webapp\n  ec2_ami_info:\n    filters:\n      "tag:Name": webapp\n\n- name: gather information about an AMI with \'AMI Name\' equal to foobar\n  ec2_ami_info:\n    filters:\n      name: foobar\n\n- name: gather information about Ubuntu 17.04 AMIs published by Canonical (099720109477)\n  ec2_ami_info:\n    owners: 099720109477\n    filters:\n      name: "ubuntu/images/ubuntu-zesty-17.04-*"\n'
RETURN = '\nimages:\n  description: A list of images.\n  returned: always\n  type: list\n  elements: dict\n  contains:\n    architecture:\n      description: The architecture of the image.\n      returned: always\n      type: str\n      sample: x86_64\n    block_device_mappings:\n      description: Any block device mapping entries.\n      returned: always\n      type: list\n      elements: dict\n      contains:\n        device_name:\n          description: The device name exposed to the instance.\n          returned: always\n          type: str\n          sample: /dev/sda1\n        ebs:\n          description: EBS volumes\n          returned: always\n          type: complex\n    creation_date:\n      description: The date and time the image was created.\n      returned: always\n      type: str\n      sample: \'2017-10-16T19:22:13.000Z\'\n    description:\n      description: The description of the AMI.\n      returned: always\n      type: str\n      sample: \'\'\n    ena_support:\n      description: Whether enhanced networking with ENA is enabled.\n      returned: always\n      type: bool\n      sample: true\n    hypervisor:\n      description: The hypervisor type of the image.\n      returned: always\n      type: str\n      sample: xen\n    image_id:\n      description: The ID of the AMI.\n      returned: always\n      type: str\n      sample: ami-5b466623\n    image_location:\n      description: The location of the AMI.\n      returned: always\n      type: str\n      sample: 408466080000/Webapp\n    image_type:\n      description: The type of image.\n      returned: always\n      type: str\n      sample: machine\n    launch_permissions:\n      description: A List of AWS accounts may launch the AMI.\n      returned: When image is owned by calling account and I(describe_image_attributes) is yes.\n      type: list\n      elements: dict\n      contains:\n        group:\n            description: A value of \'all\' means the AMI is public.\n            type: str\n        user_id:\n            description: An AWS account ID with permissions to launch the AMI.\n            type: str\n      sample: [{"group": "all"}, {"user_id": "408466080000"}]\n    name:\n      description: The name of the AMI that was provided during image creation.\n      returned: always\n      type: str\n      sample: Webapp\n    owner_id:\n      description: The AWS account ID of the image owner.\n      returned: always\n      type: str\n      sample: \'408466080000\'\n    public:\n      description: Whether the image has public launch permissions.\n      returned: always\n      type: bool\n      sample: true\n    root_device_name:\n      description: The device name of the root device.\n      returned: always\n      type: str\n      sample: /dev/sda1\n    root_device_type:\n      description: The type of root device used by the AMI.\n      returned: always\n      type: str\n      sample: ebs\n    sriov_net_support:\n      description: Whether enhanced networking is enabled.\n      returned: always\n      type: str\n      sample: simple\n    state:\n      description: The current state of the AMI.\n      returned: always\n      type: str\n      sample: available\n    tags:\n      description: Any tags assigned to the image.\n      returned: always\n      type: dict\n    virtualization_type:\n      description: The type of virtualization of the AMI.\n      returned: always\n      type: str\n      sample: hvm\n'
try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import ansible_dict_to_boto3_filter_list, camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict

def list_ec2_images(ec2_client, module):
    image_ids = module.params.get('image_ids')
    owners = module.params.get('owners')
    executable_users = module.params.get('executable_users')
    filters = module.params.get('filters')
    owner_param = []
    for owner in owners:
        if owner.isdigit():
            if 'owner-id' not in filters:
                filters['owner-id'] = list()
            filters['owner-id'].append(owner)
        elif owner == 'self':
            owner_param.append(owner)
        else:
            if 'owner-alias' not in filters:
                filters['owner-alias'] = list()
            filters['owner-alias'].append(owner)
    filters = ansible_dict_to_boto3_filter_list(filters)
    try:
        images = ec2_client.describe_images(ImageIds=image_ids, Filters=filters, Owners=owner_param, ExecutableUsers=executable_users)
        images = [camel_dict_to_snake_dict(image) for image in images['Images']]
    except (ClientError, BotoCoreError) as err:
        module.fail_json_aws(err, msg='error describing images')
    for image in images:
        try:
            image['tags'] = boto3_tag_list_to_ansible_dict(image.get('tags', []))
            if module.params.get('describe_image_attributes'):
                launch_permissions = ec2_client.describe_image_attribute(Attribute='launchPermission', ImageId=image['image_id'])['LaunchPermissions']
                image['launch_permissions'] = [camel_dict_to_snake_dict(perm) for perm in launch_permissions]
        except (ClientError, BotoCoreError) as err:
            pass
    images.sort(key=lambda e: e.get('creation_date', ''))
    module.exit_json(images=images)

def main():
    argument_spec = dict(image_ids=dict(default=[], type='list', aliases=['image_id']), filters=dict(default={}, type='dict'), owners=dict(default=[], type='list', aliases=['owner']), executable_users=dict(default=[], type='list', aliases=['executable_user']), describe_image_attributes=dict(default=False, type='bool'))
    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    if module._module._name == 'ec2_ami_facts':
        module._module.deprecate("The 'ec2_ami_facts' module has been renamed to 'ec2_ami_info'", version='2.13', collection_name='ansible.builtin')
    ec2_client = module.client('ec2')
    list_ec2_images(ec2_client, module)
if __name__ == '__main__':
    main()