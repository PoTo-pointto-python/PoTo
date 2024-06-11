from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: ec2\nshort_description: create, terminate, start or stop an instance in ec2\ndescription:\n    - Creates or terminates ec2 instances.\n    - >\n      Note: This module uses the older boto Python module to interact with the EC2 API.\n      M(ec2) will still receive bug fixes, but no new features.\n      Consider using the M(ec2_instance) module instead.\n      If M(ec2_instance) does not support a feature you need that is available in M(ec2), please\n      file a feature request.\nversion_added: "0.9"\noptions:\n  key_name:\n    description:\n      - Key pair to use on the instance.\n      - The SSH key must already exist in AWS in order to use this argument.\n      - Keys can be created / deleted using the M(ec2_key) module.\n    aliases: [\'keypair\']\n    type: str\n  id:\n    version_added: "1.1"\n    description:\n      - Identifier for this instance or set of instances, so that the module will be idempotent with respect to EC2 instances.\n      - This identifier is valid for at least 24 hours after the termination of the instance, and should not be reused for another call later on.\n      - For details, see the description of client token at U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Run_Instance_Idempotency.html).\n    type: str\n  group:\n    description:\n      - Security group (or list of groups) to use with the instance.\n    aliases: [ \'groups\' ]\n    type: list\n    elements: str\n  group_id:\n    version_added: "1.1"\n    description:\n      - Security group id (or list of ids) to use with the instance.\n    type: list\n    elements: str\n  zone:\n    version_added: "1.2"\n    description:\n      - AWS availability zone in which to launch the instance.\n    aliases: [ \'aws_zone\', \'ec2_zone\' ]\n    type: str\n  instance_type:\n    description:\n      - Instance type to use for the instance, see U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html).\n      - Required when creating a new instance.\n    type: str\n    aliases: [\'type\']\n  tenancy:\n    version_added: "1.9"\n    description:\n      - An instance with a tenancy of C(dedicated) runs on single-tenant hardware and can only be launched into a VPC.\n      - Note that to use dedicated tenancy you MUST specify a I(vpc_subnet_id) as well.\n      - Dedicated tenancy is not available for EC2 "micro" instances.\n    default: default\n    choices: [ "default", "dedicated" ]\n    type: str\n  spot_price:\n    version_added: "1.5"\n    description:\n      - Maximum spot price to bid. If not set, a regular on-demand instance is requested.\n      - A spot request is made with this maximum bid. When it is filled, the instance is started.\n    type: str\n  spot_type:\n    version_added: "2.0"\n    description:\n      - The type of spot request.\n      - After being interrupted a C(persistent) spot instance will be started once there is capacity to fill the request again.\n    default: "one-time"\n    choices: [ "one-time", "persistent" ]\n    type: str\n  image:\n    description:\n       - I(ami) ID to use for the instance.\n       - Required when I(state=present).\n    type: str\n  kernel:\n    description:\n      - Kernel eki to use for the instance.\n    type: str\n  ramdisk:\n    description:\n      - Ramdisk eri to use for the instance.\n    type: str\n  wait:\n    description:\n      - Wait for the instance to reach its desired state before returning.\n      - Does not wait for SSH, see the \'wait_for_connection\' example for details.\n    type: bool\n    default: false\n  wait_timeout:\n    description:\n      - How long before wait gives up, in seconds.\n    default: 300\n    type: int\n  spot_wait_timeout:\n    version_added: "1.5"\n    description:\n      - How long to wait for the spot instance request to be fulfilled. Affects \'Request valid until\' for setting spot request lifespan.\n    default: 600\n    type: int\n  count:\n    description:\n      - Number of instances to launch.\n    default: 1\n    type: int\n  monitoring:\n    version_added: "1.1"\n    description:\n      - Enable detailed monitoring (CloudWatch) for instance.\n    type: bool\n    default: false\n  user_data:\n    version_added: "0.9"\n    description:\n      - Opaque blob of data which is made available to the EC2 instance.\n    type: str\n  instance_tags:\n    version_added: "1.0"\n    description:\n      - A hash/dictionary of tags to add to the new instance or for starting/stopping instance by tag; \'{"key":"value"}\' and \'{"key":"value","key":"value"}\'.\n    type: dict\n  placement_group:\n    version_added: "1.3"\n    description:\n      - Placement group for the instance when using EC2 Clustered Compute.\n    type: str\n  vpc_subnet_id:\n    version_added: "1.1"\n    description:\n      - the subnet ID in which to launch the instance (VPC).\n    type: str\n  assign_public_ip:\n    version_added: "1.5"\n    description:\n      - When provisioning within vpc, assign a public IP address. Boto library must be 2.13.0+.\n    type: bool\n  private_ip:\n    version_added: "1.2"\n    description:\n      - The private ip address to assign the instance (from the vpc subnet).\n    type: str\n  instance_profile_name:\n    version_added: "1.3"\n    description:\n      - Name of the IAM instance profile (i.e. what the EC2 console refers to as an "IAM Role") to use. Boto library must be 2.5.0+.\n    type: str\n  instance_ids:\n    version_added: "1.3"\n    description:\n      - "list of instance ids, currently used for states: absent, running, stopped"\n    aliases: [\'instance_id\']\n    type: list\n    elements: str\n  source_dest_check:\n    version_added: "1.6"\n    description:\n      - Enable or Disable the Source/Destination checks (for NAT instances and Virtual Routers).\n        When initially creating an instance the EC2 API defaults this to C(True).\n    type: bool\n  termination_protection:\n    version_added: "2.0"\n    description:\n      - Enable or Disable the Termination Protection.\n    type: bool\n    default: false\n  instance_initiated_shutdown_behavior:\n    version_added: "2.2"\n    description:\n    - Set whether AWS will Stop or Terminate an instance on shutdown. This parameter is ignored when using instance-store.\n      images (which require termination on shutdown).\n    default: \'stop\'\n    choices: [ "stop", "terminate" ]\n    type: str\n  state:\n    version_added: "1.3"\n    description:\n      - Create, terminate, start, stop or restart instances. The state \'restarted\' was added in Ansible 2.2.\n      - When I(state=absent), I(instance_ids) is required.\n      - When I(state=running), I(state=stopped) or I(state=restarted) then either I(instance_ids) or I(instance_tags) is required.\n    default: \'present\'\n    choices: [\'absent\', \'present\', \'restarted\', \'running\', \'stopped\']\n    type: str\n  volumes:\n    version_added: "1.5"\n    description:\n      - A list of hash/dictionaries of volumes to add to the new instance.\n    type: list\n    elements: dict\n    suboptions:\n      device_name:\n        type: str\n        required: true\n        description:\n          - A name for the device (For example C(/dev/sda)).\n      delete_on_termination:\n        type: bool\n        default: false\n        description:\n          - Whether the volume should be automatically deleted when the instance is terminated.\n      ephemeral:\n        type: str\n        description:\n          - Whether the volume should be ephemeral.\n          - Data on ephemeral volumes is lost when the instance is stopped.\n          - Mutually exclusive with the I(snapshot) parameter.\n      encrypted:\n        type: bool\n        default: false\n        description:\n          - Whether the volume should be encrypted using the \'aws/ebs\' KMS CMK.\n      snapshot:\n        type: str\n        description:\n          - The ID of an EBS snapshot to copy when creating the volume.\n          - Mutually exclusive with the I(ephemeral) parameter.\n      volume_type:\n        type: str\n        description:\n          - The type of volume to create.\n          - See U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html) for more information on the available volume types.\n      volume_size:\n        type: int\n        description:\n          - The size of the volume (in GiB).\n      iops:\n        type: int\n        description:\n          - The number of IOPS per second to provision for the volume.\n          - Required when I(volume_type=io1).\n  ebs_optimized:\n    version_added: "1.6"\n    description:\n      - Whether instance is using optimized EBS volumes, see U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html).\n    default: false\n    type: bool\n  exact_count:\n    version_added: "1.5"\n    description:\n      - An integer value which indicates how many instances that match the \'count_tag\' parameter should be running.\n        Instances are either created or terminated based on this value.\n    type: int\n  count_tag:\n    version_added: "1.5"\n    description:\n      - Used with I(exact_count) to determine how many nodes based on a specific tag criteria should be running.\n        This can be expressed in multiple ways and is shown in the EXAMPLES section.  For instance, one can request 25 servers\n        that are tagged with "class=webserver". The specified tag must already exist or be passed in as the I(instance_tags) option.\n    type: raw\n  network_interfaces:\n    version_added: "2.0"\n    description:\n      - A list of existing network interfaces to attach to the instance at launch. When specifying existing network interfaces,\n        none of the I(assign_public_ip), I(private_ip), I(vpc_subnet_id), I(group), or I(group_id) parameters may be used. (Those parameters are\n        for creating a new network interface at launch.)\n    aliases: [\'network_interface\']\n    type: list\n    elements: str\n  spot_launch_group:\n    version_added: "2.1"\n    description:\n      - Launch group for spot requests, see U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-spot-instances-work.html#spot-launch-group).\n    type: str\nauthor:\n    - "Tim Gerla (@tgerla)"\n    - "Lester Wade (@lwade)"\n    - "Seth Vidal (@skvidal)"\nextends_documentation_fragment:\n    - aws\n    - ec2\n'
EXAMPLES = '\n# Note: These examples do not set authentication details, see the AWS Guide for details.\n\n# Basic provisioning example\n- ec2:\n    key_name: mykey\n    instance_type: t2.micro\n    image: ami-123456\n    wait: yes\n    group: webserver\n    count: 3\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n# Advanced example with tagging and CloudWatch\n- ec2:\n    key_name: mykey\n    group: databases\n    instance_type: t2.micro\n    image: ami-123456\n    wait: yes\n    wait_timeout: 500\n    count: 5\n    instance_tags:\n       db: postgres\n    monitoring: yes\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n# Single instance with additional IOPS volume from snapshot and volume delete on termination\n- ec2:\n    key_name: mykey\n    group: webserver\n    instance_type: c3.medium\n    image: ami-123456\n    wait: yes\n    wait_timeout: 500\n    volumes:\n      - device_name: /dev/sdb\n        snapshot: snap-abcdef12\n        volume_type: io1\n        iops: 1000\n        volume_size: 100\n        delete_on_termination: true\n    monitoring: yes\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n# Single instance with ssd gp2 root volume\n- ec2:\n    key_name: mykey\n    group: webserver\n    instance_type: c3.medium\n    image: ami-123456\n    wait: yes\n    wait_timeout: 500\n    volumes:\n      - device_name: /dev/xvda\n        volume_type: gp2\n        volume_size: 8\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n    count_tag:\n      Name: dbserver\n    exact_count: 1\n\n# Multiple groups example\n- ec2:\n    key_name: mykey\n    group: [\'databases\', \'internal-services\', \'sshable\', \'and-so-forth\']\n    instance_type: m1.large\n    image: ami-6e649707\n    wait: yes\n    wait_timeout: 500\n    count: 5\n    instance_tags:\n        db: postgres\n    monitoring: yes\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n# Multiple instances with additional volume from snapshot\n- ec2:\n    key_name: mykey\n    group: webserver\n    instance_type: m1.large\n    image: ami-6e649707\n    wait: yes\n    wait_timeout: 500\n    count: 5\n    volumes:\n    - device_name: /dev/sdb\n      snapshot: snap-abcdef12\n      volume_size: 10\n    monitoring: yes\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n# Dedicated tenancy example\n- local_action:\n    module: ec2\n    assign_public_ip: yes\n    group_id: sg-1dc53f72\n    key_name: mykey\n    image: ami-6e649707\n    instance_type: m1.small\n    tenancy: dedicated\n    vpc_subnet_id: subnet-29e63245\n    wait: yes\n\n# Spot instance example\n- ec2:\n    spot_price: 0.24\n    spot_wait_timeout: 600\n    keypair: mykey\n    group_id: sg-1dc53f72\n    instance_type: m1.small\n    image: ami-6e649707\n    wait: yes\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n    spot_launch_group: report_generators\n    instance_initiated_shutdown_behavior: terminate\n\n# Examples using pre-existing network interfaces\n- ec2:\n    key_name: mykey\n    instance_type: t2.small\n    image: ami-f005ba11\n    network_interface: eni-deadbeef\n\n- ec2:\n    key_name: mykey\n    instance_type: t2.small\n    image: ami-f005ba11\n    network_interfaces: [\'eni-deadbeef\', \'eni-5ca1ab1e\']\n\n# Launch instances, runs some tasks\n# and then terminate them\n\n- name: Create a sandbox instance\n  hosts: localhost\n  gather_facts: False\n  vars:\n    keypair: my_keypair\n    instance_type: m1.small\n    security_group: my_securitygroup\n    image: my_ami_id\n    region: us-east-1\n  tasks:\n    - name: Launch instance\n      ec2:\n         key_name: "{{ keypair }}"\n         group: "{{ security_group }}"\n         instance_type: "{{ instance_type }}"\n         image: "{{ image }}"\n         wait: true\n         region: "{{ region }}"\n         vpc_subnet_id: subnet-29e63245\n         assign_public_ip: yes\n      register: ec2\n\n    - name: Add new instance to host group\n      add_host:\n        hostname: "{{ item.public_ip }}"\n        groupname: launched\n      loop: "{{ ec2.instances }}"\n\n    - name: Wait for SSH to come up\n      delegate_to: "{{ item.public_dns_name }}"\n      wait_for_connection:\n        delay: 60\n        timeout: 320\n      loop: "{{ ec2.instances }}"\n\n- name: Configure instance(s)\n  hosts: launched\n  become: True\n  gather_facts: True\n  roles:\n    - my_awesome_role\n    - my_awesome_test\n\n- name: Terminate instances\n  hosts: localhost\n  tasks:\n    - name: Terminate instances that were previously launched\n      ec2:\n        state: \'absent\'\n        instance_ids: \'{{ ec2.instance_ids }}\'\n\n# Start a few existing instances, run some tasks\n# and stop the instances\n\n- name: Start sandbox instances\n  hosts: localhost\n  gather_facts: false\n  vars:\n    instance_ids:\n      - \'i-xxxxxx\'\n      - \'i-xxxxxx\'\n      - \'i-xxxxxx\'\n    region: us-east-1\n  tasks:\n    - name: Start the sandbox instances\n      ec2:\n        instance_ids: \'{{ instance_ids }}\'\n        region: \'{{ region }}\'\n        state: running\n        wait: True\n        vpc_subnet_id: subnet-29e63245\n        assign_public_ip: yes\n  roles:\n    - do_neat_stuff\n    - do_more_neat_stuff\n\n- name: Stop sandbox instances\n  hosts: localhost\n  gather_facts: false\n  vars:\n    instance_ids:\n      - \'i-xxxxxx\'\n      - \'i-xxxxxx\'\n      - \'i-xxxxxx\'\n    region: us-east-1\n  tasks:\n    - name: Stop the sandbox instances\n      ec2:\n        instance_ids: \'{{ instance_ids }}\'\n        region: \'{{ region }}\'\n        state: stopped\n        wait: True\n        vpc_subnet_id: subnet-29e63245\n        assign_public_ip: yes\n\n#\n# Start stopped instances specified by tag\n#\n- local_action:\n    module: ec2\n    instance_tags:\n        Name: ExtraPower\n    state: running\n\n#\n# Restart instances specified by tag\n#\n- local_action:\n    module: ec2\n    instance_tags:\n        Name: ExtraPower\n    state: restarted\n\n#\n# Enforce that 5 instances with a tag "foo" are running\n# (Highly recommended!)\n#\n\n- ec2:\n    key_name: mykey\n    instance_type: c1.medium\n    image: ami-40603AD1\n    wait: yes\n    group: webserver\n    instance_tags:\n        foo: bar\n    exact_count: 5\n    count_tag: foo\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n#\n# Enforce that 5 running instances named "database" with a "dbtype" of "postgres"\n#\n\n- ec2:\n    key_name: mykey\n    instance_type: c1.medium\n    image: ami-40603AD1\n    wait: yes\n    group: webserver\n    instance_tags:\n        Name: database\n        dbtype: postgres\n    exact_count: 5\n    count_tag:\n        Name: database\n        dbtype: postgres\n    vpc_subnet_id: subnet-29e63245\n    assign_public_ip: yes\n\n#\n# count_tag complex argument examples\n#\n\n    # instances with tag foo\n- ec2:\n    count_tag:\n        foo:\n\n    # instances with tag foo=bar\n- ec2:\n    count_tag:\n        foo: bar\n\n    # instances with tags foo=bar & baz\n- ec2:\n    count_tag:\n        foo: bar\n        baz:\n\n    # instances with tags foo & bar & baz=bang\n- ec2:\n    count_tag:\n        - foo\n        - bar\n        - baz: bang\n\n'
import time
import datetime
import traceback
from ast import literal_eval
from distutils.version import LooseVersion
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import get_aws_connection_info, ec2_argument_spec, ec2_connect
from ansible.module_utils.six import get_function_code, string_types
from ansible.module_utils._text import to_bytes, to_text
try:
    import boto.ec2
    from boto.ec2.blockdevicemapping import BlockDeviceType, BlockDeviceMapping
    from boto.exception import EC2ResponseError
    from boto import connect_ec2_endpoint
    from boto import connect_vpc
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def find_running_instances_by_count_tag(module, ec2, vpc, count_tag, zone=None):
    state = module.params.get('state')
    if state not in ['running', 'stopped']:
        state = None
    reservations = get_reservations(module, ec2, vpc, tags=count_tag, state=state, zone=zone)
    instances = []
    for res in reservations:
        if hasattr(res, 'instances'):
            for inst in res.instances:
                if inst.state == 'terminated' or inst.state == 'shutting-down':
                    continue
                instances.append(inst)
    return (reservations, instances)

def _set_none_to_blank(dictionary):
    result = dictionary
    for k in result:
        if isinstance(result[k], dict):
            result[k] = _set_none_to_blank(result[k])
        elif not result[k]:
            result[k] = ''
    return result

def get_reservations(module, ec2, vpc, tags=None, state=None, zone=None):
    filters = dict()
    vpc_subnet_id = module.params.get('vpc_subnet_id')
    vpc_id = None
    if vpc_subnet_id:
        filters.update({'subnet-id': vpc_subnet_id})
        if vpc:
            vpc_id = vpc.get_all_subnets(subnet_ids=[vpc_subnet_id])[0].vpc_id
    if vpc_id:
        filters.update({'vpc-id': vpc_id})
    if tags is not None:
        if isinstance(tags, str):
            try:
                tags = literal_eval(tags)
            except Exception:
                pass
        if isinstance(tags, int):
            tags = to_text(tags)
        if isinstance(tags, str):
            filters.update({'tag-key': tags})
        if isinstance(tags, list):
            for x in tags:
                if isinstance(x, dict):
                    x = _set_none_to_blank(x)
                    filters.update(dict((('tag:' + tn, tv) for (tn, tv) in x.items())))
                else:
                    filters.update({'tag-key': x})
        if isinstance(tags, dict):
            tags = _set_none_to_blank(tags)
            filters.update(dict((('tag:' + tn, tv) for (tn, tv) in tags.items())))
        if not filters:
            module.fail_json(msg='Filters based on tag is empty => tags: %s' % tags)
    if state:
        filters.update({'instance-state-name': state})
    if zone:
        filters.update({'availability-zone': zone})
    if module.params.get('id'):
        filters['client-token'] = module.params['id']
    results = ec2.get_all_instances(filters=filters)
    return results

def get_instance_info(inst):
    """
    Retrieves instance information from an instance
    ID and returns it as a dictionary
    """
    instance_info = {'id': inst.id, 'ami_launch_index': inst.ami_launch_index, 'private_ip': inst.private_ip_address, 'private_dns_name': inst.private_dns_name, 'public_ip': inst.ip_address, 'dns_name': inst.dns_name, 'public_dns_name': inst.public_dns_name, 'state_code': inst.state_code, 'architecture': inst.architecture, 'image_id': inst.image_id, 'key_name': inst.key_name, 'placement': inst.placement, 'region': inst.placement[:-1], 'kernel': inst.kernel, 'ramdisk': inst.ramdisk, 'launch_time': inst.launch_time, 'instance_type': inst.instance_type, 'root_device_type': inst.root_device_type, 'root_device_name': inst.root_device_name, 'state': inst.state, 'hypervisor': inst.hypervisor, 'tags': inst.tags, 'groups': dict(((group.id, group.name) for group in inst.groups))}
    try:
        instance_info['virtualization_type'] = getattr(inst, 'virtualization_type')
    except AttributeError:
        instance_info['virtualization_type'] = None
    try:
        instance_info['ebs_optimized'] = getattr(inst, 'ebs_optimized')
    except AttributeError:
        instance_info['ebs_optimized'] = False
    try:
        bdm_dict = {}
        bdm = getattr(inst, 'block_device_mapping')
        for device_name in bdm.keys():
            bdm_dict[device_name] = {'status': bdm[device_name].status, 'volume_id': bdm[device_name].volume_id, 'delete_on_termination': bdm[device_name].delete_on_termination}
        instance_info['block_device_mapping'] = bdm_dict
    except AttributeError:
        instance_info['block_device_mapping'] = False
    try:
        instance_info['tenancy'] = getattr(inst, 'placement_tenancy')
    except AttributeError:
        instance_info['tenancy'] = 'default'
    return instance_info

def boto_supports_associate_public_ip_address(ec2):
    """
    Check if Boto library has associate_public_ip_address in the NetworkInterfaceSpecification
    class. Added in Boto 2.13.0

    ec2: authenticated ec2 connection object

    Returns:
        True if Boto library accepts associate_public_ip_address argument, else false
    """
    try:
        network_interface = boto.ec2.networkinterface.NetworkInterfaceSpecification()
        getattr(network_interface, 'associate_public_ip_address')
        return True
    except AttributeError:
        return False

def boto_supports_profile_name_arg(ec2):
    """
    Check if Boto library has instance_profile_name argument. instance_profile_name has been added in Boto 2.5.0

    ec2: authenticated ec2 connection object

    Returns:
        True if Boto library accept instance_profile_name argument, else false
    """
    run_instances_method = getattr(ec2, 'run_instances')
    return 'instance_profile_name' in get_function_code(run_instances_method).co_varnames

def boto_supports_volume_encryption():
    """
    Check if Boto library supports encryption of EBS volumes (added in 2.29.0)

    Returns:
        True if boto library has the named param as an argument on the request_spot_instances method, else False
    """
    return hasattr(boto, 'Version') and LooseVersion(boto.Version) >= LooseVersion('2.29.0')

def create_block_device(module, ec2, volume):
    MAX_IOPS_TO_SIZE_RATIO = 30
    volume_type = volume.get('volume_type')
    if 'snapshot' not in volume and 'ephemeral' not in volume:
        if 'volume_size' not in volume:
            module.fail_json(msg='Size must be specified when creating a new volume or modifying the root volume')
    if 'snapshot' in volume:
        if volume_type == 'io1' and 'iops' not in volume:
            module.fail_json(msg='io1 volumes must have an iops value set')
        if 'iops' in volume:
            snapshot = ec2.get_all_snapshots(snapshot_ids=[volume['snapshot']])[0]
            size = volume.get('volume_size', snapshot.volume_size)
            if int(volume['iops']) > MAX_IOPS_TO_SIZE_RATIO * size:
                module.fail_json(msg='IOPS must be at most %d times greater than size' % MAX_IOPS_TO_SIZE_RATIO)
    if 'ephemeral' in volume:
        if 'snapshot' in volume:
            module.fail_json(msg='Cannot set both ephemeral and snapshot')
    if boto_supports_volume_encryption():
        return BlockDeviceType(snapshot_id=volume.get('snapshot'), ephemeral_name=volume.get('ephemeral'), size=volume.get('volume_size'), volume_type=volume_type, delete_on_termination=volume.get('delete_on_termination', False), iops=volume.get('iops'), encrypted=volume.get('encrypted', None))
    else:
        return BlockDeviceType(snapshot_id=volume.get('snapshot'), ephemeral_name=volume.get('ephemeral'), size=volume.get('volume_size'), volume_type=volume_type, delete_on_termination=volume.get('delete_on_termination', False), iops=volume.get('iops'))

def boto_supports_param_in_spot_request(ec2, param):
    """
    Check if Boto library has a <param> in its request_spot_instances() method. For example, the placement_group parameter wasn't added until 2.3.0.

    ec2: authenticated ec2 connection object

    Returns:
        True if boto library has the named param as an argument on the request_spot_instances method, else False
    """
    method = getattr(ec2, 'request_spot_instances')
    return param in get_function_code(method).co_varnames

def await_spot_requests(module, ec2, spot_requests, count):
    """
    Wait for a group of spot requests to be fulfilled, or fail.

    module: Ansible module object
    ec2: authenticated ec2 connection object
    spot_requests: boto.ec2.spotinstancerequest.SpotInstanceRequest object returned by ec2.request_spot_instances
    count: Total number of instances to be created by the spot requests

    Returns:
        list of instance ID's created by the spot request(s)
    """
    spot_wait_timeout = int(module.params.get('spot_wait_timeout'))
    wait_complete = time.time() + spot_wait_timeout
    spot_req_inst_ids = dict()
    while time.time() < wait_complete:
        reqs = ec2.get_all_spot_instance_requests()
        for sirb in spot_requests:
            if sirb.id in spot_req_inst_ids:
                continue
            for sir in reqs:
                if sir.id != sirb.id:
                    continue
                if sir.instance_id is not None:
                    spot_req_inst_ids[sirb.id] = sir.instance_id
                elif sir.state == 'open':
                    continue
                elif sir.state == 'active':
                    continue
                elif sir.state == 'failed':
                    module.fail_json(msg='Spot instance request %s failed with status %s and fault %s:%s' % (sir.id, sir.status.code, sir.fault.code, sir.fault.message))
                elif sir.state == 'cancelled':
                    module.fail_json(msg='Spot instance request %s was cancelled before it could be fulfilled.' % sir.id)
                elif sir.state == 'closed':
                    if sir.status.code == 'instance-terminated-by-user':
                        pass
                    else:
                        spot_msg = 'Spot instance request %s was closed by AWS with the status %s and fault %s:%s'
                        module.fail_json(msg=spot_msg % (sir.id, sir.status.code, sir.fault.code, sir.fault.message))
        if len(spot_req_inst_ids) < count:
            time.sleep(5)
        else:
            return list(spot_req_inst_ids.values())
    module.fail_json(msg='wait for spot requests timeout on %s' % time.asctime())

def enforce_count(module, ec2, vpc):
    exact_count = module.params.get('exact_count')
    count_tag = module.params.get('count_tag')
    zone = module.params.get('zone')
    if exact_count and count_tag is None:
        module.fail_json(msg="you must use the 'count_tag' option with exact_count")
    (reservations, instances) = find_running_instances_by_count_tag(module, ec2, vpc, count_tag, zone)
    changed = None
    checkmode = False
    instance_dict_array = []
    changed_instance_ids = None
    if len(instances) == exact_count:
        changed = False
    elif len(instances) < exact_count:
        changed = True
        to_create = exact_count - len(instances)
        if not checkmode:
            (instance_dict_array, changed_instance_ids, changed) = create_instances(module, ec2, vpc, override_count=to_create)
            for inst in instance_dict_array:
                instances.append(inst)
    elif len(instances) > exact_count:
        changed = True
        to_remove = len(instances) - exact_count
        if not checkmode:
            all_instance_ids = sorted([x.id for x in instances])
            remove_ids = all_instance_ids[0:to_remove]
            instances = [x for x in instances if x.id not in remove_ids]
            (changed, instance_dict_array, changed_instance_ids) = terminate_instances(module, ec2, remove_ids)
            terminated_list = []
            for inst in instance_dict_array:
                inst['state'] = 'terminated'
                terminated_list.append(inst)
            instance_dict_array = terminated_list
    all_instances = []
    for inst in instances:
        if not isinstance(inst, dict):
            warn_if_public_ip_assignment_changed(module, inst)
            inst = get_instance_info(inst)
        all_instances.append(inst)
    return (all_instances, instance_dict_array, changed_instance_ids, changed)

def create_instances(module, ec2, vpc, override_count=None):
    """
    Creates new instances

    module : AnsibleModule object
    ec2: authenticated ec2 connection object

    Returns:
        A list of dictionaries with instance information
        about the instances that were launched
    """
    key_name = module.params.get('key_name')
    id = module.params.get('id')
    group_name = module.params.get('group')
    group_id = module.params.get('group_id')
    zone = module.params.get('zone')
    instance_type = module.params.get('instance_type')
    tenancy = module.params.get('tenancy')
    spot_price = module.params.get('spot_price')
    spot_type = module.params.get('spot_type')
    image = module.params.get('image')
    if override_count:
        count = override_count
    else:
        count = module.params.get('count')
    monitoring = module.params.get('monitoring')
    kernel = module.params.get('kernel')
    ramdisk = module.params.get('ramdisk')
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))
    spot_wait_timeout = int(module.params.get('spot_wait_timeout'))
    placement_group = module.params.get('placement_group')
    user_data = module.params.get('user_data')
    instance_tags = module.params.get('instance_tags')
    vpc_subnet_id = module.params.get('vpc_subnet_id')
    assign_public_ip = module.boolean(module.params.get('assign_public_ip'))
    private_ip = module.params.get('private_ip')
    instance_profile_name = module.params.get('instance_profile_name')
    volumes = module.params.get('volumes')
    ebs_optimized = module.params.get('ebs_optimized')
    exact_count = module.params.get('exact_count')
    count_tag = module.params.get('count_tag')
    source_dest_check = module.boolean(module.params.get('source_dest_check'))
    termination_protection = module.boolean(module.params.get('termination_protection'))
    network_interfaces = module.params.get('network_interfaces')
    spot_launch_group = module.params.get('spot_launch_group')
    instance_initiated_shutdown_behavior = module.params.get('instance_initiated_shutdown_behavior')
    vpc_id = None
    if vpc_subnet_id:
        if not vpc:
            module.fail_json(msg='region must be specified')
        else:
            vpc_id = vpc.get_all_subnets(subnet_ids=[vpc_subnet_id])[0].vpc_id
    else:
        vpc_id = None
    try:
        if group_name:
            if vpc_id:
                grp_details = ec2.get_all_security_groups(filters={'vpc_id': vpc_id})
            else:
                grp_details = ec2.get_all_security_groups()
            if isinstance(group_name, string_types):
                group_name = [group_name]
            unmatched = set(group_name).difference((str(grp.name) for grp in grp_details))
            if len(unmatched) > 0:
                module.fail_json(msg='The following group names are not valid: %s' % ', '.join(unmatched))
            group_id = [str(grp.id) for grp in grp_details if str(grp.name) in group_name]
        elif group_id:
            if isinstance(group_id, string_types):
                group_id = [group_id]
            grp_details = ec2.get_all_security_groups(group_ids=group_id)
            group_name = [grp_item.name for grp_item in grp_details]
    except boto.exception.NoAuthHandlerFound as e:
        module.fail_json(msg=str(e))
    running_instances = []
    count_remaining = int(count)
    if id is not None:
        filter_dict = {'client-token': id, 'instance-state-name': 'running'}
        previous_reservations = ec2.get_all_instances(None, filter_dict)
        for res in previous_reservations:
            for prev_instance in res.instances:
                running_instances.append(prev_instance)
        count_remaining = count_remaining - len(running_instances)
    if count_remaining == 0:
        changed = False
    else:
        changed = True
        try:
            params = {'image_id': image, 'key_name': key_name, 'monitoring_enabled': monitoring, 'placement': zone, 'instance_type': instance_type, 'kernel_id': kernel, 'ramdisk_id': ramdisk}
            if user_data is not None:
                params['user_data'] = to_bytes(user_data, errors='surrogate_or_strict')
            if ebs_optimized:
                params['ebs_optimized'] = ebs_optimized
            if not spot_price:
                params['tenancy'] = tenancy
            if boto_supports_profile_name_arg(ec2):
                params['instance_profile_name'] = instance_profile_name
            elif instance_profile_name is not None:
                module.fail_json(msg='instance_profile_name parameter requires Boto version 2.5.0 or higher')
            if assign_public_ip is not None:
                if not boto_supports_associate_public_ip_address(ec2):
                    module.fail_json(msg='assign_public_ip parameter requires Boto version 2.13.0 or higher.')
                elif not vpc_subnet_id:
                    module.fail_json(msg='assign_public_ip only available with vpc_subnet_id')
                else:
                    if private_ip:
                        interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=vpc_subnet_id, private_ip_address=private_ip, groups=group_id, associate_public_ip_address=assign_public_ip)
                    else:
                        interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id=vpc_subnet_id, groups=group_id, associate_public_ip_address=assign_public_ip)
                    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
                    params['network_interfaces'] = interfaces
            elif network_interfaces:
                if isinstance(network_interfaces, string_types):
                    network_interfaces = [network_interfaces]
                interfaces = []
                for (i, network_interface_id) in enumerate(network_interfaces):
                    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(network_interface_id=network_interface_id, device_index=i)
                    interfaces.append(interface)
                params['network_interfaces'] = boto.ec2.networkinterface.NetworkInterfaceCollection(*interfaces)
            else:
                params['subnet_id'] = vpc_subnet_id
                if vpc_subnet_id:
                    params['security_group_ids'] = group_id
                else:
                    params['security_groups'] = group_name
            if volumes:
                bdm = BlockDeviceMapping()
                for volume in volumes:
                    if 'device_name' not in volume:
                        module.fail_json(msg='Device name must be set for volume')
                    if 'volume_size' not in volume or int(volume['volume_size']) > 0:
                        bdm[volume['device_name']] = create_block_device(module, ec2, volume)
                params['block_device_map'] = bdm
            if not spot_price:
                if assign_public_ip is not None and private_ip:
                    params.update(dict(min_count=count_remaining, max_count=count_remaining, client_token=id, placement_group=placement_group))
                else:
                    params.update(dict(min_count=count_remaining, max_count=count_remaining, client_token=id, placement_group=placement_group, private_ip_address=private_ip))
                params['instance_initiated_shutdown_behavior'] = instance_initiated_shutdown_behavior or 'stop'
                try:
                    res = ec2.run_instances(**params)
                except boto.exception.EC2ResponseError as e:
                    if params['instance_initiated_shutdown_behavior'] != 'terminate' and 'InvalidParameterCombination' == e.error_code:
                        params['instance_initiated_shutdown_behavior'] = 'terminate'
                        res = ec2.run_instances(**params)
                    else:
                        raise
                instids = [i.id for i in res.instances]
                while True:
                    try:
                        ec2.get_all_instances(instids)
                        break
                    except boto.exception.EC2ResponseError as e:
                        if '<Code>InvalidInstanceID.NotFound</Code>' in str(e):
                            continue
                        else:
                            module.fail_json(msg=str(e))
                terminated_instances = [str(instance.id) for instance in res.instances if instance.state == 'terminated']
                if terminated_instances:
                    module.fail_json(msg='Instances with id(s) %s ' % terminated_instances + 'were created previously but have since been terminated - ' + "use a (possibly different) 'instanceid' parameter")
            else:
                if private_ip:
                    module.fail_json(msg='private_ip only available with on-demand (non-spot) instances')
                if boto_supports_param_in_spot_request(ec2, 'placement_group'):
                    params['placement_group'] = placement_group
                elif placement_group:
                    module.fail_json(msg='placement_group parameter requires Boto version 2.3.0 or higher.')
                if instance_initiated_shutdown_behavior and instance_initiated_shutdown_behavior != 'terminate':
                    module.fail_json(msg='instance_initiated_shutdown_behavior=stop is not supported for spot instances.')
                if spot_launch_group and isinstance(spot_launch_group, string_types):
                    params['launch_group'] = spot_launch_group
                params.update(dict(count=count_remaining, type=spot_type))
                utc_valid_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=spot_wait_timeout)
                params['valid_until'] = utc_valid_until.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                res = ec2.request_spot_instances(spot_price, **params)
                if wait:
                    instids = await_spot_requests(module, ec2, res, count)
                else:
                    instids = []
        except boto.exception.BotoServerError as e:
            module.fail_json(msg='Instance creation failed => %s: %s' % (e.error_code, e.error_message))
        num_running = 0
        wait_timeout = time.time() + wait_timeout
        res_list = ()
        while wait_timeout > time.time() and num_running < len(instids):
            try:
                res_list = ec2.get_all_instances(instids)
            except boto.exception.BotoServerError as e:
                if e.error_code == 'InvalidInstanceID.NotFound':
                    time.sleep(1)
                    continue
                else:
                    raise
            num_running = 0
            for res in res_list:
                num_running += len([i for i in res.instances if i.state == 'running'])
            if len(res_list) <= 0:
                time.sleep(1)
                continue
            if wait and num_running < len(instids):
                time.sleep(5)
            else:
                break
        if wait and wait_timeout <= time.time():
            module.fail_json(msg='wait for instances running timeout on %s' % time.asctime())
        for res in res_list:
            running_instances.extend(res.instances)
        if source_dest_check is False:
            for inst in res.instances:
                inst.modify_attribute('sourceDestCheck', False)
        if termination_protection is True:
            for inst in res.instances:
                inst.modify_attribute('disableApiTermination', True)
        if instance_tags and instids:
            try:
                ec2.create_tags(instids, instance_tags)
            except boto.exception.EC2ResponseError as e:
                module.fail_json(msg='Instance tagging failed => %s: %s' % (e.error_code, e.error_message))
    instance_dict_array = []
    created_instance_ids = []
    for inst in running_instances:
        inst.update()
        d = get_instance_info(inst)
        created_instance_ids.append(inst.id)
        instance_dict_array.append(d)
    return (instance_dict_array, created_instance_ids, changed)

