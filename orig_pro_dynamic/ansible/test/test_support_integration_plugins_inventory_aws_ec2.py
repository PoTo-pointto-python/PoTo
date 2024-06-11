from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = "\n    name: aws_ec2\n    plugin_type: inventory\n    short_description: EC2 inventory source\n    requirements:\n        - boto3\n        - botocore\n    extends_documentation_fragment:\n        - inventory_cache\n        - constructed\n    description:\n        - Get inventory hosts from Amazon Web Services EC2.\n        - Uses a YAML configuration file that ends with C(aws_ec2.(yml|yaml)).\n    notes:\n        - If no credentials are provided and the control node has an associated IAM instance profile then the\n          role will be used for authentication.\n    author:\n        - Sloane Hertel (@s-hertel)\n    options:\n        aws_profile:\n          description: The AWS profile\n          type: str\n          aliases: [ boto_profile ]\n          env:\n            - name: AWS_DEFAULT_PROFILE\n            - name: AWS_PROFILE\n        aws_access_key:\n          description: The AWS access key to use.\n          type: str\n          aliases: [ aws_access_key_id ]\n          env:\n            - name: EC2_ACCESS_KEY\n            - name: AWS_ACCESS_KEY\n            - name: AWS_ACCESS_KEY_ID\n        aws_secret_key:\n          description: The AWS secret key that corresponds to the access key.\n          type: str\n          aliases: [ aws_secret_access_key ]\n          env:\n            - name: EC2_SECRET_KEY\n            - name: AWS_SECRET_KEY\n            - name: AWS_SECRET_ACCESS_KEY\n        aws_security_token:\n          description: The AWS security token if using temporary access and secret keys.\n          type: str\n          env:\n            - name: EC2_SECURITY_TOKEN\n            - name: AWS_SESSION_TOKEN\n            - name: AWS_SECURITY_TOKEN\n        plugin:\n            description: Token that ensures this is a source file for the plugin.\n            required: True\n            choices: ['aws_ec2']\n        iam_role_arn:\n          description: The ARN of the IAM role to assume to perform the inventory lookup. You should still provide AWS\n              credentials with enough privilege to perform the AssumeRole action.\n          version_added: '2.9'\n        regions:\n          description:\n              - A list of regions in which to describe EC2 instances.\n              - If empty (the default) default this will include all regions, except possibly restricted ones like us-gov-west-1 and cn-north-1.\n          type: list\n          default: []\n        hostnames:\n          description:\n              - A list in order of precedence for hostname variables.\n              - You can use the options specified in U(http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html#options).\n              - To use tags as hostnames use the syntax tag:Name=Value to use the hostname Name_Value, or tag:Name to use the value of the Name tag.\n          type: list\n          default: []\n        filters:\n          description:\n              - A dictionary of filter value pairs.\n              - Available filters are listed here U(http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html#options).\n          type: dict\n          default: {}\n        include_extra_api_calls:\n          description:\n              - Add two additional API calls for every instance to include 'persistent' and 'events' host variables.\n              - Spot instances may be persistent and instances may have associated events.\n          type: bool\n          default: False\n          version_added: '2.8'\n        strict_permissions:\n          description:\n              - By default if a 403 (Forbidden) error code is encountered this plugin will fail.\n              - You can set this option to False in the inventory config file which will allow 403 errors to be gracefully skipped.\n          type: bool\n          default: True\n        use_contrib_script_compatible_sanitization:\n          description:\n            - By default this plugin is using a general group name sanitization to create safe and usable group names for use in Ansible.\n              This option allows you to override that, in efforts to allow migration from the old inventory script and\n              matches the sanitization of groups when the script's ``replace_dash_in_groups`` option is set to ``False``.\n              To replicate behavior of ``replace_dash_in_groups = True`` with constructed groups,\n              you will need to replace hyphens with underscores via the regex_replace filter for those entries.\n            - For this to work you should also turn off the TRANSFORM_INVALID_GROUP_CHARS setting,\n              otherwise the core engine will just use the standard sanitization on top.\n            - This is not the default as such names break certain functionality as not all characters are valid Python identifiers\n              which group names end up being used as.\n          type: bool\n          default: False\n          version_added: '2.8'\n"
EXAMPLES = '\n# Minimal example using environment vars or instance role credentials\n# Fetch all hosts in us-east-1, the hostname is the public DNS if it exists, otherwise the private IP address\nplugin: aws_ec2\nregions:\n  - us-east-1\n\n# Example using filters, ignoring permission errors, and specifying the hostname precedence\nplugin: aws_ec2\nboto_profile: aws_profile\n# Populate inventory with instances in these regions\nregions:\n  - us-east-1\n  - us-east-2\nfilters:\n  # All instances with their `Environment` tag set to `dev`\n  tag:Environment: dev\n  # All dev and QA hosts\n  tag:Environment:\n    - dev\n    - qa\n  instance.group-id: sg-xxxxxxxx\n# Ignores 403 errors rather than failing\nstrict_permissions: False\n# Note: I(hostnames) sets the inventory_hostname. To modify ansible_host without modifying\n# inventory_hostname use compose (see example below).\nhostnames:\n  - tag:Name=Tag1,Name=Tag2  # Return specific hosts only\n  - tag:CustomDNSName\n  - dns-name\n  - private-ip-address\n\n# Example using constructed features to create groups and set ansible_host\nplugin: aws_ec2\nregions:\n  - us-east-1\n  - us-west-1\n# keyed_groups may be used to create custom groups\nstrict: False\nkeyed_groups:\n  # Add e.g. x86_64 hosts to an arch_x86_64 group\n  - prefix: arch\n    key: \'architecture\'\n  # Add hosts to tag_Name_Value groups for each Name/Value tag pair\n  - prefix: tag\n    key: tags\n  # Add hosts to e.g. instance_type_z3_tiny\n  - prefix: instance_type\n    key: instance_type\n  # Create security_groups_sg_abcd1234 group for each SG\n  - key: \'security_groups|json_query("[].group_id")\'\n    prefix: \'security_groups\'\n  # Create a group for each value of the Application tag\n  - key: tags.Application\n    separator: \'\'\n  # Create a group per region e.g. aws_region_us_east_2\n  - key: placement.region\n    prefix: aws_region\n  # Create a group (or groups) based on the value of a custom tag "Role" and add them to a metagroup called "project"\n  - key: tags[\'Role\']\n    prefix: foo\n    parent_group: "project"\n# Set individual variables with compose\ncompose:\n  # Use the private IP address to connect to the host\n  # (note: this does not modify inventory_hostname, which is set via I(hostnames))\n  ansible_host: private_ip_address\n'
import re
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.utils.display import Display
from ansible.module_utils.six import string_types
try:
    import boto3
    import botocore
