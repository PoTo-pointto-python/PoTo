from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'supported_by': 'community', 'status': ['preview']}
DOCUMENTATION = "\nmodule: aws_az_info\nshort_description: Gather information about availability zones in AWS.\ndescription:\n    - Gather information about availability zones in AWS.\n    - This module was called C(aws_az_facts) before Ansible 2.9. The usage did not change.\nversion_added: '2.5'\nauthor: 'Henrique Rodrigues (@Sodki)'\noptions:\n  filters:\n    description:\n      - A dict of filters to apply. Each dict item consists of a filter key and a filter value. See\n        U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeAvailabilityZones.html) for\n        possible filters. Filter names and values are case sensitive. You can also use underscores\n        instead of dashes (-) in the filter keys, which will take precedence in case of conflict.\n    required: false\n    default: {}\n    type: dict\nextends_documentation_fragment:\n    - aws\n    - ec2\nrequirements: [botocore, boto3]\n"
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Gather information about all availability zones\n- aws_az_info:\n\n# Gather information about a single availability zone\n- aws_az_info:\n    filters:\n      zone-name: eu-west-1a\n'
RETURN = '\navailability_zones:\n    returned: on success\n    description: >\n        Availability zones that match the provided filters. Each element consists of a dict with all the information\n        related to that available zone.\n    type: list\n    sample: "[\n        {\n            \'messages\': [],\n            \'region_name\': \'us-west-1\',\n            \'state\': \'available\',\n            \'zone_name\': \'us-west-1b\'\n        },\n        {\n            \'messages\': [],\n            \'region_name\': \'us-west-1\',\n            \'state\': \'available\',\n            \'zone_name\': \'us-west-1c\'\n        }\n    ]"\n'
from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import AWSRetry, ansible_dict_to_boto3_filter_list, camel_dict_to_snake_dict
try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass

def main():
    argument_spec = dict(filters=dict(default={}, type='dict'))
    module = AnsibleAWSModule(argument_spec=argument_spec)
    if module._name == 'aws_az_facts':
        module.deprecate("The 'aws_az_facts' module has been renamed to 'aws_az_info'", version='2.14', collection_name='ansible.builtin')
    connection = module.client('ec2', retry_decorator=AWSRetry.jittered_backoff())
    sanitized_filters = dict(((k.replace('_', '-'), v) for (k, v) in module.params.get('filters').items()))
    try:
        availability_zones = connection.describe_availability_zones(Filters=ansible_dict_to_boto3_filter_list(sanitized_filters))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Unable to describe availability zones.')
    snaked_availability_zones = [camel_dict_to_snake_dict(az) for az in availability_zones['AvailabilityZones']]
    module.exit_json(availability_zones=snaked_availability_zones)
if __name__ == '__main__':
    main()