def terminate_instances(module, ec2, instance_ids):
    """
    Terminates a list of instances

    module: Ansible module object
    ec2: authenticated ec2 connection object
    termination_list: a list of instances to terminate in the form of
      [ {id: <inst-id>}, ..]

    Returns a dictionary of instance information
    about the instances terminated.

    If the instance to be terminated is running
    "changed" will be set to False.

    """
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))
    changed = False
    instance_dict_array = []
    if not isinstance(instance_ids, list) or len(instance_ids) < 1:
        module.fail_json(msg='instance_ids should be a list of instances, aborting')
    terminated_instance_ids = []
    for res in ec2.get_all_instances(instance_ids):
        for inst in res.instances:
            if inst.state == 'running' or inst.state == 'stopped':
                terminated_instance_ids.append(inst.id)
                instance_dict_array.append(get_instance_info(inst))
                try:
                    ec2.terminate_instances([inst.id])
                except EC2ResponseError as e:
                    module.fail_json(msg='Unable to terminate instance {0}, error: {1}'.format(inst.id, e))
                changed = True
    if wait:
        num_terminated = 0
        wait_timeout = time.time() + wait_timeout
        while wait_timeout > time.time() and num_terminated < len(terminated_instance_ids):
            response = ec2.get_all_instances(instance_ids=terminated_instance_ids, filters={'instance-state-name': 'terminated'})
            try:
                num_terminated = sum([len(res.instances) for res in response])
            except Exception as e:
                time.sleep(1)
                continue
            if num_terminated < len(terminated_instance_ids):
                time.sleep(5)
        if wait_timeout < time.time() and num_terminated < len(terminated_instance_ids):
            module.fail_json(msg='wait for instance termination timeout on %s' % time.asctime())
        instance_dict_array = []
        for res in ec2.get_all_instances(instance_ids=terminated_instance_ids, filters={'instance-state-name': 'terminated'}):
            for inst in res.instances:
                instance_dict_array.append(get_instance_info(inst))
    return (changed, instance_dict_array, terminated_instance_ids)