except ImportError:
    raise AnsibleError('The ec2 dynamic inventory plugin requires boto3 and botocore.')
display = Display()
instance_meta_filter_to_boto_attr = {'group-id': ('Groups', 'GroupId'), 'group-name': ('Groups', 'GroupName'), 'network-interface.attachment.instance-owner-id': ('OwnerId',), 'owner-id': ('OwnerId',), 'requester-id': ('RequesterId',), 'reservation-id': ('ReservationId',)}
instance_data_filter_to_boto_attr = {'affinity': ('Placement', 'Affinity'), 'architecture': ('Architecture',), 'availability-zone': ('Placement', 'AvailabilityZone'), 'block-device-mapping.attach-time': ('BlockDeviceMappings', 'Ebs', 'AttachTime'), 'block-device-mapping.delete-on-termination': ('BlockDeviceMappings', 'Ebs', 'DeleteOnTermination'), 'block-device-mapping.device-name': ('BlockDeviceMappings', 'DeviceName'), 'block-device-mapping.status': ('BlockDeviceMappings', 'Ebs', 'Status'), 'block-device-mapping.volume-id': ('BlockDeviceMappings', 'Ebs', 'VolumeId'), 'client-token': ('ClientToken',), 'dns-name': ('PublicDnsName',), 'host-id': ('Placement', 'HostId'), 'hypervisor': ('Hypervisor',), 'iam-instance-profile.arn': ('IamInstanceProfile', 'Arn'), 'image-id': ('ImageId',), 'instance-id': ('InstanceId',), 'instance-lifecycle': ('InstanceLifecycle',), 'instance-state-code': ('State', 'Code'), 'instance-state-name': ('State', 'Name'), 'instance-type': ('InstanceType',), 'instance.group-id': ('SecurityGroups', 'GroupId'), 'instance.group-name': ('SecurityGroups', 'GroupName'), 'ip-address': ('PublicIpAddress',), 'kernel-id': ('KernelId',), 'key-name': ('KeyName',), 'launch-index': ('AmiLaunchIndex',), 'launch-time': ('LaunchTime',), 'monitoring-state': ('Monitoring', 'State'), 'network-interface.addresses.private-ip-address': ('NetworkInterfaces', 'PrivateIpAddress'), 'network-interface.addresses.primary': ('NetworkInterfaces', 'PrivateIpAddresses', 'Primary'), 'network-interface.addresses.association.public-ip': ('NetworkInterfaces', 'PrivateIpAddresses', 'Association', 'PublicIp'), 'network-interface.addresses.association.ip-owner-id': ('NetworkInterfaces', 'PrivateIpAddresses', 'Association', 'IpOwnerId'), 'network-interface.association.public-ip': ('NetworkInterfaces', 'Association', 'PublicIp'), 'network-interface.association.ip-owner-id': ('NetworkInterfaces', 'Association', 'IpOwnerId'), 'network-interface.association.allocation-id': ('ElasticGpuAssociations', 'ElasticGpuId'), 'network-interface.association.association-id': ('ElasticGpuAssociations', 'ElasticGpuAssociationId'), 'network-interface.attachment.attachment-id': ('NetworkInterfaces', 'Attachment', 'AttachmentId'), 'network-interface.attachment.instance-id': ('InstanceId',), 'network-interface.attachment.device-index': ('NetworkInterfaces', 'Attachment', 'DeviceIndex'), 'network-interface.attachment.status': ('NetworkInterfaces', 'Attachment', 'Status'), 'network-interface.attachment.attach-time': ('NetworkInterfaces', 'Attachment', 'AttachTime'), 'network-interface.attachment.delete-on-termination': ('NetworkInterfaces', 'Attachment', 'DeleteOnTermination'), 'network-interface.availability-zone': ('Placement', 'AvailabilityZone'), 'network-interface.description': ('NetworkInterfaces', 'Description'), 'network-interface.group-id': ('NetworkInterfaces', 'Groups', 'GroupId'), 'network-interface.group-name': ('NetworkInterfaces', 'Groups', 'GroupName'), 'network-interface.ipv6-addresses.ipv6-address': ('NetworkInterfaces', 'Ipv6Addresses', 'Ipv6Address'), 'network-interface.mac-address': ('NetworkInterfaces', 'MacAddress'), 'network-interface.network-interface-id': ('NetworkInterfaces', 'NetworkInterfaceId'), 'network-interface.owner-id': ('NetworkInterfaces', 'OwnerId'), 'network-interface.private-dns-name': ('NetworkInterfaces', 'PrivateDnsName'), 'network-interface.requester-managed': ('NetworkInterfaces', 'Association', 'IpOwnerId'), 'network-interface.status': ('NetworkInterfaces', 'Status'), 'network-interface.source-dest-check': ('NetworkInterfaces', 'SourceDestCheck'), 'network-interface.subnet-id': ('NetworkInterfaces', 'SubnetId'), 'network-interface.vpc-id': ('NetworkInterfaces', 'VpcId'), 'placement-group-name': ('Placement', 'GroupName'), 'platform': ('Platform',), 'private-dns-name': ('PrivateDnsName',), 'private-ip-address': ('PrivateIpAddress',), 'product-code': ('ProductCodes', 'ProductCodeId'), 'product-code.type': ('ProductCodes', 'ProductCodeType'), 'ramdisk-id': ('RamdiskId',), 'reason': ('StateTransitionReason',), 'root-device-name': ('RootDeviceName',), 'root-device-type': ('RootDeviceType',), 'source-dest-check': ('SourceDestCheck',), 'spot-instance-request-id': ('SpotInstanceRequestId',), 'state-reason-code': ('StateReason', 'Code'), 'state-reason-message': ('StateReason', 'Message'), 'subnet-id': ('SubnetId',), 'tag': ('Tags',), 'tag-key': ('Tags',), 'tag-value': ('Tags',), 'tenancy': ('Placement', 'Tenancy'), 'virtualization-type': ('VirtualizationType',), 'vpc-id': ('VpcId',)}

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = 'aws_ec2'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.group_prefix = 'aws_ec2_'
        self.boto_profile = None
        self.aws_secret_access_key = None
        self.aws_access_key_id = None
        self.aws_security_token = None
        self.iam_role_arn = None

    def _compile_values(self, obj, attr):
        """
            :param obj: A list or dict of instance attributes
            :param attr: A key
            :return The value(s) found via the attr
        """
        if obj is None:
            return
        temp_obj = []
        if isinstance(obj, list) or isinstance(obj, tuple):
            for each in obj:
                value = self._compile_values(each, attr)
                if value:
                    temp_obj.append(value)
        else:
            temp_obj = obj.get(attr)
        has_indexes = any([isinstance(temp_obj, list), isinstance(temp_obj, tuple)])
        if has_indexes and len(temp_obj) == 1:
            return temp_obj[0]
        return temp_obj

    def _get_boto_attr_chain(self, filter_name, instance):
        """
            :param filter_name: The filter
            :param instance: instance dict returned by boto3 ec2 describe_instances()
        """
        allowed_filters = sorted(list(instance_data_filter_to_boto_attr.keys()) + list(instance_meta_filter_to_boto_attr.keys()))
        if filter_name not in allowed_filters:
            raise AnsibleError("Invalid filter '%s' provided; filter must be one of %s." % (filter_name, allowed_filters))
        if filter_name in instance_data_filter_to_boto_attr:
            boto_attr_list = instance_data_filter_to_boto_attr[filter_name]
        else:
            boto_attr_list = instance_meta_filter_to_boto_attr[filter_name]
        instance_value = instance
        for attribute in boto_attr_list:
            instance_value = self._compile_values(instance_value, attribute)
        return instance_value

    def _get_credentials(self):
        """
            :return A dictionary of boto client credentials
        """
        boto_params = {}
        for credential in (('aws_access_key_id', self.aws_access_key_id), ('aws_secret_access_key', self.aws_secret_access_key), ('aws_session_token', self.aws_security_token)):
            if credential[1]:
                boto_params[credential[0]] = credential[1]
        return boto_params

    def _get_connection(self, credentials, region='us-east-1'):
        try:
            connection = boto3.session.Session(profile_name=self.boto_profile).client('ec2', region, **credentials)
        except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
            if self.boto_profile:
                try:
                    connection = boto3.session.Session(profile_name=self.boto_profile).client('ec2', region)
                except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
                    raise AnsibleError('Insufficient credentials found: %s' % to_native(e))
            else:
                raise AnsibleError('Insufficient credentials found: %s' % to_native(e))
        return connection

    def _boto3_assume_role(self, credentials, region):
        """
        Assume an IAM role passed by iam_role_arn parameter

        :return: a dict containing the credentials of the assumed role
        """
        iam_role_arn = self.iam_role_arn
        try:
            sts_connection = boto3.session.Session(profile_name=self.boto_profile).client('sts', region, **credentials)
            sts_session = sts_connection.assume_role(RoleArn=iam_role_arn, RoleSessionName='ansible_aws_ec2_dynamic_inventory')
            return dict(aws_access_key_id=sts_session['Credentials']['AccessKeyId'], aws_secret_access_key=sts_session['Credentials']['SecretAccessKey'], aws_session_token=sts_session['Credentials']['SessionToken'])
        except botocore.exceptions.ClientError as e:
            raise AnsibleError('Unable to assume IAM role: %s' % to_native(e))

    def _boto3_conn(self, regions):
        """
            :param regions: A list of regions to create a boto3 client

            Generator that yields a boto3 client and the region
        """
        credentials = self._get_credentials()
        iam_role_arn = self.iam_role_arn
        if not regions:
            try:
                client = self._get_connection(credentials)
                resp = client.describe_regions()
                regions = [x['RegionName'] for x in resp.get('Regions', [])]
            except botocore.exceptions.NoRegionError:
                pass
        if not regions:
            session = boto3.Session()
            regions = session.get_available_regions('ec2')
        if not regions:
            raise AnsibleError('Unable to get regions list from available methods, you must specify the "regions" option to continue.')
        for region in regions:
            connection = self._get_connection(credentials, region)
            try:
                if iam_role_arn is not None:
                    assumed_credentials = self._boto3_assume_role(credentials, region)
                else:
                    assumed_credentials = credentials
                connection = boto3.session.Session(profile_name=self.boto_profile).client('ec2', region, **assumed_credentials)
            except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
                if self.boto_profile:
                    try:
                        connection = boto3.session.Session(profile_name=self.boto_profile).client('ec2', region)
                    except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
                        raise AnsibleError('Insufficient credentials found: %s' % to_native(e))
                else:
                    raise AnsibleError('Insufficient credentials found: %s' % to_native(e))
            yield (connection, region)

    def _get_instances_by_region(self, regions, filters, strict_permissions):
        """
           :param regions: a list of regions in which to describe instances
           :param filters: a list of boto3 filter dictionaries
           :param strict_permissions: a boolean determining whether to fail or ignore 403 error codes
           :return A list of instance dictionaries
        """
        all_instances = []
        for (connection, region) in self._boto3_conn(regions):
            try:
                if not any([f['Name'] == 'instance-state-name' for f in filters]):
                    filters.append({'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']})
                paginator = connection.get_paginator('describe_instances')
                reservations = paginator.paginate(Filters=filters).build_full_result().get('Reservations')
                instances = []
                for r in reservations:
                    new_instances = r['Instances']
                    for instance in new_instances:
                        instance.update(self._get_reservation_details(r))
                        if self.get_option('include_extra_api_calls'):
                            instance.update(self._get_event_set_and_persistence(connection, instance['InstanceId'], instance.get('SpotInstanceRequestId')))
                    instances.extend(new_instances)
            except botocore.exceptions.ClientError as e:
                if e.response['ResponseMetadata']['HTTPStatusCode'] == 403 and (not strict_permissions):
                    instances = []
                else:
                    raise AnsibleError('Failed to describe instances: %s' % to_native(e))
            except botocore.exceptions.BotoCoreError as e:
                raise AnsibleError('Failed to describe instances: %s' % to_native(e))
            all_instances.extend(instances)
        return sorted(all_instances, key=lambda x: x['InstanceId'])

    def _get_reservation_details(self, reservation):
        return {'OwnerId': reservation['OwnerId'], 'RequesterId': reservation.get('RequesterId', ''), 'ReservationId': reservation['ReservationId']}

    def _get_event_set_and_persistence(self, connection, instance_id, spot_instance):
        host_vars = {'Events': '', 'Persistent': False}
        try:
            kwargs = {'InstanceIds': [instance_id]}
            host_vars['Events'] = connection.describe_instance_status(**kwargs)['InstanceStatuses'][0].get('Events', '')
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            if not self.get_option('strict_permissions'):
                pass
            else:
                raise AnsibleError('Failed to describe instance status: %s' % to_native(e))
        if spot_instance:
            try:
                kwargs = {'SpotInstanceRequestIds': [spot_instance]}
                host_vars['Persistent'] = bool(connection.describe_spot_instance_requests(**kwargs)['SpotInstanceRequests'][0].get('Type') == 'persistent')
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                if not self.get_option('strict_permissions'):
                    pass
                else:
                    raise AnsibleError('Failed to describe spot instance requests: %s' % to_native(e))
        return host_vars

    def _get_tag_hostname(self, preference, instance):
        tag_hostnames = preference.split('tag:', 1)[1]
        if ',' in tag_hostnames:
            tag_hostnames = tag_hostnames.split(',')
        else:
            tag_hostnames = [tag_hostnames]
        tags = boto3_tag_list_to_ansible_dict(instance.get('Tags', []))
        for v in tag_hostnames:
            if '=' in v:
                (tag_name, tag_value) = v.split('=')
                if tags.get(tag_name) == tag_value:
                    return to_text(tag_name) + '_' + to_text(tag_value)
            else:
                tag_value = tags.get(v)
                if tag_value:
                    return to_text(tag_value)
        return None

    def _get_hostname(self, instance, hostnames):
        """
            :param instance: an instance dict returned by boto3 ec2 describe_instances()
            :param hostnames: a list of hostname destination variables in order of preference
            :return the preferred identifer for the host
        """
        if not hostnames:
            hostnames = ['dns-name', 'private-dns-name']
        hostname = None
        for preference in hostnames:
            if 'tag' in preference:
                if not preference.startswith('tag:'):
                    raise AnsibleError("To name a host by tags name_value, use 'tag:name=value'.")
                hostname = self._get_tag_hostname(preference, instance)
            else:
                hostname = self._get_boto_attr_chain(preference, instance)
            if hostname:
                break
        if hostname:
            if ':' in to_text(hostname):
                return self._sanitize_group_name(to_text(hostname))
            else:
                return to_text(hostname)

    def _query(self, regions, filters, strict_permissions):
        """
            :param regions: a list of regions to query
            :param filters: a list of boto3 filter dictionaries
            :param hostnames: a list of hostname destination variables in order of preference
            :param strict_permissions: a boolean determining whether to fail or ignore 403 error codes
        """
        return {'aws_ec2': self._get_instances_by_region(regions, filters, strict_permissions)}

    def _populate(self, groups, hostnames):
        for group in groups:
            group = self.inventory.add_group(group)
            self._add_hosts(hosts=groups[group], group=group, hostnames=hostnames)
            self.inventory.add_child('all', group)

    def _add_hosts(self, hosts, group, hostnames):
        """
            :param hosts: a list of hosts to be added to a group
            :param group: the name of the group to which the hosts belong
            :param hostnames: a list of hostname destination variables in order of preference
        """
        for host in hosts:
            hostname = self._get_hostname(host, hostnames)
            host = camel_dict_to_snake_dict(host, ignore_list=['Tags'])
            host['tags'] = boto3_tag_list_to_ansible_dict(host.get('tags', []))
            host['placement']['region'] = host['placement']['availability_zone'][:-1]
            if not hostname:
                continue
            self.inventory.add_host(hostname, group=group)
            for (hostvar, hostval) in host.items():
                self.inventory.set_variable(hostname, hostvar, hostval)
            strict = self.get_option('strict')
            self._set_composite_vars(self.get_option('compose'), host, hostname, strict=strict)
            self._add_host_to_composed_groups(self.get_option('groups'), host, hostname, strict=strict)
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host, hostname, strict=strict)

    def _set_credentials(self):
        """
            :param config_data: contents of the inventory config file
        """
        self.boto_profile = self.get_option('aws_profile')
        self.aws_access_key_id = self.get_option('aws_access_key')
        self.aws_secret_access_key = self.get_option('aws_secret_key')
        self.aws_security_token = self.get_option('aws_security_token')
        self.iam_role_arn = self.get_option('iam_role_arn')
        if not self.boto_profile and (not (self.aws_access_key_id and self.aws_secret_access_key)):
            session = botocore.session.get_session()
            try:
                credentials = session.get_credentials().get_frozen_credentials()
            except AttributeError:
                pass
            else:
                self.aws_access_key_id = credentials.access_key
                self.aws_secret_access_key = credentials.secret_key
                self.aws_security_token = credentials.token
        if not self.boto_profile and (not (self.aws_access_key_id and self.aws_secret_access_key)):
            raise AnsibleError('Insufficient boto credentials found. Please provide them in your inventory configuration file or set them as environment variables.')

    def verify_file(self, path):
        """
            :param loader: an ansible.parsing.dataloader.DataLoader object
            :param path: the path to the inventory config file
            :return the contents of the config file
        """
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('aws_ec2.yml', 'aws_ec2.yaml')):
                return True
        display.debug("aws_ec2 inventory filename must end with 'aws_ec2.yml' or 'aws_ec2.yaml'")
        return False

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        if self.get_option('use_contrib_script_compatible_sanitization'):
            self._sanitize_group_name = self._legacy_script_compatible_group_sanitization
        self._set_credentials()
        regions = self.get_option('regions')
        filters = ansible_dict_to_boto3_filter_list(self.get_option('filters'))
        hostnames = self.get_option('hostnames')
        strict_permissions = self.get_option('strict_permissions')
        cache_key = self.get_cache_key(path)
        if cache:
            cache = self.get_option('cache')
        cache_needs_update = False
        if cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        if not cache or cache_needs_update:
            results = self._query(regions, filters, strict_permissions)
        self._populate(results, hostnames)
        if cache_needs_update or (not cache and self.get_option('cache')):
            self._cache[cache_key] = results

    @staticmethod
    def _legacy_script_compatible_group_sanitization(name):
        regex = re.compile('[^A-Za-z0-9\\_\\-]')
        return regex.sub('_', name)

