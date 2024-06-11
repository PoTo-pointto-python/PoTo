from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: cs_service_offering\ndescription:\n  - Create and delete service offerings for guest and system VMs.\n  - Update display_text of existing service offering.\nshort_description: Manages service offerings on Apache CloudStack based clouds.\nversion_added: '2.5'\nauthor: René Moser (@resmo)\noptions:\n  disk_bytes_read_rate:\n    description:\n      - Bytes read rate of the disk offering.\n    type: int\n    aliases: [ bytes_read_rate ]\n  disk_bytes_write_rate:\n    description:\n      - Bytes write rate of the disk offering.\n    type: int\n    aliases: [ bytes_write_rate ]\n  cpu_number:\n    description:\n      - The number of CPUs of the service offering.\n    type: int\n  cpu_speed:\n    description:\n      - The CPU speed of the service offering in MHz.\n    type: int\n  limit_cpu_usage:\n    description:\n      - Restrict the CPU usage to committed service offering.\n    type: bool\n  deployment_planner:\n    description:\n      - The deployment planner heuristics used to deploy a VM of this offering.\n      - If not set, the value of global config I(vm.deployment.planner) is used.\n    type: str\n  display_text:\n    description:\n      - Display text of the service offering.\n      - If not set, I(name) will be used as I(display_text) while creating.\n    type: str\n  domain:\n    description:\n      - Domain the service offering is related to.\n      - Public for all domains and subdomains if not set.\n    type: str\n  host_tags:\n    description:\n      - The host tags for this service offering.\n    type: list\n    aliases:\n      - host_tag\n  hypervisor_snapshot_reserve:\n    description:\n      - Hypervisor snapshot reserve space as a percent of a volume.\n      - Only for managed storage using Xen or VMware.\n    type: int\n  is_iops_customized:\n    description:\n      - Whether compute offering iops is custom or not.\n    type: bool\n    aliases: [ disk_iops_customized ]\n  disk_iops_read_rate:\n    description:\n      - IO requests read rate of the disk offering.\n    type: int\n  disk_iops_write_rate:\n    description:\n      - IO requests write rate of the disk offering.\n    type: int\n  disk_iops_max:\n    description:\n      - Max. iops of the compute offering.\n    type: int\n  disk_iops_min:\n    description:\n      - Min. iops of the compute offering.\n    type: int\n  is_system:\n    description:\n      - Whether it is a system VM offering or not.\n    type: bool\n    default: no\n  is_volatile:\n    description:\n      - Whether the virtual machine needs to be volatile or not.\n      - Every reboot of VM the root disk is detached then destroyed and a fresh root disk is created and attached to VM.\n    type: bool\n  memory:\n    description:\n      - The total memory of the service offering in MB.\n    type: int\n  name:\n    description:\n      - Name of the service offering.\n    type: str\n    required: true\n  network_rate:\n    description:\n      - Data transfer rate in Mb/s allowed.\n      - Supported only for non-system offering and system offerings having I(system_vm_type=domainrouter).\n    type: int\n  offer_ha:\n    description:\n      - Whether HA is set for the service offering.\n    type: bool\n    default: no\n  provisioning_type:\n    description:\n      - Provisioning type used to create volumes.\n    type: str\n    choices:\n      - thin\n      - sparse\n      - fat\n  service_offering_details:\n    description:\n      - Details for planner, used to store specific parameters.\n      - A list of dictionaries having keys C(key) and C(value).\n    type: list\n  state:\n    description:\n      - State of the service offering.\n    type: str\n    choices:\n      - present\n      - absent\n    default: present\n  storage_type:\n    description:\n      - The storage type of the service offering.\n    type: str\n    choices:\n      - local\n      - shared\n  system_vm_type:\n    description:\n      - The system VM type.\n      - Required if I(is_system=yes).\n    type: str\n    choices:\n      - domainrouter\n      - consoleproxy\n      - secondarystoragevm\n  storage_tags:\n    description:\n      - The storage tags for this service offering.\n    type: list\n    aliases:\n      - storage_tag\n  is_customized:\n    description:\n      - Whether the offering is customizable or not.\n    type: bool\n    version_added: '2.8'\nextends_documentation_fragment: cloudstack\n"
EXAMPLES = '\n- name: Create a non-volatile compute service offering with local storage\n  cs_service_offering:\n    name: Micro\n    display_text: Micro 512mb 1cpu\n    cpu_number: 1\n    cpu_speed: 2198\n    memory: 512\n    host_tags: eco\n    storage_type: local\n  delegate_to: localhost\n\n- name: Create a volatile compute service offering with shared storage\n  cs_service_offering:\n    name: Tiny\n    display_text: Tiny 1gb 1cpu\n    cpu_number: 1\n    cpu_speed: 2198\n    memory: 1024\n    storage_type: shared\n    is_volatile: yes\n    host_tags: eco\n    storage_tags: eco\n  delegate_to: localhost\n\n- name: Create or update a volatile compute service offering with shared storage\n  cs_service_offering:\n    name: Tiny\n    display_text: Tiny 1gb 1cpu\n    cpu_number: 1\n    cpu_speed: 2198\n    memory: 1024\n    storage_type: shared\n    is_volatile: yes\n    host_tags: eco\n    storage_tags: eco\n  delegate_to: localhost\n\n- name: Create or update a custom compute service offering\n  cs_service_offering:\n    name: custom\n    display_text: custom compute offer\n    is_customized: yes\n    storage_type: shared\n    host_tags: eco\n    storage_tags: eco\n  delegate_to: localhost\n\n- name: Remove a compute service offering\n  cs_service_offering:\n    name: Tiny\n    state: absent\n  delegate_to: localhost\n\n- name: Create or update a system offering for the console proxy\n  cs_service_offering:\n    name: System Offering for Console Proxy 2GB\n    display_text: System Offering for Console Proxy 2GB RAM\n    is_system: yes\n    system_vm_type: consoleproxy\n    cpu_number: 1\n    cpu_speed: 2198\n    memory: 2048\n    storage_type: shared\n    storage_tags: perf\n  delegate_to: localhost\n\n- name: Remove a system offering\n  cs_service_offering:\n    name: System Offering for Console Proxy 2GB\n    is_system: yes\n    state: absent\n  delegate_to: localhost\n'
RETURN = '\n---\nid:\n  description: UUID of the service offering\n  returned: success\n  type: str\n  sample: a6f7a5fc-43f8-11e5-a151-feff819cdc9f\ncpu_number:\n  description: Number of CPUs in the service offering\n  returned: success\n  type: int\n  sample: 4\ncpu_speed:\n  description: Speed of CPUs in MHz in the service offering\n  returned: success\n  type: int\n  sample: 2198\ndisk_iops_max:\n  description: Max iops of the disk offering\n  returned: success\n  type: int\n  sample: 1000\ndisk_iops_min:\n  description: Min iops of the disk offering\n  returned: success\n  type: int\n  sample: 500\ndisk_bytes_read_rate:\n  description: Bytes read rate of the service offering\n  returned: success\n  type: int\n  sample: 1000\ndisk_bytes_write_rate:\n  description: Bytes write rate of the service offering\n  returned: success\n  type: int\n  sample: 1000\ndisk_iops_read_rate:\n  description: IO requests per second read rate of the service offering\n  returned: success\n  type: int\n  sample: 1000\ndisk_iops_write_rate:\n  description: IO requests per second write rate of the service offering\n  returned: success\n  type: int\n  sample: 1000\ncreated:\n  description: Date the offering was created\n  returned: success\n  type: str\n  sample: 2017-11-19T10:48:59+0000\ndisplay_text:\n  description: Display text of the offering\n  returned: success\n  type: str\n  sample: Micro 512mb 1cpu\ndomain:\n  description: Domain the offering is into\n  returned: success\n  type: str\n  sample: ROOT\nhost_tags:\n  description: List of host tags\n  returned: success\n  type: list\n  sample: [ \'eco\' ]\nstorage_tags:\n  description: List of storage tags\n  returned: success\n  type: list\n  sample: [ \'eco\' ]\nis_system:\n  description: Whether the offering is for system VMs or not\n  returned: success\n  type: bool\n  sample: false\nis_iops_customized:\n  description: Whether the offering uses custom IOPS or not\n  returned: success\n  type: bool\n  sample: false\nis_volatile:\n  description: Whether the offering is volatile or not\n  returned: success\n  type: bool\n  sample: false\nlimit_cpu_usage:\n  description: Whether the CPU usage is restricted to committed service offering\n  returned: success\n  type: bool\n  sample: false\nmemory:\n  description: Memory of the system offering\n  returned: success\n  type: int\n  sample: 512\nname:\n  description: Name of the system offering\n  returned: success\n  type: str\n  sample: Micro\noffer_ha:\n  description: Whether HA support is enabled in the offering or not\n  returned: success\n  type: bool\n  sample: false\nprovisioning_type:\n  description: Provisioning type used to create volumes\n  returned: success\n  type: str\n  sample: thin\nstorage_type:\n  description: Storage type used to create volumes\n  returned: success\n  type: str\n  sample: shared\nsystem_vm_type:\n  description: System VM type of this offering\n  returned: success\n  type: str\n  sample: consoleproxy\nservice_offering_details:\n  description: Additioanl service offering details\n  returned: success\n  type: dict\n  sample: "{\'vgpuType\': \'GRID K180Q\',\'pciDevice\':\'Group of NVIDIA Corporation GK107GL [GRID K1] GPUs\'}"\nnetwork_rate:\n  description: Data transfer rate in megabits per second allowed\n  returned: success\n  type: int\n  sample: 1000\nis_customized:\n  description: Whether the offering is customizable or not\n  returned: success\n  type: bool\n  sample: false\n  version_added: \'2.8\'\n'
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cloudstack import AnsibleCloudStack, cs_argument_spec, cs_required_together