def startstop_instances(module, ec2, instance_ids, state, instance_tags):
    """
    Starts or stops a list of existing instances

    module: Ansible module object
    ec2: authenticated ec2 connection object
    instance_ids: The list of instances to start in the form of
      [ {id: <inst-id>}, ..]
    instance_tags: A dict of tag keys and values in the form of
      {key: value, ... }
    state: Intended state ("running" or "stopped")

    Returns a dictionary of instance information
    about the instances started/stopped.

    If the instance was not able to change state,
    "changed" will be set to False.

    Note that if instance_ids and instance_tags are both non-empty,
    this method will process the intersection of the two
    """
    wait = module.params.get('wait')
    wait_timeout = int(module.params.get('wait_timeout'))
    group_id = module.params.get('group_id')
    group_name = module.params.get('group')
    changed = False
    instance_dict_array = []
    if not isinstance(instance_ids, list) or len(instance_ids) < 1:
        if not instance_tags:
            module.fail_json(msg='instance_ids should be a list of instances, aborting')
    filters = {}
    if instance_tags:
        for (key, value) in instance_tags.items():
            filters['tag:' + key] = value
    if module.params.get('id'):
        filters['client-token'] = module.params['id']
    existing_instances_array = []
    for res in ec2.get_all_instances(instance_ids, filters=filters):
        for inst in res.instances:
            warn_if_public_ip_assignment_changed(module, inst)
            changed = check_source_dest_attr(module, inst, ec2) or check_termination_protection(module, inst) or changed
            if inst.vpc_id and group_name:
                grp_details = ec2.get_all_security_groups(filters={'vpc_id': inst.vpc_id})
                if isinstance(group_name, string_types):
                    group_name = [group_name]
                unmatched = set(group_name) - set((to_text(grp.name) for grp in grp_details))
                if unmatched:
                    module.fail_json(msg='The following group names are not valid: %s' % ', '.join(unmatched))
                group_ids = [to_text(grp.id) for grp in grp_details if to_text(grp.name) in group_name]
            elif inst.vpc_id and group_id:
                if isinstance(group_id, string_types):
                    group_id = [group_id]
                grp_details = ec2.get_all_security_groups(group_ids=group_id)
                group_ids = [grp_item.id for grp_item in grp_details]
            if inst.vpc_id and (group_name or group_id):
                if set((sg.id for sg in inst.groups)) != set(group_ids):
                    changed = inst.modify_attribute('groupSet', group_ids)
            if inst.state != state:
                instance_dict_array.append(get_instance_info(inst))
                try:
                    if state == 'running':
                        inst.start()
                    else:
                        inst.stop()
                except EC2ResponseError as e:
                    module.fail_json(msg='Unable to change state for instance {0}, error: {1}'.format(inst.id, e))
                changed = True
            existing_instances_array.append(inst.id)
    instance_ids = list(set(existing_instances_array + (instance_ids or [])))
    wait_timeout = time.time() + wait_timeout
    while wait and wait_timeout > time.time():
        instance_dict_array = []
        matched_instances = []
        for res in ec2.get_all_instances(instance_ids):
            for i in res.instances:
                if i.state == state:
                    instance_dict_array.append(get_instance_info(i))
                    matched_instances.append(i)
        if len(matched_instances) < len(instance_ids):
            time.sleep(5)
        else:
            break
    if wait and wait_timeout <= time.time():
        module.fail_json(msg='wait for instances running timeout on %s' % time.asctime())
    return (changed, instance_dict_array, instance_ids)