def ansible_dict_to_boto3_filter_list(filters_dict):
    """ Convert an Ansible dict of filters to list of dicts that boto3 can use
    Args:
        filters_dict (dict): Dict of AWS filters.
    Basic Usage:
        >>> filters = {'some-aws-id': 'i-01234567'}
        >>> ansible_dict_to_boto3_filter_list(filters)
        {
            'some-aws-id': 'i-01234567'
        }
    Returns:
        List: List of AWS filters and their values
        [
            {
                'Name': 'some-aws-id',
                'Values': [
                    'i-01234567',
                ]
            }
        ]
    """
    filters_list = []
    for (k, v) in filters_dict.items():
        filter_dict = {'Name': k}
        if isinstance(v, string_types):
            filter_dict['Values'] = [v]
        else:
            filter_dict['Values'] = v
        filters_list.append(filter_dict)
    return filters_list

def boto3_tag_list_to_ansible_dict(tags_list, tag_name_key_name=None, tag_value_key_name=None):
    """ Convert a boto3 list of resource tags to a flat dict of key:value pairs
    Args:
        tags_list (list): List of dicts representing AWS tags.
        tag_name_key_name (str): Value to use as the key for all tag keys (useful because boto3 doesn't always use "Key")
        tag_value_key_name (str): Value to use as the key for all tag values (useful because boto3 doesn't always use "Value")
    Basic Usage:
        >>> tags_list = [{'Key': 'MyTagKey', 'Value': 'MyTagValue'}]
        >>> boto3_tag_list_to_ansible_dict(tags_list)
        [
            {
                'Key': 'MyTagKey',
                'Value': 'MyTagValue'
            }
        ]
    Returns:
        Dict: Dict of key:value pairs representing AWS tags
         {
            'MyTagKey': 'MyTagValue',
        }
    """
    if tag_name_key_name and tag_value_key_name:
        tag_candidates = {tag_name_key_name: tag_value_key_name}
    else:
        tag_candidates = {'key': 'value', 'Key': 'Value'}
    if not tags_list:
        return {}
    for (k, v) in tag_candidates.items():
        if k in tags_list[0] and v in tags_list[0]:
            return dict(((tag[k], tag[v]) for tag in tags_list))
    raise ValueError("Couldn't find tag key (candidates %s) in tag list %s" % (str(tag_candidates), str(tags_list)))