class AnsibleCloudStackServiceOffering(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackServiceOffering, self).__init__(module)
        self.returns = {'cpunumber': 'cpu_number', 'cpuspeed': 'cpu_speed', 'deploymentplanner': 'deployment_planner', 'diskBytesReadRate': 'disk_bytes_read_rate', 'diskBytesWriteRate': 'disk_bytes_write_rate', 'diskIopsReadRate': 'disk_iops_read_rate', 'diskIopsWriteRate': 'disk_iops_write_rate', 'maxiops': 'disk_iops_max', 'miniops': 'disk_iops_min', 'hypervisorsnapshotreserve': 'hypervisor_snapshot_reserve', 'iscustomized': 'is_customized', 'iscustomizediops': 'is_iops_customized', 'issystem': 'is_system', 'isvolatile': 'is_volatile', 'limitcpuuse': 'limit_cpu_usage', 'memory': 'memory', 'networkrate': 'network_rate', 'offerha': 'offer_ha', 'provisioningtype': 'provisioning_type', 'serviceofferingdetails': 'service_offering_details', 'storagetype': 'storage_type', 'systemvmtype': 'system_vm_type', 'tags': 'storage_tags'}

    def get_service_offering(self):
        args = {'name': self.module.params.get('name'), 'domainid': self.get_domain(key='id'), 'issystem': self.module.params.get('is_system'), 'systemvmtype': self.module.params.get('system_vm_type')}
        service_offerings = self.query_api('listServiceOfferings', **args)
        if service_offerings:
            return service_offerings['serviceoffering'][0]

    def present_service_offering(self):
        service_offering = self.get_service_offering()
        if not service_offering:
            service_offering = self._create_offering(service_offering)
        else:
            service_offering = self._update_offering(service_offering)
        return service_offering

    def absent_service_offering(self):
        service_offering = self.get_service_offering()
        if service_offering:
            self.result['changed'] = True
            if not self.module.check_mode:
                args = {'id': service_offering['id']}
                self.query_api('deleteServiceOffering', **args)
        return service_offering

    def _create_offering(self, service_offering):
        self.result['changed'] = True
        system_vm_type = self.module.params.get('system_vm_type')
        is_system = self.module.params.get('is_system')
        required_params = []
        if is_system and (not system_vm_type):
            required_params.append('system_vm_type')
        self.module.fail_on_missing_params(required_params=required_params)
        args = {'name': self.module.params.get('name'), 'displaytext': self.get_or_fallback('display_text', 'name'), 'bytesreadrate': self.module.params.get('disk_bytes_read_rate'), 'byteswriterate': self.module.params.get('disk_bytes_write_rate'), 'cpunumber': self.module.params.get('cpu_number'), 'cpuspeed': self.module.params.get('cpu_speed'), 'customizediops': self.module.params.get('is_iops_customized'), 'deploymentplanner': self.module.params.get('deployment_planner'), 'domainid': self.get_domain(key='id'), 'hosttags': self.module.params.get('host_tags'), 'hypervisorsnapshotreserve': self.module.params.get('hypervisor_snapshot_reserve'), 'iopsreadrate': self.module.params.get('disk_iops_read_rate'), 'iopswriterate': self.module.params.get('disk_iops_write_rate'), 'maxiops': self.module.params.get('disk_iops_max'), 'miniops': self.module.params.get('disk_iops_min'), 'issystem': is_system, 'isvolatile': self.module.params.get('is_volatile'), 'memory': self.module.params.get('memory'), 'networkrate': self.module.params.get('network_rate'), 'offerha': self.module.params.get('offer_ha'), 'provisioningtype': self.module.params.get('provisioning_type'), 'serviceofferingdetails': self.module.params.get('service_offering_details'), 'storagetype': self.module.params.get('storage_type'), 'systemvmtype': system_vm_type, 'tags': self.module.params.get('storage_tags'), 'limitcpuuse': self.module.params.get('limit_cpu_usage'), 'customized': self.module.params.get('is_customized')}
        if not self.module.check_mode:
            res = self.query_api('createServiceOffering', **args)
            service_offering = res['serviceoffering']
        return service_offering

    def _update_offering(self, service_offering):
        args = {'id': service_offering['id'], 'name': self.module.params.get('name'), 'displaytext': self.get_or_fallback('display_text', 'name')}
        if self.has_changed(args, service_offering):
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('updateServiceOffering', **args)
                service_offering = res['serviceoffering']
        return service_offering

    def get_result(self, service_offering):
        super(AnsibleCloudStackServiceOffering, self).get_result(service_offering)
        if service_offering:
            if 'hosttags' in service_offering:
                self.result['host_tags'] = service_offering['hosttags'].split(',') or [service_offering['hosttags']]
            if 'tags' in service_offering:
                self.result['storage_tags'] = service_offering['tags'].split(',') or [service_offering['tags']]
            if 'tags' in self.result:
                del self.result['tags']
        return self.result