def restart_instances(module, ec2, instance_ids, state, instance_tags):
    """
    Restarts a list of existing instances

    module: Ansible module object
    ec2: authenticated ec2 connection object
    instance_ids: The list of instances to start in the form of
      [ {id: <inst-id>}, ..]
    instance_tags: A dict of tag keys and values in the form of
      {key: value, ... }
    state: Intended state ("restarted")

    Returns a dictionary of instance information
    about the instances.

    If the instance was not able to change state,
    "changed" will be set to False.

    Wait will not apply here as this is a OS level operation.

    Note that if instance_ids and instance_tags are both non-empty,
    this method will process the intersection of the two.
    """
    changed = False
    instance_dict_array = []
    if not isinstance(instance_ids, list) or len(instance_ids) < 1:
        if not instance_tags:
            module.fail_json(msg='instance_ids should be a list of instances, aborting')
    filters = {}
    if instance_tags:
        for (key, value) in instance_tags.items():
            filters['tag:' + key] = value
    if module.params.get('id'):
        filters['client-token'] = module.params['id']
    for res in ec2.get_all_instances(instance_ids, filters=filters):
        for inst in res.instances:
            warn_if_public_ip_assignment_changed(module, inst)
            changed = check_source_dest_attr(module, inst, ec2) or check_termination_protection(module, inst) or changed
            if inst.state != state:
                instance_dict_array.append(get_instance_info(inst))
                try:
                    inst.reboot()
                except EC2ResponseError as e:
                    module.fail_json(msg='Unable to change state for instance {0}, error: {1}'.format(inst.id, e))
                changed = True
    return (changed, instance_dict_array, instance_ids)