def test_InventoryModule__compile_values():
    ret = InventoryModule()._compile_values()

def test_InventoryModule__get_boto_attr_chain():
    ret = InventoryModule()._get_boto_attr_chain()

def test_InventoryModule__get_credentials():
    ret = InventoryModule()._get_credentials()

def test_InventoryModule__get_connection():
    ret = InventoryModule()._get_connection()

def test_InventoryModule__boto3_assume_role():
    ret = InventoryModule()._boto3_assume_role()

def test_InventoryModule__boto3_conn():
    ret = InventoryModule()._boto3_conn()

def test_InventoryModule__get_instances_by_region():
    ret = InventoryModule()._get_instances_by_region()

def test_InventoryModule__get_reservation_details():
    ret = InventoryModule()._get_reservation_details()

def test_InventoryModule__get_event_set_and_persistence():
    ret = InventoryModule()._get_event_set_and_persistence()

def test_InventoryModule__get_tag_hostname():
    ret = InventoryModule()._get_tag_hostname()

def test_InventoryModule__get_hostname():
    ret = InventoryModule()._get_hostname()

def test_InventoryModule__query():
    ret = InventoryModule()._query()

def test_InventoryModule__populate():
    ret = InventoryModule()._populate()

def test_InventoryModule__add_hosts():
    ret = InventoryModule()._add_hosts()

def test_InventoryModule__set_credentials():
    ret = InventoryModule()._set_credentials()

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()

def test_InventoryModule__legacy_script_compatible_group_sanitization():
    ret = InventoryModule()._legacy_script_compatible_group_sanitization()