def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(name=dict(required=True), display_text=dict(), cpu_number=dict(type='int'), cpu_speed=dict(type='int'), limit_cpu_usage=dict(type='bool'), deployment_planner=dict(), domain=dict(), host_tags=dict(type='list', aliases=['host_tag']), hypervisor_snapshot_reserve=dict(type='int'), disk_bytes_read_rate=dict(type='int', aliases=['bytes_read_rate']), disk_bytes_write_rate=dict(type='int', aliases=['bytes_write_rate']), disk_iops_read_rate=dict(type='int'), disk_iops_write_rate=dict(type='int'), disk_iops_max=dict(type='int'), disk_iops_min=dict(type='int'), is_system=dict(type='bool', default=False), is_volatile=dict(type='bool'), is_iops_customized=dict(type='bool', aliases=['disk_iops_customized']), memory=dict(type='int'), network_rate=dict(type='int'), offer_ha=dict(type='bool'), provisioning_type=dict(choices=['thin', 'sparse', 'fat']), service_offering_details=dict(type='list'), storage_type=dict(choices=['local', 'shared']), system_vm_type=dict(choices=['domainrouter', 'consoleproxy', 'secondarystoragevm']), storage_tags=dict(type='list', aliases=['storage_tag']), state=dict(choices=['present', 'absent'], default='present'), is_customized=dict(type='bool')))
    module = AnsibleModule(argument_spec=argument_spec, required_together=cs_required_together(), supports_check_mode=True)
    acs_so = AnsibleCloudStackServiceOffering(module)
    state = module.params.get('state')
    if state == 'absent':
        service_offering = acs_so.absent_service_offering()
    else:
        service_offering = acs_so.present_service_offering()
    result = acs_so.get_result(service_offering)
    module.exit_json(**result)
if __name__ == '__main__':
    main()

def test_AnsibleCloudStackServiceOffering_get_service_offering():
    ret = AnsibleCloudStackServiceOffering().get_service_offering()

def test_AnsibleCloudStackServiceOffering_present_service_offering():
    ret = AnsibleCloudStackServiceOffering().present_service_offering()

def test_AnsibleCloudStackServiceOffering_absent_service_offering():
    ret = AnsibleCloudStackServiceOffering().absent_service_offering()

def test_AnsibleCloudStackServiceOffering__create_offering():
    ret = AnsibleCloudStackServiceOffering()._create_offering()

def test_AnsibleCloudStackServiceOffering__update_offering():
    ret = AnsibleCloudStackServiceOffering()._update_offering()

def test_AnsibleCloudStackServiceOffering_get_result():
    ret = AnsibleCloudStackServiceOffering().get_result()