def check_termination_protection(module, inst):
    """
    Check the instance disableApiTermination attribute.

    module: Ansible module object
    inst: EC2 instance object

    returns: True if state changed None otherwise
    """
    termination_protection = module.params.get('termination_protection')
    if inst.get_attribute('disableApiTermination')['disableApiTermination'] != termination_protection and termination_protection is not None:
        inst.modify_attribute('disableApiTermination', termination_protection)
        return True

def check_source_dest_attr(module, inst, ec2):
    """
    Check the instance sourceDestCheck attribute.

    module: Ansible module object
    inst: EC2 instance object

    returns: True if state changed None otherwise
    """
    source_dest_check = module.params.get('source_dest_check')
    if source_dest_check is not None:
        try:
            if inst.vpc_id is not None and inst.get_attribute('sourceDestCheck')['sourceDestCheck'] != source_dest_check:
                inst.modify_attribute('sourceDestCheck', source_dest_check)
                return True
        except boto.exception.EC2ResponseError as exc:
            if exc.code == 'InvalidInstanceID':
                for interface in inst.interfaces:
                    if interface.source_dest_check != source_dest_check:
                        ec2.modify_network_interface_attribute(interface.id, 'sourceDestCheck', source_dest_check)
                        return True
            else:
                module.fail_json(msg='Failed to handle source_dest_check state for instance {0}, error: {1}'.format(inst.id, exc), exception=traceback.format_exc())

def warn_if_public_ip_assignment_changed(module, instance):
    assign_public_ip = module.params.get('assign_public_ip')
    public_dns_name = getattr(instance, 'public_dns_name', None)
    if (assign_public_ip or public_dns_name) and (not public_dns_name or assign_public_ip is False):
        module.warn('Unable to modify public ip assignment to {0} for instance {1}. Whether or not to assign a public IP is determined during instance creation.'.format(assign_public_ip, instance.id))

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(key_name=dict(aliases=['keypair']), id=dict(), group=dict(type='list', aliases=['groups']), group_id=dict(type='list'), zone=dict(aliases=['aws_zone', 'ec2_zone']), instance_type=dict(aliases=['type']), spot_price=dict(), spot_type=dict(default='one-time', choices=['one-time', 'persistent']), spot_launch_group=dict(), image=dict(), kernel=dict(), count=dict(type='int', default='1'), monitoring=dict(type='bool', default=False), ramdisk=dict(), wait=dict(type='bool', default=False), wait_timeout=dict(type='int', default=300), spot_wait_timeout=dict(type='int', default=600), placement_group=dict(), user_data=dict(), instance_tags=dict(type='dict'), vpc_subnet_id=dict(), assign_public_ip=dict(type='bool'), private_ip=dict(), instance_profile_name=dict(), instance_ids=dict(type='list', aliases=['instance_id']), source_dest_check=dict(type='bool', default=None), termination_protection=dict(type='bool', default=None), state=dict(default='present', choices=['present', 'absent', 'running', 'restarted', 'stopped']), instance_initiated_shutdown_behavior=dict(default='stop', choices=['stop', 'terminate']), exact_count=dict(type='int', default=None), count_tag=dict(type='raw'), volumes=dict(type='list'), ebs_optimized=dict(type='bool', default=False), tenancy=dict(default='default', choices=['default', 'dedicated']), network_interfaces=dict(type='list', aliases=['network_interface'])))
    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=[['exact_count', 'count'], ['exact_count', 'state'], ['exact_count', 'instance_ids'], ['network_interfaces', 'assign_public_ip'], ['network_interfaces', 'group'], ['network_interfaces', 'group_id'], ['network_interfaces', 'private_ip'], ['network_interfaces', 'vpc_subnet_id']])
    if module.params.get('group') and module.params.get('group_id'):
        module.deprecate(msg='Support for passing both group and group_id has been deprecated. Currently group_id is ignored, in future passing both will result in an error', version='2.14', collection_name='ansible.builtin')
    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')
    try:
        (region, ec2_url, aws_connect_kwargs) = get_aws_connection_info(module)
        if module.params.get('region') or not module.params.get('ec2_url'):
            ec2 = ec2_connect(module)
        elif module.params.get('ec2_url'):
            ec2 = connect_ec2_endpoint(ec2_url, **aws_connect_kwargs)
        if 'region' not in aws_connect_kwargs:
            aws_connect_kwargs['region'] = ec2.region
        vpc = connect_vpc(**aws_connect_kwargs)
    except boto.exception.NoAuthHandlerFound as e:
        module.fail_json(msg='Failed to get connection: %s' % e.message, exception=traceback.format_exc())
    tagged_instances = []
    state = module.params['state']
    if state == 'absent':
        instance_ids = module.params['instance_ids']
        if not instance_ids:
            module.fail_json(msg='instance_ids list is required for absent state')
        (changed, instance_dict_array, new_instance_ids) = terminate_instances(module, ec2, instance_ids)
    elif state in ('running', 'stopped'):
        instance_ids = module.params.get('instance_ids')
        instance_tags = module.params.get('instance_tags')
        if not (isinstance(instance_ids, list) or isinstance(instance_tags, dict)):
            module.fail_json(msg='running list needs to be a list of instances or set of tags to run: %s' % instance_ids)
        (changed, instance_dict_array, new_instance_ids) = startstop_instances(module, ec2, instance_ids, state, instance_tags)
    elif state in 'restarted':
        instance_ids = module.params.get('instance_ids')
        instance_tags = module.params.get('instance_tags')
        if not (isinstance(instance_ids, list) or isinstance(instance_tags, dict)):
            module.fail_json(msg='running list needs to be a list of instances or set of tags to run: %s' % instance_ids)
        (changed, instance_dict_array, new_instance_ids) = restart_instances(module, ec2, instance_ids, state, instance_tags)
    elif state == 'present':
        if not module.params.get('image'):
            module.fail_json(msg='image parameter is required for new instance')
        if module.params.get('exact_count') is None:
            (instance_dict_array, new_instance_ids, changed) = create_instances(module, ec2, vpc)
        else:
            (tagged_instances, instance_dict_array, new_instance_ids, changed) = enforce_count(module, ec2, vpc)
    if new_instance_ids:
        new_instance_ids.sort()
    if instance_dict_array:
        instance_dict_array.sort(key=lambda x: x['id'])
    if tagged_instances:
        tagged_instances.sort(key=lambda x: x['id'])
    module.exit_json(changed=changed, instance_ids=new_instance_ids, instances=instance_dict_array, tagged_instances=tagged_instances)
if __name__ == '__main__':
    main()